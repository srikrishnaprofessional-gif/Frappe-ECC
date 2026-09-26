"""Load, normalise and validate a Frappe ECC app spec.

A spec describes an app (name, publisher, modules) and the DocTypes it contains.
Validation mirrors the checks Frappe runs when it saves a DocType, so a spec that
passes here produces DocType JSON that Frappe accepts on `bench migrate`.
See docs/SPEC_REFERENCE.md for the format.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import cache
from importlib import resources
from pathlib import Path
from typing import Any

from frappe_ecc import frappe_rules as R

SPEC_VERSION = 1

APP_KEYS = {"name", "title", "publisher", "email", "description", "license", "required_apps"}
MODULE_KEYS = {"name", "doctypes"}
DOCTYPE_KEYS = {
	"name",
	"description",
	"istable",
	"issingle",
	"is_submittable",
	"autoname",
	"title_field",
	"search_fields",
	"sort_field",
	"sort_order",
	"track_changes",
	"quick_entry",
	"allow_rename",
	"allow_import",
	"editable_grid",
	"show_title_field_in_link",
	"fields",
	"permissions",
}
# Friendlier spellings accepted in specs.
DOCTYPE_ALIASES = {
	"child_table": "istable",
	"is_child": "istable",
	"single": "issingle",
	"is_single": "issingle",
	"submittable": "is_submittable",
	"naming": "autoname",
}
FIELD_KEYS = {
	"fieldname",
	"label",
	"fieldtype",
	"options",
	"reqd",
	"unique",
	"default",
	"description",
	"in_list_view",
	"in_standard_filter",
	"in_global_search",
	"in_preview",
	"bold",
	"read_only",
	"hidden",
	"depends_on",
	"mandatory_depends_on",
	"read_only_depends_on",
	"fetch_from",
	"fetch_if_empty",
	"precision",
	"length",
	"search_index",
	"allow_on_submit",
	"no_copy",
	"print_hide",
	"report_hide",
	"permlevel",
	"non_negative",
	"collapsible",
	"collapsible_depends_on",
	"set_only_once",
	"translatable",
	"ignore_user_permissions",
	"remember_last_selected_value",
	"link_filters",
	"columns",
	"width",
}
FIELD_ALIASES = {"type": "fieldtype", "required": "reqd", "mandatory": "reqd"}
BOOL_FIELD_KEYS = {
	"reqd",
	"unique",
	"in_list_view",
	"in_standard_filter",
	"in_global_search",
	"in_preview",
	"bold",
	"read_only",
	"hidden",
	"search_index",
	"allow_on_submit",
	"no_copy",
	"print_hide",
	"report_hide",
	"non_negative",
	"collapsible",
	"set_only_once",
	"translatable",
	"ignore_user_permissions",
	"remember_last_selected_value",
	"fetch_if_empty",
}
BOOL_DOCTYPE_KEYS = {
	"istable",
	"issingle",
	"is_submittable",
	"track_changes",
	"quick_entry",
	"allow_rename",
	"allow_import",
	"editable_grid",
	"show_title_field_in_link",
}
PERMISSION_KEYS = {"role", "permlevel", "if_owner", *R.PERMISSION_RIGHTS}
RESERVED_APP_NAMES = {"frappe", "erpnext", "hrms", "payments", "bench", "test", "tests", "app", "apps"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
FORMAT_FIELD_PATTERN = re.compile(r"\{([^{}]+)\}")


class SpecError(Exception):
	"""The spec file cannot be read or is not a mapping."""


@dataclass
class ValidationResult:
	errors: list[str] = field(default_factory=list)
	warnings: list[str] = field(default_factory=list)

	@property
	def ok(self) -> bool:
		return not self.errors


@cache
def standard_names() -> dict[str, dict[str, list[str]]]:
	"""DocType and module names shipped by frappe, erpnext, hrms and payments."""
	text = resources.files("frappe_ecc").joinpath("data/standard_names.json").read_text()
	return json.loads(text)


def load_spec(path: str | Path) -> dict[str, Any]:
	path = Path(path)
	try:
		text = path.read_text(encoding="utf-8")
	except OSError as e:
		raise SpecError(f"cannot read {path}: {e.strerror}") from e

	if path.suffix.lower() in (".yaml", ".yml"):
		try:
			import yaml
		except ImportError as e:
			raise SpecError(
				"YAML specs need PyYAML (pip install pyyaml). Frappe benches already have it; "
				"or write the spec as .json."
			) from e
		try:
			data = yaml.safe_load(text)
		except yaml.YAMLError as e:
			raise SpecError(f"{path} is not valid YAML: {e}") from e
	else:
		try:
			data = json.loads(text)
		except json.JSONDecodeError as e:
			raise SpecError(f"{path} is not valid JSON: {e}") from e

	if not isinstance(data, dict):
		raise SpecError(f"{path}: the top level must be a mapping with 'app' and 'modules'")
	return data


def _as_int_flag(value: Any) -> int:
	if isinstance(value, str):
		return 1 if value.strip().lower() in ("1", "true", "yes", "y") else 0
	return 1 if value else 0


def normalise(spec: dict[str, Any]) -> dict[str, Any]:
	"""Return a copy with aliases resolved, defaults filled and flags as 0/1.

	Unknown keys are kept so validate() can report them.
	"""
	app = dict(spec.get("app") or {})
	if app.get("name"):
		app["name"] = str(app["name"]).strip()
	app.setdefault("title", R.unscrub(app.get("name", "")))
	app.setdefault("publisher", "")
	app.setdefault("email", "")
	app.setdefault("description", app["title"])
	app.setdefault("license", "mit")
	app.setdefault("required_apps", [])

	modules = []
	for module in spec.get("modules") or []:
		if not isinstance(module, dict):
			modules.append(module)
			continue
		module = dict(module)
		module["doctypes"] = [
			_normalise_doctype(dt) if isinstance(dt, dict) else dt for dt in module.get("doctypes") or []
		]
		modules.append(module)

	# A spec with no modules gets one named after the app, which is what `bench new-app` does.
	out = {k: v for k, v in spec.items() if k not in ("app", "modules")}
	out["spec_version"] = spec.get("spec_version", SPEC_VERSION)
	out["app"] = app
	out["modules"] = modules
	return out


def _normalise_doctype(dt: dict[str, Any]) -> dict[str, Any]:
	dt = {DOCTYPE_ALIASES.get(k, k): v for k, v in dt.items()}
	if isinstance(dt.get("name"), str):
		dt["name"] = dt["name"].strip()
	for key in BOOL_DOCTYPE_KEYS:
		if key in dt:
			dt[key] = _as_int_flag(dt[key])
	for key in ("istable", "issingle", "is_submittable"):
		dt.setdefault(key, 0)
	dt.setdefault("track_changes", 0 if dt["istable"] else 1)
	if dt["istable"]:
		dt.setdefault("editable_grid", 1)
	if isinstance(dt.get("search_fields"), str):
		dt["search_fields"] = [s.strip() for s in dt["search_fields"].split(",") if s.strip()]

	fields = []
	for f in dt.get("fields") or []:
		fields.append(_normalise_field(f) if isinstance(f, dict) else f)
	dt["fields"] = fields

	if "permissions" not in dt:
		dt["permissions"] = [] if dt["istable"] else [_default_permission(dt)]
	else:
		dt["permissions"] = [
			_normalise_permission(p) if isinstance(p, dict) else p for p in dt["permissions"] or []
		]
	return dt


def _normalise_field(f: dict[str, Any]) -> dict[str, Any]:
	f = {FIELD_ALIASES.get(k, k): v for k, v in f.items()}
	f.setdefault("fieldtype", "Data")
	if not f.get("fieldname") and isinstance(f.get("label"), str):
		f["fieldname"] = re.sub(r"[^a-z0-9_]", "", R.scrub(f["label"].strip()))
	if f.get("fieldname") and not f.get("label") and f["fieldtype"] not in R.LAYOUT_FIELDTYPES:
		f["label"] = R.unscrub(str(f["fieldname"]))
	if isinstance(f.get("options"), list):
		f["options"] = "\n".join(str(o) for o in f["options"])
	for key in BOOL_FIELD_KEYS:
		if key in f:
			f[key] = _as_int_flag(f[key])
	if f["fieldtype"] == "Check":
		if "default" not in f or f["default"] in (None, ""):
			f["default"] = "0"
		elif f["default"] in (True, False, 0, 1) or str(f["default"]).strip().lower() in ("0", "1", "true", "false"):
			f["default"] = str(_as_int_flag(f["default"]))
		else:
			f["default"] = str(f["default"])  # left as-is so validate() reports it
	elif "default" in f and f["default"] is not None and not isinstance(f["default"], str):
		f["default"] = str(f["default"])
	return f


def _normalise_permission(p: dict[str, Any]) -> dict[str, Any]:
	p = dict(p)
	for key in (*R.PERMISSION_RIGHTS, "if_owner"):
		if key in p:
			p[key] = _as_int_flag(p[key])
	if "permlevel" in p:
		try:
			p["permlevel"] = int(p["permlevel"])
		except (TypeError, ValueError):
			pass
	return p


def _default_permission(dt: dict[str, Any]) -> dict[str, Any]:
	perm = {"role": "System Manager"}
	rights = ["read", "write", "create", "print", "email", "share"]
	if not dt.get("issingle"):
		rights += ["delete", "report", "export"]
	if dt.get("is_submittable"):
		rights += ["submit", "cancel", "amend"]
	perm.update({r: 1 for r in rights})
	return perm


def iter_doctypes(spec: dict[str, Any]):
	"""Yield (module_name, doctype) for every DocType in a normalised spec."""
	for module in spec["modules"]:
		for dt in module["doctypes"]:
			yield module["name"], dt


def validate(spec: dict[str, Any], target_version: int | None = None) -> ValidationResult:
	"""Validate a normalised spec. `target_version` is the Frappe major version, if known."""
	result = ValidationResult()
	err = result.errors.append
	warn = result.warnings.append

	unknown_top = set(spec) - {"spec_version", "app", "modules"}
	if unknown_top:
		err(f"unknown top-level keys: {', '.join(sorted(unknown_top))}")
	if spec.get("spec_version") != SPEC_VERSION:
		err(f"spec_version must be {SPEC_VERSION}")

	_validate_app(spec["app"], err, warn)

	if not spec["modules"]:
		err("modules: at least one module with at least one DocType is required")
		return result

	names = standard_names()
	frappe_doctypes = set(names["frappe"]["doctypes"])
	other_doctypes = {
		dt: app for app in ("erpnext", "hrms", "payments") for dt in names[app]["doctypes"]
	}
	frappe_modules = set(names["frappe"]["modules"]) | {"Core"}
	other_modules = {m: app for app in ("erpnext", "hrms", "payments") for m in names[app]["modules"]}

	seen_modules: dict[str, str] = {}
	spec_doctypes: dict[str, dict[str, Any]] = {}
	for mi, module in enumerate(spec["modules"]):
		where = f"modules[{mi}]"
		if not isinstance(module, dict):
			err(f"{where}: must be a mapping")
			continue
		for key in sorted(set(module) - MODULE_KEYS):
			err(f"{where}: unknown key '{key}'")
		mname = module.get("name")
		if not isinstance(mname, str) or not R.DOCTYPE_NAME_PATTERN.match(mname):
			err(f"{where}.name: '{mname}' must start with a letter and use letters, digits, spaces, '-' or '_'")
			continue
		where = f"module '{mname}'"
		scrubbed = R.scrub(mname)
		if scrubbed in seen_modules:
			err(f"{where}: folder name '{scrubbed}' clashes with module '{seen_modules[scrubbed]}'")
		seen_modules[scrubbed] = mname
		if mname in frappe_modules:
			err(f"{where}: Frappe already has a module with this name; module names are global to a site")
		elif mname in other_modules:
			warn(
				f"{where}: {other_modules[mname]} has a module with this name; installing both on one site will fail"
			)
		if not module["doctypes"]:
			err(f"{where}: add at least one DocType")
		for di, dt in enumerate(module["doctypes"]):
			if not isinstance(dt, dict):
				err(f"{where}.doctypes[{di}]: must be a mapping")
				continue
			dname = dt.get("name")
			if not isinstance(dname, str) or not dname:
				err(f"{where}.doctypes[{di}]: 'name' is required")
				continue
			if dname in spec_doctypes:
				err(f"DocType '{dname}' is defined more than once")
				continue
			spec_doctypes[dname] = dt
			if dname in frappe_doctypes:
				err(f"DocType '{dname}': Frappe already has a DocType with this name")
			elif dname in other_doctypes:
				warn(
					f"DocType '{dname}': {other_doctypes[dname]} has a DocType with this name; "
					"installing both on one site will fail"
				)

	scrubbed_doctypes: dict[str, str] = {}
	for dname, dt in spec_doctypes.items():
		s = R.scrub(dname)
		if s in scrubbed_doctypes:
			err(f"DocType '{dname}': folder name '{s}' clashes with DocType '{scrubbed_doctypes[s]}'")
		scrubbed_doctypes[s] = dname
		_validate_doctype(dt, spec_doctypes, frappe_doctypes | set(other_doctypes), err, warn)

	return result


def _validate_app(app: dict[str, Any], err, warn) -> None:
	for key in sorted(set(app) - APP_KEYS):
		err(f"app: unknown key '{key}'")
	name = app.get("name")
	if not name:
		err("app.name is required (snake_case, e.g. clinic_management)")
	elif not R.APP_NAME_PATTERN.match(name):
		err(f"app.name '{name}' must be snake_case: lowercase letters, digits and '_', starting with a letter")
	elif name in RESERVED_APP_NAMES:
		err(f"app.name '{name}' is reserved")
	title = app.get("title") or ""
	if not R.DOCTYPE_NAME_PATTERN.match(title):
		err(f"app.title '{title}' must start with a letter and use letters, digits, spaces, '-' or '_'")
	if not app.get("publisher"):
		err("app.publisher is required")
	email = app.get("email")
	if not email:
		err("app.email is required")
	elif not EMAIL_PATTERN.match(email):
		err(f"app.email '{email}' is not a valid email address")
	if not isinstance(app.get("required_apps"), list):
		err("app.required_apps must be a list, e.g. [erpnext]")


def _validate_doctype(dt, spec_doctypes, known_doctypes, err, warn) -> None:
	name = dt["name"]
	where = f"DocType '{name}'"
	for key in sorted(set(dt) - DOCTYPE_KEYS):
		err(f"{where}: unknown key '{key}'")

	if len(name) > R.MAX_DOCTYPE_NAME_LENGTH:
		err(f"{where}: name is longer than {R.MAX_DOCTYPE_NAME_LENGTH} characters")
	if not R.DOCTYPE_NAME_PATTERN.match(name):
		err(f"{where}: name must start with a letter and use letters, digits, spaces, '-' or '_'")

	istable, issingle, submittable = dt["istable"], dt["issingle"], dt["is_submittable"]
	if istable and issingle:
		err(f"{where}: a DocType cannot be both a child table and a single")
	if istable and submittable:
		err(f"{where}: child tables cannot be submittable; make the parent submittable instead")
	if issingle and submittable:
		err(f"{where}: single DocTypes cannot be submittable")

	fields = dt["fields"]
	if not isinstance(fields, list) or not fields:
		err(f"{where}: add at least one field")
		return

	by_name: dict[str, dict[str, Any]] = {}
	data_field_count = 0
	for i, f in enumerate(fields):
		if not isinstance(f, dict):
			err(f"{where}.fields[{i}]: must be a mapping")
			continue
		fname = f.get("fieldname")
		fwhere = f"{where}.{fname or f'fields[{i}]'}"
		for key in sorted(set(f) - FIELD_KEYS):
			err(f"{fwhere}: unknown key '{key}'")
		if not fname:
			err(f"{fwhere}: fieldname (or label) is required")
			continue
		if fname in by_name:
			err(f"{fwhere}: fieldname appears more than once")
			continue
		by_name[fname] = f
		_validate_field(f, fwhere, dt, spec_doctypes, known_doctypes, err, warn)
		if f.get("fieldtype") not in R.NO_VALUE_FIELDTYPES:
			data_field_count += 1

	if not data_field_count:
		err(f"{where}: needs at least one field that stores a value")

	for f in by_name.values():
		if f.get("fieldtype") == "Dynamic Link":
			pointer = by_name.get(f.get("options") or "")
			if not pointer or not (
				(pointer.get("fieldtype") == "Link" and pointer.get("options") == "DocType")
				or pointer.get("fieldtype") == "Select"
			):
				err(
					f"{where}.{f['fieldname']}: Dynamic Link options must name a field in this DocType "
					"that is a Link to 'DocType' (or a Select of DocType names)"
				)
		fetch_from = f.get("fetch_from")
		if fetch_from:
			link_field = str(fetch_from).split(".", 1)[0]
			target = by_name.get(link_field)
			if "." not in str(fetch_from) or not target or target.get("fieldtype") not in ("Link", "Dynamic Link"):
				err(
					f"{where}.{f['fieldname']}: fetch_from must be '<link_field>.<fieldname>' "
					"where <link_field> is a Link field in this DocType"
				)
			elif target.get("options") in spec_doctypes:
				src = str(fetch_from).split(".", 1)[1]
				target_fields = {x.get("fieldname") for x in spec_doctypes[target["options"]]["fields"]}
				if src not in target_fields | R.DEFAULT_FIELDS:
					err(f"{where}.{f['fieldname']}: '{target['options']}' has no field '{src}' to fetch")

	_validate_naming(dt, by_name, where, err, warn)

	title_field = dt.get("title_field")
	if title_field:
		tf = by_name.get(title_field)
		if not tf:
			err(f"{where}: title_field '{title_field}' is not a field of this DocType")
		elif tf.get("fieldtype") not in ("Data", "Read Only", "Text", "Small Text", "Link", "Select", "Autocomplete"):
			err(f"{where}: title_field '{title_field}' must be a text-like field, not {tf.get('fieldtype')}")

	for sf in dt.get("search_fields") or []:
		f = by_name.get(sf)
		if not f:
			err(f"{where}: search_fields entry '{sf}' is not a field of this DocType")
		elif f.get("fieldtype") in R.NO_VALUE_FIELDTYPES or f.get("fieldtype") in R.NOT_INDEXABLE_FIELDTYPES:
			err(f"{where}: search_fields entry '{sf}' cannot be a {f.get('fieldtype')} field")

	sort_field = dt.get("sort_field")
	if sort_field and sort_field not in by_name and sort_field not in R.DEFAULT_FIELDS:
		err(f"{where}: sort_field '{sort_field}' is not a field of this DocType")
	if dt.get("sort_order") and dt["sort_order"] not in ("ASC", "DESC"):
		err(f"{where}: sort_order must be ASC or DESC")

	_validate_permissions(dt, where, err, warn)


def _validate_field(f, fwhere, dt, spec_doctypes, known_doctypes, err, warn) -> None:
	fname = f["fieldname"]
	ftype = f.get("fieldtype")
	options = f.get("options")

	if not isinstance(fname, str) or not R.FIELDNAME_PATTERN.match(fname):
		err(f"{fwhere}: fieldname must be snake_case (lowercase letters, digits, '_'), starting with a letter")
		return
	if len(fname) > R.MAX_FIELDNAME_LENGTH:
		err(f"{fwhere}: fieldname is longer than {R.MAX_FIELDNAME_LENGTH} characters")
	if fname in R.RESERVED_FIELDNAMES:
		err(f"{fwhere}: '{fname}' is reserved by Frappe; choose another fieldname")
	if fname == "amended_from" and not dt["is_submittable"]:
		err(f"{fwhere}: amended_from is only for submittable DocTypes, and Frappe adds it for you")
	if ftype not in R.ALL_FIELDTYPES:
		err(f"{fwhere}: unknown fieldtype '{ftype}'")
		return

	if ftype in ("Link", *R.TABLE_FIELDTYPES) and not options:
		err(f"{fwhere}: {ftype} fields need 'options' set to the target DocType")
	if ftype == "Link" and options and options not in spec_doctypes and options not in known_doctypes:
		warn(f"{fwhere}: links to '{options}', which is not in this spec; it must exist on the target site")
	if ftype == "Link" and options in spec_doctypes and spec_doctypes[options]["istable"]:
		err(f"{fwhere}: cannot link to child table '{options}'")
	if ftype in R.TABLE_FIELDTYPES and options:
		if dt["istable"]:
			err(f"{fwhere}: Frappe's form UI cannot edit a table inside a child table; link to a separate DocType")
		if options in spec_doctypes:
			if not spec_doctypes[options]["istable"]:
				err(f"{fwhere}: '{options}' must be a child table (istable: 1) to be used in a {ftype} field")
		elif options not in known_doctypes:
			err(f"{fwhere}: child table '{options}' is not defined in this spec")
		if ftype == "Table MultiSelect" and options in spec_doctypes:
			child_links = [
				x for x in spec_doctypes[options]["fields"] if isinstance(x, dict) and x.get("fieldtype") == "Link"
			]
			if not child_links:
				err(f"{fwhere}: Table MultiSelect child '{options}' needs a Link field")
	if ftype == "Select":
		opts = [o for o in str(options or "").split("\n")]
		if not any(o.strip() for o in opts):
			err(f"{fwhere}: Select fields need 'options' (a list, or values separated by newlines)")
		default = f.get("default")
		if default not in (None, "") and default not in opts:
			err(f"{fwhere}: default '{default}' is not one of the options")
	if ftype == "Data" and options and options not in R.DATA_FIELD_OPTIONS:
		err(f"{fwhere}: Data options must be one of {', '.join(sorted(R.DATA_FIELD_OPTIONS))}")
	if ftype == "Check" and str(f.get("default", "0")) not in ("0", "1"):
		err(f"{fwhere}: Check default must be 0 or 1")

	if f.get("reqd") and ftype in R.NO_VALUE_FIELDTYPES and ftype not in R.TABLE_FIELDTYPES:
		err(f"{fwhere}: {ftype} fields cannot be mandatory")
	if f.get("reqd") and f.get("hidden") and f.get("default") in (None, ""):
		err(f"{fwhere}: a hidden mandatory field needs a default")
	if f.get("unique") and ftype not in R.UNIQUE_ALLOWED_FIELDTYPES:
		err(f"{fwhere}: {ftype} fields cannot be unique (only {', '.join(sorted(R.UNIQUE_ALLOWED_FIELDTYPES))})")
	if f.get("unique") and dt["issingle"]:
		warn(f"{fwhere}: 'unique' is ignored on single DocTypes")
	if f.get("search_index") and (ftype in R.NOT_INDEXABLE_FIELDTYPES or ftype in R.NO_VALUE_FIELDTYPES):
		err(f"{fwhere}: {ftype} fields cannot be indexed")
	not_allowed = R.NOT_ALLOWED_IN_GRID_VIEW if dt["istable"] else R.NOT_ALLOWED_IN_LIST_VIEW
	if f.get("in_list_view") and ftype in not_allowed:
		err(f"{fwhere}: {ftype} fields cannot be shown in {'grid' if dt['istable'] else 'list'} view")
	if f.get("in_global_search") and ftype in R.NO_VALUE_FIELDTYPES:
		err(f"{fwhere}: {ftype} fields cannot be in global search")
	if f.get("precision") not in (None, ""):
		try:
			precision = int(f["precision"])
		except (TypeError, ValueError):
			precision = -1
		if ftype not in R.PRECISION_FIELDTYPES:
			err(f"{fwhere}: precision only applies to {', '.join(sorted(R.PRECISION_FIELDTYPES))}")
		elif not 1 <= precision <= 6:
			err(f"{fwhere}: precision must be between 1 and 6")
		else:
			f["precision"] = str(precision)
	if f.get("allow_on_submit") and not dt["is_submittable"] and not dt["istable"]:
		warn(f"{fwhere}: allow_on_submit has no effect on a DocType that is not submittable")
	permlevel = f.get("permlevel", 0)
	if not isinstance(permlevel, int) or not 0 <= permlevel <= 9:
		err(f"{fwhere}: permlevel must be a whole number from 0 to 9")


def _validate_naming(dt, by_name, where, err, warn) -> None:
	autoname = dt.get("autoname")
	if autoname in (None, ""):
		return
	if not isinstance(autoname, str):
		err(f"{where}: autoname must be a string")
		return
	if dt["istable"]:
		warn(f"{where}: child tables are always named by hash; autoname is ignored")
		return
	if autoname.startswith("field:"):
		fieldname = autoname[len("field:") :].strip()
		f = by_name.get(fieldname)
		if not f:
			err(f"{where}: autoname '{autoname}' refers to missing field '{fieldname}'")
		else:
			if not f.get("reqd"):
				err(f"{where}: field '{fieldname}' is used for naming, so set reqd: 1")
			if not f.get("unique"):
				warn(f"{where}: field '{fieldname}' names the document; consider unique: 1 for a clearer error")
	elif autoname.startswith("naming_series:"):
		f = by_name.get("naming_series")
		if not f or f.get("fieldtype") != "Select" or not f.get("options"):
			err(
				f"{where}: 'naming_series:' needs a Select field named naming_series whose options "
				"are the series, e.g. 'PAT-.YYYY.-'"
			)
	elif autoname.startswith("format:"):
		for ref in FORMAT_FIELD_PATTERN.findall(autoname):
			if ref.startswith("#") or ref in ("YY", "YYYY", "MM", "DD", "MON", "FY", "timestamp", "WW", "JJJ"):
				continue
			if ref not in by_name:
				err(f"{where}: autoname '{autoname}' refers to missing field '{ref}'")
		if "{#" not in autoname:
			warn(f"{where}: autoname '{autoname}' has no counter like {{####}}; names may collide")
	elif autoname in ("hash", "autoincrement", "prompt", "UUID"):
		pass
	elif autoname.lower() == "uuid":
		err(f"{where}: write autoname as 'UUID' (Frappe v16+ only)")
	elif re.match(r"^[A-Za-z0-9_-]+$", autoname) and autoname in by_name:
		warn(f"{where}: use 'field:{autoname}' rather than the bare fieldname")
	elif "#" in autoname and "." in autoname:
		pass  # old-style series like PAT-.#####
	else:
		err(
			f"{where}: unsupported autoname '{autoname}'. Use field:<fieldname>, naming_series:, "
			"format:PREFIX-{####}, hash, autoincrement, prompt or a series like PAT-.#####"
		)
	if autoname == "UUID":
		warn(f"{where}: UUID naming needs Frappe v16 or later")


def _validate_permissions(dt, where, err, warn) -> None:
	perms = dt["permissions"]
	if dt["istable"]:
		if perms:
			err(f"{where}: child tables take their permissions from the parent; remove 'permissions'")
		return
	if not perms:
		err(f"{where}: add at least one permission rule, or omit 'permissions' for System Manager access")
		return
	seen = set()
	levels_by_role: dict[str, set[int]] = {}
	for i, p in enumerate(perms):
		pwhere = f"{where}.permissions[{i}]"
		if not isinstance(p, dict):
			err(f"{pwhere}: must be a mapping")
			continue
		for key in sorted(set(p) - PERMISSION_KEYS):
			err(f"{pwhere}: unknown key '{key}'")
		role = p.get("role")
		if not role or not isinstance(role, str):
			err(f"{pwhere}: 'role' is required")
			continue
		if role == "Guest":
			warn(f"{pwhere}: Guest access makes records readable without logging in")
		level = p.get("permlevel", 0)
		if not isinstance(level, int) or not 0 <= level <= 9:
			err(f"{pwhere}: permlevel must be a whole number from 0 to 9")
			continue
		key = (role, level, p.get("if_owner", 0))
		if key in seen:
			err(f"{pwhere}: duplicate rule for role '{role}' at permlevel {level}")
		seen.add(key)
		levels_by_role.setdefault(role, set()).add(level)
		rights = [r for r in R.PERMISSION_RIGHTS if p.get(r)]
		if not any(p.get(r) for r in ("select", "read", "write", "submit", "cancel", "create")):
			err(f"{pwhere}: grant at least one of select, read, write, create, submit or cancel")
		if not dt["is_submittable"]:
			bad = [r for r in rights if r in R.SUBMIT_RIGHTS]
			if bad:
				err(f"{pwhere}: {', '.join(bad)} only apply to submittable DocTypes")
		# frappe.core.doctype.doctype.doctype.validate_permissions.check_permission_dependency
		if p.get("cancel") and not p.get("submit"):
			err(f"{pwhere}: cancel needs submit")
		if any(p.get(r) for r in R.SUBMIT_RIGHTS) and not p.get("write"):
			err(f"{pwhere}: submit, cancel and amend need write")
		if p.get("amend") and not p.get("create"):
			err(f"{pwhere}: amend needs create")
		if p.get("import"):
			if not p.get("create"):
				err(f"{pwhere}: import needs create")
			if not dt.get("allow_import"):
				err(f"{pwhere}: import needs allow_import: 1 on the DocType")
		if dt["issingle"]:
			bad = [r for r in ("report", "import", "export") if p.get(r)]
			if bad:
				err(f"{pwhere}: single DocTypes cannot grant {', '.join(bad)}")
		if level > 0 and role not in ("All", "Desk User"):
			bad = [r for r in ("create", "submit", "cancel", "amend") if p.get(r)]
			if bad:
				err(f"{pwhere}: {', '.join(bad)} do not apply above permlevel 0")
	for role, levels in levels_by_role.items():
		if role not in ("All", "Desk User") and 0 not in levels:
			err(f"{where}: role '{role}' has rules above permlevel 0 but none at permlevel 0")
