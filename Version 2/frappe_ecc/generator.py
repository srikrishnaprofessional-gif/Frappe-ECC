"""Write a Frappe app (or new DocTypes in an existing app) from a validated spec.

Output follows the layout `bench new-app` and `bench new-doctype` produce on
Frappe v15 and v16, so the app installs with `bench get-app` + `install-app` and
DocTypes sync on `bench migrate`.
"""

from __future__ import annotations

import datetime as _dt
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from frappe_ecc import __version__
from frappe_ecc import frappe_rules as R
from frappe_ecc.spec import iter_doctypes

# Field properties written to DocType JSON, in the order Frappe exports them (alphabetical).
_FIELD_EXPORT_KEYS = sorted(
	{
		"allow_on_submit",
		"bold",
		"collapsible",
		"collapsible_depends_on",
		"columns",
		"default",
		"depends_on",
		"description",
		"fetch_from",
		"fetch_if_empty",
		"fieldname",
		"fieldtype",
		"hidden",
		"ignore_user_permissions",
		"in_global_search",
		"in_list_view",
		"in_preview",
		"in_standard_filter",
		"label",
		"length",
		"link_filters",
		"mandatory_depends_on",
		"no_copy",
		"non_negative",
		"options",
		"permlevel",
		"precision",
		"print_hide",
		"read_only",
		"read_only_depends_on",
		"remember_last_selected_value",
		"report_hide",
		"reqd",
		"search_index",
		"set_only_once",
		"translatable",
		"unique",
		"width",
	}
)


class GenerateError(Exception):
	pass


def _now() -> str:
	return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def _write(path: Path, content: str, written: list[Path], overwrite: bool = False) -> None:
	if path.exists() and not overwrite:
		raise GenerateError(f"{path} already exists; refusing to overwrite it")
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(content, encoding="utf-8")
	written.append(path)


def _py_str(value: str) -> str:
	"""Quote a value for a double-quoted Python string literal."""
	return json.dumps(value, ensure_ascii=False)[1:-1]


def doctype_json(module: str, dt: dict[str, Any], timestamp: str) -> dict[str, Any]:
	fields = []
	for f in dt["fields"]:
		row = {k: f[k] for k in _FIELD_EXPORT_KEYS if k in f and f[k] not in (None, "", 0)}
		# Frappe keeps Check defaults of "0" in exports.
		if f.get("fieldtype") == "Check":
			row["default"] = f.get("default", "0")
		fields.append(row)

	if dt["is_submittable"] and not any(f["fieldname"] == "amended_from" for f in dt["fields"]):
		fields.append(
			{
				"fieldname": "amended_from",
				"fieldtype": "Link",
				"label": "Amended From",
				"no_copy": 1,
				"options": dt["name"],
				"print_hide": 1,
				"read_only": 1,
				"search_index": 1,
			}
		)

	permissions = []
	for p in dt["permissions"]:
		row = {"role": p["role"]}
		for right in R.PERMISSION_RIGHTS:
			if p.get(right):
				row[right] = 1
		if p.get("permlevel"):
			row["permlevel"] = p["permlevel"]
		if p.get("if_owner"):
			row["if_owner"] = 1
		permissions.append(dict(sorted(row.items())))

	doc: dict[str, Any] = {
		"actions": [],
		"creation": timestamp,
		"doctype": "DocType",
		"engine": "InnoDB",
		"field_order": [f["fieldname"] for f in fields],
		"fields": fields,
		"index_web_pages_for_search": 0 if dt["istable"] else 1,
		"links": [],
		"modified": timestamp,
		"modified_by": "Administrator",
		"module": module,
		"name": dt["name"],
		"owner": "Administrator",
		"permissions": permissions,
		"sort_field": dt.get("sort_field") or "modified",
		"sort_order": dt.get("sort_order") or "DESC",
		"states": [],
	}
	for key in ("istable", "issingle", "is_submittable", "track_changes", "quick_entry",
				"allow_rename", "allow_import", "editable_grid", "show_title_field_in_link"):
		if dt.get(key):
			doc[key] = 1
	if dt.get("description"):
		doc["description"] = dt["description"]
	autoname = dt.get("autoname")
	if autoname and not dt["istable"]:
		doc["autoname"] = autoname
		doc["naming_rule"] = _naming_rule(autoname)
	elif dt["istable"]:
		doc["autoname"] = "hash"
	if dt.get("title_field"):
		doc["title_field"] = dt["title_field"]
	if dt.get("search_fields"):
		doc["search_fields"] = ",".join(dt["search_fields"])
	return dict(sorted(doc.items()))


