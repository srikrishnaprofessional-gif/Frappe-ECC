import copy
import unittest
from pathlib import Path

from frappe_ecc import frappe_rules as R
from frappe_ecc import spec

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def base_spec(**doctype_overrides):
	dt = {
		"name": "Library Book",
		"fields": [{"fieldname": "title", "fieldtype": "Data", "reqd": 1}],
	}
	dt.update(doctype_overrides)
	return {
		"spec_version": 1,
		"app": {"name": "library", "publisher": "Acme", "email": "dev@acme.test"},
		"modules": [{"name": "Library", "doctypes": [dt]}],
	}


def check(raw):
	return spec.validate(spec.normalise(raw))


class TestExamples(unittest.TestCase):
	def test_examples_are_valid(self):
		files = sorted(EXAMPLES.glob("*.json"))
		self.assertTrue(files)
		for path in files:
			with self.subTest(path.name):
				result = check(spec.load_spec(path))
				self.assertEqual(result.errors, [])


class TestNormalise(unittest.TestCase):
	def test_aliases_and_defaults(self):
		raw = base_spec(child_table=True)
		raw["modules"][0]["doctypes"][0]["fields"].append({"label": "Pages Read", "type": "Int", "required": "yes"})
		dt = spec.normalise(raw)["modules"][0]["doctypes"][0]
		self.assertEqual(dt["istable"], 1)
		self.assertEqual(dt["permissions"], [])
		f = dt["fields"][1]
		self.assertEqual((f["fieldname"], f["fieldtype"], f["reqd"]), ("pages_read", "Int", 1))

	def test_default_permission_matches_doctype_kind(self):
		dt = spec.normalise(base_spec(submittable=True))["modules"][0]["doctypes"][0]
		perm = dt["permissions"][0]
		self.assertEqual(perm["role"], "System Manager")
		self.assertEqual((perm["submit"], perm["cancel"], perm["amend"]), (1, 1, 1))
		single = spec.normalise(base_spec(single=True))["modules"][0]["doctypes"][0]["permissions"][0]
		self.assertNotIn("report", single)
		self.assertNotIn("delete", single)
		self.assertEqual(check(base_spec(single=True)).errors, [])
		self.assertEqual(check(base_spec(submittable=True)).errors, [])

	def test_select_list_and_check_default(self):
		raw = base_spec()
		raw["modules"][0]["doctypes"][0]["fields"] += [
			{"fieldname": "status", "fieldtype": "Select", "options": ["Open", "Closed"], "default": "Open"},
			{"fieldname": "is_available", "fieldtype": "Check", "default": True},
		]
		fields = spec.normalise(raw)["modules"][0]["doctypes"][0]["fields"]
		self.assertEqual(fields[1]["options"], "Open\nClosed")
		self.assertEqual(fields[2]["default"], "1")
		self.assertEqual(check(raw).errors, [])


