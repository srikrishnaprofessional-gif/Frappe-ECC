# /frappe:controller

**Purpose**: Implement or refactor a Python DocType controller with lifecycle events and business validation.

## Usage
`/frappe:controller "<DocType Name>"`

## Execution Workflow
1. Invoke the **frappe-backend-builder** agent.
2. Read the existing DocType schema JSON to understand all fields and relationships.
3. Implement lifecycle hooks:
   - `before_insert()`
   - `validate()` (dates, state checks, calculations)
   - `before_save()` / `on_update()`
   - `on_submit()` / `on_cancel()` (if submittable)
4. Enforce Frappe standards: no `frappe.db.commit()`, use `frappe.throw(_("..."))`.
