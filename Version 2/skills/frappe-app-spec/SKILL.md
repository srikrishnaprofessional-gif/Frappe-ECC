---
name: frappe-app-spec
description: Write a Frappe ECC app spec (JSON/YAML describing an app, its modules, DocTypes, fields and permissions) and turn it into an installable Frappe app with the frappe-ecc CLI. Use when creating a new Frappe app, adding DocTypes from a requirements description, or when a file named *.spec.json / ecc.spec.json is involved.
---

# Frappe ECC app spec

The `frappe-ecc` CLI turns a spec into an app that installs with `bench get-app` and syncs on
`bench migrate`. You write the spec; the CLI writes the boilerplate (DocType JSON, controllers,
form scripts, tests, hooks, pyproject) and checks the spec against the same rules Frappe applies
when it saves a DocType. Business logic, reports, workflows and UI polish are written by hand
afterwards, following the other frappe-* skills.

## Where the CLI is

Inside Claude Code the plugin puts `frappe-ecc` on PATH. If it is missing, run
`python3 -m frappe_ecc` from the plugin root (`${CLAUDE_PLUGIN_ROOT}`) or `pip install` the repo.

## Workflow

1. Write the spec to `<app_name>.spec.json` (or `.yaml` when PyYAML is available).
2. `frappe-ecc validate <spec>` and fix every error. Read the warnings; each one is a real risk.
3. `frappe-ecc new <spec> --dest <dir> [--ci]` creates `<dir>/<app_name>/`.
4. `frappe-ecc verify <dir>/<app_name> --bench <bench> --site <throwaway-site>` links the app
   into the bench, installs it, migrates and runs its tests. Only report the app as working when
   this prints `VERIFIED`.
5. Add business logic in the generated controllers, then re-run verify.

To add DocTypes to an app that already exists, write a spec with the same `app` block and only
the new DocTypes, then `frappe-ecc add-doctypes <spec> <app_path>` and `bench migrate`.

## Spec format

```json
{
  "spec_version": 1,
  "app": {
    "name": "clinic_management",          // snake_case, becomes the Python package
    "title": "Clinic Management",
    "publisher": "Example Clinic Ltd",
    "email": "dev@example.com",
    "description": "Patients and appointments",
    "license": "mit",
    "required_apps": []                   // e.g. ["erpnext"] when you link to ERPNext DocTypes
  },
  "modules": [
    {
      "name": "Clinic",
      "doctypes": [
        {
          "name": "Clinic Patient",
          "autoname": "format:PAT-{#####}",
          "title_field": "patient_name",
          "search_fields": ["mobile"],
          "fields": [
            {"fieldname": "patient_name", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
            {"fieldname": "mobile", "fieldtype": "Data", "options": "Phone", "reqd": 1},
            {"fieldname": "gender", "fieldtype": "Select", "options": ["", "Female", "Male", "Other"]}
          ],
          "permissions": [
            {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "Clinic Receptionist", "read": 1, "write": 1, "create": 1}
          ]
        }
      ]
    }
  ]
}
```

DocType keys: `name`, `description`, `istable` (alias `child_table`), `issingle` (alias `single`),
`is_submittable` (alias `submittable`), `autoname` (alias `naming`), `title_field`, `search_fields`,
`sort_field`, `sort_order`, `track_changes`, `quick_entry`, `allow_rename`, `allow_import`,
`editable_grid`, `show_title_field_in_link`, `fields`, `permissions`.

Field keys are Frappe DocField properties: `fieldname`, `label`, `fieldtype`, `options`, `reqd`,
`unique`, `default`, `description`, `in_list_view`, `in_standard_filter`, `in_global_search`,
`bold`, `read_only`, `hidden`, `depends_on`, `mandatory_depends_on`, `read_only_depends_on`,
`fetch_from`, `fetch_if_empty`, `precision`, `length`, `search_index`, `allow_on_submit`, `no_copy`,
`print_hide`, `permlevel`, `non_negative`, `collapsible`, and a few more. `type` and `required`
are accepted as aliases. A field with only a `label` gets a fieldname made from it.

Unknown keys are errors, so typos are caught.

## Design rules the validator enforces

- Prefix DocType names with the domain (`Clinic Patient`, not `Patient`). DocType and module
  names are global on a site. The validator rejects names Frappe already uses and warns about
  names ERPNext or HRMS use.
- Child tables (`istable`) have no permissions and cannot contain Table fields.
- `field:<fieldname>` naming needs that field to be `reqd`. `naming_series:` needs a Select field
  called `naming_series`. `format:` uses braces, e.g. `format:APT-{YYYY}-{#####}`.
- Permission rules follow Frappe's dependencies: cancel needs submit; submit, cancel and amend
  need write; amend and import need create; singles cannot grant report, import or export.
- Leave `permissions` out to get full System Manager access only.
- Link targets outside the spec are warnings. The target must exist on the site where the app is
  installed, so add the owning app to `required_apps`.

## What the generated app contains

- `pyproject.toml` (flit, Python ≥3.10), `hooks.py`, `modules.txt`, `patches.txt`, `license.txt`,
  `README.md`, `.gitignore`, `ecc.spec.json` (the normalised spec, kept for traceability).
- Per DocType: `<doctype>.json`, controller class, form script (not for child tables), and a test.
- `<app>/factories.py` with `make_doc(doctype, **values)`. It inserts a document with every
  mandatory field filled and creates linked records from the same app. Use it in your own tests.
- With `--ci`: a GitHub Actions workflow that installs the app on Frappe v15 and runs its tests.

Generated tests use `IntegrationTestCase` on v16+ and fall back to `FrappeTestCase` on v15.