class TestValidationErrors(unittest.TestCase):
	def assertError(self, raw, fragment):
		errors = check(raw).errors
		self.assertTrue(any(fragment in e for e in errors), f"no error containing {fragment!r} in {errors}")

	def add_field(self, raw, **field):
		raw["modules"][0]["doctypes"][0]["fields"].append(field)
		return raw

	def test_app_name_and_metadata(self):
		raw = base_spec()
		raw["app"]["name"] = "Library App"
		self.assertError(raw, "snake_case")
		raw["app"]["name"] = "frappe"
		self.assertError(raw, "reserved")
		raw = base_spec()
		raw["app"]["email"] = "nope"
		self.assertError(raw, "valid email")

	def test_unknown_keys_are_reported(self):
		raw = base_spec(colour="red")
		self.assertError(raw, "unknown key 'colour'")
		raw = self.add_field(base_spec(), fieldname="x", fieldtype="Data", mandatroy=1)
		self.assertError(raw, "unknown key 'mandatroy'")

	def test_doctype_name_rules(self):
		self.assertError(base_spec(name="1st Book"), "must start with a letter")
		self.assertError(base_spec(name="B" * 62), "longer than 61")
		self.assertError(base_spec(name="User"), "Frappe already has")

	def test_reserved_and_conflicting_fieldnames(self):
		for name in ("name", "owner", "parent", "save", "meta", "flags", "docstatus"):
			with self.subTest(name):
				self.assertError(self.add_field(base_spec(), fieldname=name, fieldtype="Data"), "reserved")

	def test_duplicate_fieldname(self):
		self.assertError(self.add_field(base_spec(), fieldname="title", fieldtype="Data"), "more than once")

	def test_link_and_table_options(self):
		self.assertError(self.add_field(base_spec(), fieldname="author", fieldtype="Link"), "need 'options'")
		self.assertError(
			self.add_field(base_spec(), fieldname="rows", fieldtype="Table", options="Missing Child"),
			"not defined in this spec",
		)
		raw = self.add_field(base_spec(), fieldname="rows", fieldtype="Table", options="Library Book")
		self.assertError(raw, "must be a child table")

	def test_link_to_unknown_doctype_is_a_warning(self):
		raw = self.add_field(base_spec(), fieldname="author", fieldtype="Link", options="Author Somewhere")
		result = check(raw)
		self.assertEqual(result.errors, [])
		self.assertTrue(any("Author Somewhere" in w for w in result.warnings))

	def test_select_rules(self):
		self.assertError(self.add_field(base_spec(), fieldname="s", fieldtype="Select"), "need 'options'")
		self.assertError(
			self.add_field(base_spec(), fieldname="s", fieldtype="Select", options="A\nB", default="C"),
			"not one of the options",
		)

	def test_field_property_rules(self):
		cases = [
			(dict(fieldname="n", fieldtype="Small Text", unique=1), "cannot be unique"),
			(dict(fieldname="n", fieldtype="Text", search_index=1), "cannot be indexed"),
			(dict(fieldname="n", fieldtype="Section Break", reqd=1), "cannot be mandatory"),
			(dict(fieldname="n", fieldtype="Data", reqd=1, hidden=1), "needs a default"),
			(dict(fieldname="n", fieldtype="Float", precision=9), "between 1 and 6"),
			(dict(fieldname="n", fieldtype="Data", precision=2), "precision only applies"),
			(dict(fieldname="n", fieldtype="Data", options="Colour"), "Data options must be"),
			(dict(fieldname="n", fieldtype="Check", default="2"), "Check default must be 0 or 1"),
			(dict(fieldname="n", fieldtype="Wibble"), "unknown fieldtype"),
			(dict(fieldname="Bad Name", fieldtype="Data"), "snake_case"),
			(dict(fieldname="n", fieldtype="Section Break", in_list_view=1), "cannot be shown in list view"),
		]
		for field, fragment in cases:
			with self.subTest(fragment):
				self.assertError(self.add_field(base_spec(), **field), fragment)

	def test_dynamic_link_needs_pointer(self):
		raw = self.add_field(base_spec(), fieldname="ref", fieldtype="Dynamic Link", options="ref_type")
		self.assertError(raw, "Dynamic Link options")
		raw = self.add_field(base_spec(), fieldname="ref_type", fieldtype="Link", options="DocType")
		self.add_field(raw, fieldname="ref", fieldtype="Dynamic Link", options="ref_type")
		self.assertEqual(check(raw).errors, [])

	def test_fetch_from(self):
		self.assertError(self.add_field(base_spec(), fieldname="x", fieldtype="Data", fetch_from="nope.title"), "fetch_from")

	def test_naming(self):
		self.assertError(base_spec(autoname="field:missing"), "missing field 'missing'")
		self.assertError(base_spec(autoname="format:BK-{missing}-{###}"), "missing field 'missing'")
		self.assertError(base_spec(autoname="naming_series:"), "Select field named naming_series")
		self.assertError(base_spec(autoname="whatever"), "unsupported autoname")
		self.assertEqual(check(base_spec(autoname="format:BK-{YYYY}-{####}")).errors, [])
		self.assertEqual(check(base_spec(autoname="BK-.#####")).errors, [])

	def test_doctype_kind_conflicts(self):
		self.assertError(base_spec(istable=1, issingle=1), "both a child table and a single")
		self.assertError(base_spec(istable=1, is_submittable=1), "child tables cannot be submittable")
		self.assertError(base_spec(issingle=1, is_submittable=1), "single DocTypes cannot be submittable")

	def test_title_search_sort(self):
		self.assertError(base_spec(title_field="nope"), "title_field 'nope'")
		self.assertError(base_spec(search_fields=["nope"]), "search_fields entry 'nope'")
		self.assertError(base_spec(sort_field="nope"), "sort_field 'nope'")

	def test_permission_rules(self):
		def perms(*rows, **dt):
			return base_spec(permissions=list(rows), **dt)

		self.assertError(perms({"role": "Librarian", "print": 1}), "grant at least one of")
		self.assertError(perms({"role": "Librarian", "read": 1, "submit": 1}), "only apply to submittable")
		self.assertError(perms({"role": "Librarian", "read": 1, "write": 1, "cancel": 1}, submittable=1), "cancel needs submit")
		self.assertError(perms({"role": "Librarian", "read": 1, "submit": 1}, submittable=1), "need write")
		self.assertError(perms({"role": "Librarian", "read": 1, "write": 1, "submit": 1, "amend": 1}, submittable=1), "amend needs create")
		self.assertError(perms({"role": "Librarian", "read": 1, "import": 1, "create": 1}), "allow_import")
		self.assertError(perms({"role": "Librarian", "read": 1, "permlevel": 1}), "none at permlevel 0")
		self.assertError(perms({"role": "Librarian", "read": 1}, {"role": "Librarian", "read": 1}), "duplicate rule")
		self.assertError(perms({"role": "Librarian", "read": 1, "report": 1}, issingle=1), "cannot grant report")
		self.assertError(base_spec(istable=1, permissions=[{"role": "X", "read": 1}]), "take their permissions")

	def test_nested_child_table_rejected(self):
		raw = base_spec()
		raw["modules"][0]["doctypes"] += [
			{"name": "Book Row", "istable": 1, "fields": [{"fieldname": "inner", "fieldtype": "Table", "options": "Inner Row"}]},
			{"name": "Inner Row", "istable": 1, "fields": [{"fieldname": "x", "fieldtype": "Data"}]},
		]
		self.assertError(raw, "table inside a child table")

	def test_module_rules(self):
		raw = base_spec()
		raw["modules"][0]["name"] = "Core"
		self.assertError(raw, "Frappe already has a module")
		raw = base_spec()
		raw["modules"].append(copy.deepcopy(raw["modules"][0]))
		self.assertError(raw, "more than once")


