import ast
import json
import tempfile
import unittest
from pathlib import Path

from frappe_ecc import generator, spec

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "clinic_management.json"


def load_example():
	normalised = spec.normalise(spec.load_spec(EXAMPLE))
	assert spec.validate(normalised).ok
	return normalised


class TestGenerateApp(unittest.TestCase):
	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.dest = Path(self.tmp.name)
		self.spec = load_example()
		self.files = generator.generate_app(self.spec, self.dest, with_ci=True)
		self.root = self.dest / "clinic_management"
		self.pkg = self.root / "clinic_management"

	def tearDown(self):
		self.tmp.cleanup()

	def test_app_layout_matches_bench_new_app(self):
		for rel in (
			"pyproject.toml",
			"license.txt",
			"README.md",
			".gitignore",
			"clinic_management/__init__.py",
			"clinic_management/hooks.py",
			"clinic_management/modules.txt",
			"clinic_management/patches.txt",
			"clinic_management/config/__init__.py",
			"clinic_management/public/.gitkeep",
			"clinic_management/clinic/__init__.py",
			"clinic_management/clinic/.frappe",
			"clinic_management/clinic/doctype/__init__.py",
			".github/workflows/ci.yml",
		):
			self.assertTrue((self.root / rel).exists(), rel)
		self.assertEqual((self.pkg / "modules.txt").read_text().strip(), "Clinic")

	def test_doctype_folders_use_frappe_scrub(self):
		base = self.pkg / "clinic" / "doctype"
		for folder in ("clinic_patient", "clinic_doctor", "clinic_appointment", "clinic_prescription_item", "clinic_settings"):
			self.assertTrue((base / folder / f"{folder}.json").exists(), folder)
			self.assertTrue((base / folder / f"{folder}.py").exists(), folder)
			self.assertTrue((base / folder / "__init__.py").exists(), folder)
		# Child tables get no form script and no test, like `bench new-doctype`.
		self.assertFalse((base / "clinic_prescription_item" / "clinic_prescription_item.js").exists())
		self.assertFalse((base / "clinic_prescription_item" / "test_clinic_prescription_item.py").exists())

	def test_every_python_file_parses(self):
		for path in self.root.rglob("*.py"):
			with self.subTest(str(path.relative_to(self.root))):
				ast.parse(path.read_text())

	def test_controller_class_names(self):
		src = (self.pkg / "clinic" / "doctype" / "clinic_prescription_item" / "clinic_prescription_item.py").read_text()
		self.assertIn("class ClinicPrescriptionItem(Document):", src)

	def test_doctype_json(self):
		path = self.pkg / "clinic" / "doctype" / "clinic_appointment" / "clinic_appointment.json"
		doc = json.loads(path.read_text())
		self.assertEqual(doc["doctype"], "DocType")
		self.assertEqual(doc["name"], "Clinic Appointment")
		self.assertEqual(doc["module"], "Clinic")
		self.assertEqual(doc["is_submittable"], 1)
		self.assertEqual(doc["field_order"], [f["fieldname"] for f in doc["fields"]])
		amended = [f for f in doc["fields"] if f["fieldname"] == "amended_from"]
		self.assertEqual(amended[0]["options"], "Clinic Appointment")
		status = next(f for f in doc["fields"] if f["fieldname"] == "status")
		self.assertEqual(status["options"], "Scheduled\nCompleted\nNo Show")
		self.assertEqual(doc["naming_rule"], "Expression")

	def test_child_and_single_flags(self):
		child = json.loads((self.pkg / "clinic/doctype/clinic_prescription_item/clinic_prescription_item.json").read_text())
		self.assertEqual(child["istable"], 1)
		self.assertEqual(child["permissions"], [])
		single = json.loads((self.pkg / "clinic/doctype/clinic_settings/clinic_settings.json").read_text())
		self.assertEqual(single["issingle"], 1)

	def test_check_default_kept(self):
		doc = json.loads((self.pkg / "clinic/doctype/clinic_doctor/clinic_doctor.json").read_text())
		is_active = next(f for f in doc["fields"] if f["fieldname"] == "is_active")
		self.assertEqual(is_active["default"], "1")

	def test_hooks_escape_quotes(self):
		self.spec["app"]["description"] = 'Says "hi"'
		tmp = Path(self.tmp.name) / "again"
		generator.generate_app(self.spec, tmp)
		src = (tmp / "clinic_management" / "clinic_management" / "hooks.py").read_text()
		tree = ast.parse(src)
		values = {n.targets[0].id: n.value.value for n in tree.body if isinstance(n, ast.Assign)}
		self.assertEqual(values["app_description"], 'Says "hi"')

	def test_refuses_to_overwrite(self):
		with self.assertRaises(generator.GenerateError):
			generator.generate_app(self.spec, self.dest)

	def test_add_doctypes_to_existing_app(self):
		extra = spec.normalise(
			{
				"app": dict(self.spec["app"]),
				"modules": [
					{
						"name": "Billing",
						"doctypes": [{"name": "Clinic Invoice", "fields": [{"fieldname": "amount", "fieldtype": "Currency", "reqd": 1}]}],
					}
				],
			}
		)
		self.assertTrue(spec.validate(extra).ok)
		written = generator.add_doctypes(extra, self.root)
		self.assertIn(self.pkg / "billing" / "doctype" / "clinic_invoice" / "clinic_invoice.json", written)
		self.assertEqual((self.pkg / "modules.txt").read_text().split(), ["Clinic", "Billing"])
		with self.assertRaises(generator.GenerateError):
			generator.add_doctypes(extra, self.root)


if __name__ == "__main__":
	unittest.main()
