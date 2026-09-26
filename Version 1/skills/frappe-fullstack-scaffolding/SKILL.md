---
name: frappe-fullstack-scaffolding
description: Turnkey, end-to-end full-stack code synthesis for Frappe Framework, implementing complete vertical slices without placeholders.
---

# Turnkey Full-Stack Feature Scaffolding

## 1. The Zero-Placeholder Rule
When scaffolding a feature end-to-end, every layer of the vertical stack must be complete and executable:
- **DocType Schema**: Full `.json` file with valid fields, section breaks, permissions, and indexing.
- **Controller**: Full `.py` class with `validate()`, calculations, lifecycle methods, and localized error messages (`_("...")`).
- **Client Script**: Full `.js` file with `frappe.ui.form.on`, custom buttons, and dynamic field visibility.
- **Hooks Registration**: Updates to `hooks.py` for events, cron, or class overrides.
- **API Endpoints**: Full `@frappe.whitelist()` methods with permissions and validation.
- **Automated Tests**: Complete `FrappeTestCase` covering creation, validation, and submission.
- **Database Patch**: Idempotent patch registered in `patches.txt`.

## 2. Vertical Slice Generation Sequence
1. **Directory Structure**: Create `<app_name>/<module_name>/doctype/<doctype_slug>/`.
2. **Schema JSON**: Define schema, options, and permission arrays.
3. **Controller Class**: Extend `Document`, write validations, and prevent `frappe.db.commit()`.
4. **Desk Client Script**: Wire form hooks, action dialogs, and child table auto-math.
5. **Unit Tests**: Implement isolated tests in `test_<doctype_slug>.py`.
6. **Registration**: Verify `modules.txt`, `hooks.py`, and `patches.txt`.