class TestRulesMatchInstalledFrappe(unittest.TestCase):
	"""Runs only where Frappe is importable (e.g. a bench's env/bin/python)."""

	@classmethod
	def setUpClass(cls):
		try:
			import frappe.model as model
		except ImportError:
			raise unittest.SkipTest("frappe is not importable")
		cls.model = model

	def test_fieldtypes(self):
		self.assertEqual(set(self.model.data_fieldtypes), set(R.DATA_FIELDTYPES))
		self.assertEqual(set(self.model.no_value_fields), set(R.NO_VALUE_FIELDTYPES))
		self.assertEqual(set(self.model.table_fields), set(R.TABLE_FIELDTYPES))
		self.assertEqual(set(self.model.data_field_options), set(R.DATA_FIELD_OPTIONS))

	def test_reserved_fields(self):
		self.assertEqual(set(self.model.default_fields), set(R.DEFAULT_FIELDS))
		self.assertEqual(set(self.model.child_table_fields), set(R.CHILD_TABLE_FIELDS))
		self.assertEqual(set(self.model.optional_fields), set(R.OPTIONAL_FIELDS))

	def test_document_attributes_are_reserved(self):
		from frappe.model.document import Document

		public = {n for n in dir(Document) if not n.startswith("_")}
		missing = public - R.RESERVED_FIELDNAMES
		# Attributes Frappe added after this list was written are fine to allow only if they are
		# not callable; report them so the list can be updated.
		callables = {n for n in missing if callable(getattr(Document, n, None))}
		self.assertFalse(callables, f"add to DOCUMENT_ATTRIBUTES: {sorted(callables)}")

	def test_scrub(self):
		import frappe

		for text in ("Sales Order", "Clinic-Patient Item", "ABC"):
			self.assertEqual(frappe.scrub(text), R.scrub(text))


if __name__ == "__main__":
	unittest.main()