def _naming_rule(autoname: str) -> str:
	if autoname.startswith("field:"):
		return "By fieldname"
	if autoname.startswith("naming_series:"):
		return 'By "Naming Series" field'
	if autoname.startswith("format:"):
		return "Expression"
	if autoname == "hash":
		return "Random"
	if autoname == "autoincrement":
		return "Autoincrement"
	if autoname == "prompt":
		return "Set by user"
	if autoname == "UUID":
		return "UUID"
	return "Expression (old style)"


def controller_py(dt: dict[str, Any], publisher: str, year: int) -> str:
	return f"""# Copyright (c) {year}, {publisher} and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class {R.class_name(dt["name"])}(Document):
	pass
"""


def controller_js(dt: dict[str, Any], publisher: str, year: int) -> str:
	return f"""// Copyright (c) {year}, {publisher} and contributors
// For license information, please see license.txt

// frappe.ui.form.on("{dt["name"]}", {{
// 	refresh(frm) {{

// 	}},
// }});
"""


def controller_test(app_name: str, dt: dict[str, Any], publisher: str, year: int) -> str:
	name = dt["name"]
	cls = R.class_name(name)
	header = f"""# Copyright (c) {year}, {publisher} and Contributors
# See license.txt

import frappe

from {app_name}.factories import make_doc

try:
	from frappe.tests import IntegrationTestCase
except ImportError:  # Frappe v15
	from frappe.tests.utils import FrappeTestCase as IntegrationTestCase


class Test{cls}(IntegrationTestCase):
"""
	if dt["issingle"]:
		body = f"""	def test_settings_save_and_reload(self):
		doc = make_doc("{name}")
		doc.reload()
		self.assertEqual(doc.doctype, "{name}")
"""
	elif dt["is_submittable"]:
		body = f"""	def test_insert_submit_cancel(self):
		doc = make_doc("{name}")
		self.assertTrue(frappe.db.exists("{name}", doc.name))
		self.assertEqual(doc.docstatus, 0)

		doc.submit()
		self.assertEqual(frappe.db.get_value("{name}", doc.name, "docstatus"), 1)

		doc.cancel()
		self.assertEqual(frappe.db.get_value("{name}", doc.name, "docstatus"), 2)
"""
	else:
		body = f"""	def test_insert_and_read_back(self):
		doc = make_doc("{name}")
		self.assertTrue(frappe.db.exists("{name}", doc.name))

		saved = frappe.get_doc("{name}", doc.name)
		for fieldname in ({_mandatory_tuple(dt)}):
			self.assertEqual(saved.get(fieldname), doc.get(fieldname))
"""
	return header + body


# Types whose value reads back from the database unchanged. Time comes back as a
# timedelta, Password is masked, and JSON/Geolocation may be re-serialised.
_READ_BACK_TYPES = frozenset(
	{"Data", "Select", "Link", "Int", "Long Int", "Check", "Small Text", "Text", "Long Text",
	 "Float", "Currency", "Percent", "Date", "Phone", "Autocomplete", "Barcode", "Color"}
)


