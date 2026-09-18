# /frappe:doctype

**Purpose**: Scaffold complete, production-ready DocType schema JSON, Python controller, and client script.

## Usage
`/frappe:doctype "<DocType Name>" --module "<Module Name>" [--submittable] [--child-table]`

## Execution Workflow
1. Activate the `frappe-doctype-design` skill.
2. Generate `<doctype_name>.json` with standard Frappe properties:
   - Field layout (Sections, Columns, Fields)
   - Proper fieldtypes (Data, Link, Table, Select, etc.)
   - Permissions array for System Manager and standard roles
3. Generate `<doctype_name>.py` extending `Document`.
4. Generate `<doctype_name>.js` with `frappe.ui.form.on`.
5. Generate `test_<doctype_name>.py` with `FrappeTestCase`.
