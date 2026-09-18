# Frappe Core Coding Standards & Architecture Rules

## 1. DocType Design & Naming
- **DocType Naming**: Use Title Case with spaces for DocType labels/names (e.g. `Asset Maintenance Log`, not `asset_maintenance_log`).
- **Field Naming**: Use `snake_case` for all fieldnames (e.g. `asset_tag`, `purchase_date`, `maintenance_status`).
- **Module Structure**: Group related DocTypes into a cohesive Frappe module (e.g., `itam_core`, `telephony`). Never leave DocTypes in generic default modules.
- **Child Tables**: Any DocType marked as `Is Child Table` must:
  - Have fieldname prefix or clear descriptor.
  - Never be created or modified via standalone URL endpoints; always operate through the parent document (`parent.append("child_table_name", {...})`).
- **Docstatus Lifecycle**:
  - `docstatus = 0`: Draft. Editable.
  - `docstatus = 1`: Submitted. Immutable except for fields with `Allow on Submit` enabled.
  - `docstatus = 2`: Cancelled. Read-only audit state.
  - NEVER manually assign `doc.docstatus = 1` in custom code without triggering `.submit()`.

## 2. File & Directory Layout Conventions
```
your_app/
├── your_app/
│   ├── hooks.py
│   ├── patches.txt
│   ├── modules.txt
│   ├── api/                   # Dedicated whitelisted REST endpoints
│   ├── your_module/
│   │   └── doctype/
│   │       └── your_doctype/
│   │           ├── your_doctype.json
│   │           ├── your_doctype.py
│   │           ├── your_doctype.js
│   │           └── test_your_doctype.py
│   └── public/
│       ├── js/
│       └── css/
```

## 3. Transaction Integrity
- NEVER call `frappe.db.commit()` inside DocType controller event hooks (`before_insert`, `validate`, `on_update`, `before_submit`, `on_submit`, `on_cancel`). Frappe manages transaction boundaries automatically. Calling manual commit breaks test isolation and rollbacks on error.
- Use `frappe.throw(_("Message"))` to abort transactions cleanly with user-facing translatable error messages.

## 4. Internationalization & Strings
- All user-facing strings MUST be wrapped with `_("...")` for translation:
  ```python
  frappe.throw(_("Asset {0} is currently under maintenance").format(doc.asset_name))
  ```
- In JavaScript:
  ```javascript
  frappe.msgprint(__('Please provide a valid Serial Number.'));
  ```