def _mandatory_tuple(dt: dict[str, Any]) -> str:
	names = [f["fieldname"] for f in dt["fields"] if f.get("reqd") and f.get("fieldtype") in _READ_BACK_TYPES]
	return "".join(f'"{n}", ' for n in names)


FACTORIES_PY = '''"""Test data factory generated by Frappe ECC.

make_doc(doctype, **values) inserts a document with every mandatory field filled,
creating linked records from this app on the way. Use it in tests:

	from {app_name}.factories import make_doc
	patient = make_doc("Patient", patient_name="Asha")
"""

import frappe
from frappe.utils import add_days, now_datetime, today

APP_NAME = "{app_name}"
_MAX_DEPTH = 4


def make_doc(doctype, submit=False, **values):
	"""Insert and return a {{doctype}} with mandatory fields filled. Singles are saved instead."""
	return _make(doctype, values, submit, depth=0)


def _make(doctype, values, submit, depth):
	meta = frappe.get_meta(doctype)
	if meta.issingle:
		doc = frappe.get_single(doctype)
		doc.update(values)
		_fill(doc, meta, depth)
		doc.save()
		return doc

	doc = frappe.new_doc(doctype)
	doc.update(values)
	if meta.autoname == "prompt" and not doc.name:
		doc.name = f"_Test {{doctype}} {{frappe.generate_hash(length=8)}}"
	_fill(doc, meta, depth)
	doc.insert()
	if submit:
		doc.submit()
	return doc


def _fill(doc, meta, depth):
	for df in meta.fields:
		if not df.reqd or df.fieldtype in ("Section Break", "Column Break", "Tab Break"):
			continue
		if df.fieldtype in ("Table", "Table MultiSelect"):
			if not doc.get(df.fieldname):
				child_meta = frappe.get_meta(df.options)
				row = doc.append(df.fieldname, {{}})
				_fill(row, child_meta, depth + 1)
			continue
		if doc.get(df.fieldname) not in (None, ""):
			continue
		doc.set(df.fieldname, _value_for(doc, meta, df, depth))


def _value_for(doc, meta, df, depth):
	unique = frappe.generate_hash(length=8)
	ft = df.fieldtype
	if ft == "Data":
		return {{
			"Email": f"test-{{unique}}@example.com",
			"Phone": "+919876543210",
			"URL": "https://example.com",
			"IBAN": "DE89370400440532013000",
		}}.get(df.options or "", f"_Test {{df.label}} {{unique}}")
	if ft in ("Small Text", "Text", "Long Text", "Text Editor", "Markdown Editor", "HTML Editor", "Code"):
		return f"_Test {{df.label}}"
	if ft in ("Autocomplete", "Barcode"):
		return unique
	if ft == "Read Only":
		return None
	if ft in ("Int", "Long Int"):
		return 1
	if ft in ("Float", "Currency"):
		return 100
	if ft == "Percent":
		return 10
	if ft == "Check":
		return 1
	if ft == "Rating":
		return 0.6
	if ft == "Date":
		return add_days(today(), 1)
	if ft == "Datetime":
		return now_datetime()
	if ft == "Time":
		return "10:00:00"
	if ft == "Duration":
		return 3600
	if ft == "Select":
		options = [o for o in (df.options or "").split("\\n") if o]
		return options[0] if options else None
	if ft == "Phone":
		return "+919876543210"
	if ft == "Color":
		return "#4F46E5"
	if ft == "JSON":
		return "{{}}"
	if ft == "Password":
		return frappe.generate_hash(length=16)
	if ft in ("Attach", "Attach Image", "Signature"):
		return "/files/_test.png"
	if ft == "Geolocation":
		return '{{"type": "FeatureCollection", "features": []}}'
	if ft == "Link":
		return _link_value(df.options, depth)
	if ft == "Dynamic Link":
		pointer = meta.get_field(df.options)
		target = doc.get(df.options)
		if not target:
			target = "User"
			if pointer and pointer.fieldtype == "Select":
				target = [o for o in (pointer.options or "").split("\\n") if o][0]
			doc.set(df.options, target)
		return _link_value(target, depth)
	return None


def _link_value(target, depth):
	"""Create a record when {{target}} belongs to this app, otherwise reuse an existing one."""
	if target == "User":
		return "Administrator"
	if target == "DocType":
		return "User"
	module = frappe.db.get_value("DocType", target, "module")
	app = frappe.db.get_value("Module Def", module, "app_name") if module else None
	if app == APP_NAME and depth < _MAX_DEPTH:
		return _make(target, {{}}, False, depth + 1).name
	existing = frappe.db.get_value(target, {{}}, "name")
	if existing:
		return existing
	raise frappe.ValidationError(
		f"make_doc needs a '{{target}}' record. Create one in your test's setUp, "
		f"or pass the field explicitly."
	)
'''


