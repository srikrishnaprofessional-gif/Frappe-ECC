---
name: frappe-doctypes
description: Design Frappe DocTypes correctly - standard, submittable, child table and single DocTypes, fieldtypes, naming (autoname), Link/Dynamic Link/Table fields, fetch_from, list view and indexes. Use when adding or changing a DocType, choosing fieldtypes, or reviewing DocType JSON.
---

# Designing DocTypes

Applies to Frappe v15 and later. Prefer generating DocTypes with the `frappe-app-spec` workflow.
Its validator applies these rules for you. Hand-edit DocType JSON only for small changes, and
then run `bench --site <site> migrate`.

## Choose the kind

| Kind | Flag | Use for |
|---|---|---|
| Standard | none | Master data and records (Customer, Clinic Patient) |
| Submittable | `is_submittable: 1` | Transactions that are locked once final: Draft (docstatus 0), Submitted (1), Cancelled (2). Frappe adds `amended_from` |
| Child table | `istable: 1` | Rows inside a parent (invoice items). Stored with `parent`, `parenttype`, `parentfield`. No permissions of its own |
| Single | `issingle: 1` | Settings. One record, values stored in `tabSingles`. Read with `frappe.db.get_single_value("X Settings", "field")` |
| Tree | `is_tree: 1` | Hierarchies. Needs `lft`, `rgt`, `is_group`, `old_parent` and a `parent_<scrubbed_doctype>` Link field. The controller must subclass `frappe.utils.nestedset.NestedSet` |
| Virtual | `is_virtual: 1` | Data from another system. The controller implements `db_insert`, `load_from_db`, `db_update`, `delete`, `get_list`, `get_count` and `get_stats` |

Names: start with a letter, use letters, digits, spaces, `-` and `_`, at most 61 characters.
DocType names are global on a site, so prefix them with your domain (`Clinic Appointment`).

## Fieldtypes that matter

| Fieldtype | Notes |
|---|---|
| Data | varchar(140). `options` may be `Email`, `Phone`, `URL`, `Name`, `Barcode` or `IBAN` for validation |
| Link | Stores the target's `name`. `options` = target DocType. **Not indexed automatically**: set `search_index: 1` if you filter or join on it |
| Dynamic Link | `options` = the fieldname of a Link-to-`DocType` (or a Select of DocType names) in the same DocType |
| Select | `options` separated by `\n`. A leading empty option allows "not set" |
| Table | `options` = a child DocType (`istable: 1`). Frappe's UI cannot edit a table inside a child table |
| Table MultiSelect | `options` = a child DocType with a Link field; renders as tags |
| Currency / Float / Percent | `precision` 1–6. Currency may set `options` to a Link field holding the currency |
| Int, Long Int, Check | Check stores 0/1; its default must be "0" or "1" |
| Small Text / Text / Long Text / Text Editor / Code | Cannot be unique or indexed |
| Date / Datetime / Time / Duration | Time comes back from the database as `datetime.timedelta` |
| Attach / Attach Image | Stores a file URL; the file itself is a `File` document |
| Read Only | Display value, usually with `fetch_from` |
| Section Break / Column Break / Tab Break | Layout only |

## Rules Frappe enforces on save or migrate

- Fieldnames are snake_case, at most 64 characters, and unique in the DocType.
- A fieldname cannot be a standard column (`name`, `owner`, `creation`, `modified`,
  `modified_by`, `docstatus`, `idx`, `parent`, `parenttype`, `parentfield`) or any attribute of
  `Document` (`save`, `insert`, `meta`, `flags`, `get`, `set`, `update`, `delete`, `is_new`,
  `status` is fine, `amended_from` is reserved for submittables).
- Link and Table fields need `options`.
- Layout fields cannot be mandatory, in list view, or in global search.
- `unique` works only on Data, Link, Read Only and Int.
- A hidden mandatory field needs a default.
- `fetch_from: "link_field.source_field"` needs `link_field` to be a Link in the same DocType.

## Naming (`autoname`)

| autoname | Result |
|---|---|
| `field:customer_code` | The field's value. Make the field `reqd` and `unique` |
| `format:APT-{YYYY}-{#####}` | `APT-2026-00001`. Braces for date parts, fields and counters |
| `naming_series:` | Users pick a series. Needs a Select field `naming_series` with options such as `APT-.YYYY.-` |
| `APT-.#####` | Old-style series (dots separate the parts) |
| `hash` | Random 10-character name (the default) |
| `autoincrement` | Integer names from a database sequence. Decide before the first record; it cannot be switched later |
| `prompt` | The user types the name |
| `UUID` | v16+ only |

For custom logic, define `autoname(self)` in the controller and set `self.name`.

## List view, search and performance

- Mark 3–5 key fields `in_list_view`, and filter fields `in_standard_filter`.
- `title_field` + `show_title_field_in_link: 1` shows readable titles in Link fields.
- `search_fields` (comma-separated in JSON) are searched by Link-field autocomplete.
- Add `search_index: 1` to fields used in filters, reports and joins, including Link fields.
- `track_changes: 1` keeps a Version log of edits. Turn it on for business records.

## Changing an existing DocType

- Renaming or removing a field loses its column data on migrate unless a patch copies it first.
  Use a `[pre_model_sync]` patch (see `frappe-patches`).
- Changing a fieldtype to a narrower one (Text → Data) can truncate data.
- Standard DocTypes live in the app's JSON files. Edits made in the Desk UI are written back to
  JSON only when the site has `developer_mode: 1`, and are lost otherwise.
- To change a DocType from another app (e.g. ERPNext), use Custom Fields and Property Setters,
  exported as fixtures. Never edit the other app's JSON.
