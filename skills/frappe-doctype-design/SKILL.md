---
name: frappe-doctype-design
description: Design and create complete, robust Frappe DocTypes, Child Tables, Single DocTypes, fieldtypes, autonaming rules, and schema JSON files.
---

# Frappe DocType Design & Schema Modeling

This skill provides step-by-step instructions and production standards for designing DocTypes in Frappe Framework.

## 1. DocType Categories
- **Standard DocType**: Regular table stored in MariaDB/PostgreSQL (e.g. `tabAsset`). Has state, status, name.
- **Submittable DocType**: `is_submittable: 1`. Supports Draft (`0`), Submitted (`1`), Cancelled (`2`). Immutable once submitted.
- **Child Table**: `istable: 1`. Stored as child records linked to parent (`parent`, `parentfield`, `parenttype`). Cannot exist without a parent.
- **Single DocType**: `issingle: 1`. Configuration store stored as key-value pairs in `tabSingles`. Used for settings.
- **Virtual DocType**: `is_virtual: 1`. Backed by external APIs or memory rather than a database table.

## 2. Common Field Types & Best Practices
| Field Type | Purpose & Notes |
|---|---|
| `Data` | Standard text input (up to 140 chars). |
| `Link` | Foreign key referencing another DocType. Always set `options: "Target DocType"`. Automatically indexed. |
| `Dynamic Link` | Polymorphic link. Requires an accompanying `Link` field (`options: "DocType"`). |
| `Select` | Dropdown with fixed options separated by `\n`. |
| `Table` | Embedded child table grid. `options: "Child DocType Name"`. |
| `Currency` | Numeric with currency symbol formatting. Often paired with `options: "currency"`. |
| `Check` | Boolean 0 or 1. |
| `Attach Image` | File attachment restricted to image types. |
| `Read Only` | Display-only field or calculated value. |

## 3. Autonaming Patterns
Configure `autoname` in DocType JSON:
- `format:AST-.YYYY.-.#####` -> generates `AST-2026-00001`
- `field:serial_no` -> uses the unique serial number field
- `naming_series:` -> allows user to select prefix in form
- `hash` -> 10-character random hash
- `Prompt` -> prompts the user to enter name on creation

## 4. Production DocType JSON Template
```json
{
  "actions": [],
  "allow_rename": 0,
  "autoname": "format:AST-.YYYY.-.#####",
  "creation": "2026-09-18 10:00:00.000000",
  "doctype": "DocType",
  "engine": "InnoDB",
  "field_order": [
    "details_section",
    "asset_name",
    "asset_category",
    "status",
    "column_break_1",
    "serial_no",
    "purchase_date",
    "items_section",
    "items"
  ],
  "fields": [
    {
      "fieldname": "details_section",
      "fieldtype": "Section Break",
      "label": "Asset Details"
    },
    {
      "fieldname": "asset_name",
      "fieldtype": "Data",
      "in_list_view": 1,
      "label": "Asset Name",
      "reqd": 1,
      "search_index": 1
    },
    {
      "fieldname": "asset_category",
      "fieldtype": "Link",
      "in_standard_filter": 1,
      "label": "Category",
      "options": "Asset Category",
      "reqd": 1
    },
    {
      "default": "Draft",
      "fieldname": "status",
      "fieldtype": "Select",
      "in_list_view": 1,
      "label": "Status",
      "options": "Draft\nIn Use\nUnder Maintenance\nDecommissioned"
    },
    {
      "fieldname": "column_break_1",
      "fieldtype": "Column Break"
    },
    {
      "fieldname": "serial_no",
      "fieldtype": "Data",
      "label": "Serial Number",
      "unique": 1,
      "search_index": 1
    },
    {
      "fieldname": "purchase_date",
      "fieldtype": "Date",
      "label": "Purchase Date"
    },
    {
      "fieldname": "items_section",
      "fieldtype": "Section Break",
      "label": "Components"
    },
    {
      "fieldname": "items",
      "fieldtype": "Table",
      "label": "Components",
      "options": "Asset Component Item"
    }
  ],
  "is_submittable": 0,
  "module": "Itam Core",
  "name": "Asset Item",
  "naming_rule": "Expression",
  "owner": "Administrator",
  "permissions": [
    {
      "create": 1,
      "delete": 1,
      "email": 1,
      "export": 1,
      "print": 1,
      "read": 1,
      "report": 1,
      "role": "System Manager",
      "share": 1,
      "write": 1
    }
  ],
  "sort_field": "modified",
  "sort_order": "DESC",
  "track_changes": 1
}
```