HOOKS_PY = '''app_name = "{app_name}"
app_title = "{app_title}"
app_publisher = "{app_publisher}"
app_description = "{app_description}"
app_email = "{app_email}"
app_license = "{app_license}"
{required_apps}
# Generated by Frappe ECC {ecc_version}. Hooks reference:
# https://docs.frappe.io/framework/user/en/python-api/hooks

# Document Events
# ---------------
# doc_events = {{
# 	"*": {{
# 		"on_update": "method",
# 	}}
# }}

# Scheduled Tasks
# ---------------
# scheduler_events = {{
# 	"daily": ["{app_name}.tasks.daily"],
# }}

# Permissions evaluated in scripted ways
# --------------------------------------
# permission_query_conditions = {{
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }}
# has_permission = {{
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }}

# Fixtures exported with `bench --site <site> export-fixtures`
# fixtures = []
'''

PYPROJECT = '''[project]
name = "{app_name}"
authors = [
    {{ name = "{app_publisher}", email = "{app_email}" }}
]
description = "{app_description}"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = [
    # "frappe~=15.0.0" # Installed and managed by bench.
]

[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[tool.ruff]
line-length = 110
target-version = "py310"

[tool.ruff.lint]
select = ["F", "E", "W", "I", "UP", "B"]
ignore = ["E101", "E402", "E501", "E741", "F401", "F403", "F405", "W191", "UP030", "UP031", "UP032", "B017"]
typing-modules = ["frappe.types.DF"]

[tool.ruff.format]
quote-style = "double"
indent-style = "tab"
'''

PATCHES_TXT = """[pre_model_sync]
# Patches added in this section will be executed before doctypes are migrated
# Read docs to understand patches: https://docs.frappe.io/framework/user/en/database-migrations

[post_model_sync]
# Patches added in this section will be executed after doctypes are migrated
"""

GITIGNORE = """.DS_Store
*.pyc
*.egg-info
*.swp
tags
node_modules
__pycache__
{app_name}/docs/current
{app_name}/public/dist
"""

EDITORCONFIG = """root = true

[*]
indent_style = tab
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{json,yml,yaml,md}]
indent_style = space
indent_size = 2
"""

README = """## {app_title}

{app_description}

Generated by [Frappe ECC](https://github.com/srikrishnaprofessional-gif/Frappe-ECC) {ecc_version} from `ecc.spec.json`.

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench --site <site> install-app {app_name}
bench --site <site> migrate
```

### DocTypes

{doctype_table}

### Tests

```bash
bench --site <site> set-config allow_tests true
bench --site <site> run-tests --app {app_name}
```

### License

{app_license}
"""

LICENSE_MIT = """MIT License

Copyright (c) {year} {publisher}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CI_WORKFLOW = """name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ci-${{{{ github.ref }}}}
  cancel-in-progress: true

jobs:
  tests:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - frappe-branch: version-15
            python: "3.11"
            node: 18
          - frappe-branch: version-16
            python: "3.14"
            node: 24
    name: Tests (${{{{ matrix.frappe-branch }}}})

    services:
      mariadb:
        image: mariadb:10.6
        env:
          MARIADB_ROOT_PASSWORD: root
        ports:
          - 3306:3306
        options: --health-cmd="mariadb-admin ping" --health-interval=5s --health-timeout=2s --health-retries=3
      redis:
        image: redis:alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python }}}}
      - uses: actions/setup-node@v4
        with:
          node-version: ${{{{ matrix.node }}}}
      - name: Install system packages
        run: sudo apt-get update && sudo apt-get install -y mariadb-client
      - name: Install bench
        run: pip install frappe-bench
      - name: Init bench
        run: bench init --skip-redis-config-generation --skip-assets --frappe-branch ${{{{ matrix.frappe-branch }}}} --python "$(which python)" ~/frappe-bench
      - name: Install app
        working-directory: /home/runner/frappe-bench
        run: |
          bench get-app {app_name} $GITHUB_WORKSPACE
          bench set-config -g redis_cache redis://localhost:6379
          bench set-config -g redis_queue redis://localhost:6379
          bench set-config -g redis_socketio redis://localhost:6379
          bench new-site --db-root-password root --admin-password admin test_site
          bench --site test_site install-app {app_name}
          bench --site test_site set-config allow_tests true
      - name: Run tests
        working-directory: /home/runner/frappe-bench
        run: bench --site test_site run-tests --app {app_name}
"""


def init_git(root: Path, publisher: str, email: str) -> bool:
	"""git init + first commit, as `bench new-app` does. bench get-app needs a git repo.

	Returns False when git is not installed. Uses the app's publisher as author only when the
	user has no git identity configured.
	"""
	if not shutil.which("git"):
		return False
	if (root / ".git").exists():
		return True
	identity: list[str] = []
	has_email = subprocess.run(["git", "config", "user.email"], cwd=root, capture_output=True, text=True).stdout.strip()
	if not has_email:
		identity = ["-c", f"user.name={publisher or 'Frappe ECC'}", "-c", f"user.email={email or 'ecc@localhost'}"]
	for args in (["init", "-q", "-b", "main"], ["add", "-A"], [*identity, "commit", "-q", "-m", "feat: initialize app (generated by Frappe ECC)"]):
		proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
		if proc.returncode != 0:
			raise GenerateError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
	return True


def generate_app(spec: dict[str, Any], dest: Path, *, with_ci: bool = False, force: bool = False) -> list[Path]:
	"""Create <dest>/<app_name>/ from a validated, normalised spec. Returns the files written."""
	app = spec["app"]
	app_name = app["name"]
	root = dest / app_name
	if root.exists() and any(root.iterdir()) and not force:
		raise GenerateError(f"{root} already exists and is not empty")

	written: list[Path] = []
	pkg = root / app_name
	year = _dt.date.today().year
	fmt = {
		"app_name": app_name,
		"app_title": _py_str(app["title"]),
		"app_publisher": _py_str(app["publisher"]),
		"app_description": _py_str(app["description"]),
		"app_email": _py_str(app["email"]),
		"app_license": _py_str(app["license"]),
		"ecc_version": __version__,
		"required_apps": (
			f"\nrequired_apps = {json.dumps(app['required_apps'])}\n" if app["required_apps"] else ""
		),
	}

	_write(root / "pyproject.toml", PYPROJECT.format(**fmt), written, force)
	_write(root / ".gitignore", GITIGNORE.format(app_name=app_name), written, force)
	_write(root / ".editorconfig", EDITORCONFIG, written, force)
	license_text = (
		LICENSE_MIT.format(year=year, publisher=app["publisher"])
		if app["license"].lower() == "mit"
		else f"{app['license']}\n\nCopyright (c) {year} {app['publisher']}\n"
	)
	_write(root / "license.txt", license_text, written, force)
	_write(root / "ecc.spec.json", json.dumps(spec, indent=2, ensure_ascii=False) + "\n", written, force)

	_write(pkg / "__init__.py", '__version__ = "0.0.1"\n', written, force)
	_write(pkg / "hooks.py", HOOKS_PY.format(**fmt), written, force)
	_write(pkg / "patches.txt", PATCHES_TXT, written, force)
	_write(pkg / "modules.txt", "\n".join(m["name"] for m in spec["modules"]) + "\n", written, force)
	_write(pkg / "factories.py", FACTORIES_PY.format(app_name=app_name), written, force)
	for init in ("config", "templates", "templates/pages", "patches"):
		_write(pkg / init / "__init__.py", "", written, force)
	for keep in ("public/.gitkeep", "www/.gitkeep", "templates/includes/.gitkeep"):
		_write(pkg / keep, "", written, force)

	for module in spec["modules"]:
		mdir = pkg / R.scrub(module["name"])
		_write(mdir / "__init__.py", "", written, force)
		_write(mdir / ".frappe", "", written, force)
		_write(mdir / "doctype" / "__init__.py", "", written, force)

	written += add_doctypes(spec, root, overwrite=force)

	rows = ["| DocType | Module | Type |", "|---|---|---|"]
	for module_name, dt in iter_doctypes(spec):
		kind = "Child table" if dt["istable"] else "Single" if dt["issingle"] else (
			"Submittable" if dt["is_submittable"] else "Standard"
		)
		rows.append(f"| {dt['name']} | {module_name} | {kind} |")
	_write(
		root / "README.md",
		README.format(
			app_title=app["title"],
			app_description=app["description"],
			app_name=app_name,
			app_license=app["license"],
			ecc_version=__version__,
			doctype_table="\n".join(rows),
		),
		written,
		force,
	)

	if with_ci:
		_write(root / ".github" / "workflows" / "ci.yml", CI_WORKFLOW.format(app_name=app_name), written, force)

	return written


def add_doctypes(spec: dict[str, Any], app_root: Path, *, overwrite: bool = False) -> list[Path]:
	"""Write every DocType in the spec into an existing app checkout at `app_root`."""
	app_name = spec["app"]["name"]
	pkg = app_root / app_name
	if not (pkg / "hooks.py").exists():
		raise GenerateError(f"{pkg} is not a Frappe app (no hooks.py)")

	written: list[Path] = []
	timestamp = _now()
	year = _dt.date.today().year
	publisher = spec["app"]["publisher"]

	modules_txt = pkg / "modules.txt"
	existing_modules = (
		[line.strip() for line in modules_txt.read_text().splitlines() if line.strip()]
		if modules_txt.exists()
		else []
	)
	for module in spec["modules"]:
		if module["name"] not in existing_modules:
			existing_modules.append(module["name"])
			mdir = pkg / R.scrub(module["name"])
			for path, content in ((mdir / "__init__.py", ""), (mdir / ".frappe", ""), (mdir / "doctype" / "__init__.py", "")):
				if not path.exists():
					_write(path, content, written)
	modules_txt.write_text("\n".join(existing_modules) + "\n", encoding="utf-8")

	for module_name, dt in iter_doctypes(spec):
		folder = pkg / R.scrub(module_name) / "doctype" / R.scrub(dt["name"])
		base = R.scrub(dt["name"])
		_write(folder / "__init__.py", "", written, overwrite)
		content = json.dumps(doctype_json(module_name, dt, timestamp), indent=1, ensure_ascii=False)
		_write(folder / f"{base}.json", content + "\n", written, overwrite)
		_write(folder / f"{base}.py", controller_py(dt, publisher, year), written, overwrite)
		if not dt["istable"]:
			_write(folder / f"{base}.js", controller_js(dt, publisher, year), written, overwrite)
			_write(folder / f"test_{base}.py", controller_test(app_name, dt, publisher, year), written, overwrite)
	return written
