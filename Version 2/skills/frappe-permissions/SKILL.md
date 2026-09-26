---
name: frappe-permissions
description: Design Frappe access control - roles, DocType permission rules (DocPerm), permlevels, if_owner, User Permissions, permission_query_conditions and has_permission hooks, sharing, and checking permissions in code. Use when deciding who can see or change records in a Frappe app.
---

# Permissions

Frappe checks access in layers. A user needs every layer to allow the action.

1. **Role permissions** (DocPerm rows on the DocType, plus Custom DocPerm from the Role Permission
   Manager): which roles may read, write, create, delete, submit, cancel, amend, report, export,
   import, print, email or share.
2. **User Permissions**: records a user is restricted to. For example, Company = "Acme India"
   limits every DocType that links to Company.
3. **`permission_query_conditions` hook**: SQL added to list and report queries.
4. **`has_permission` hook**: a per-document check that can only *deny*, never grant
   (`frappe/permissions.py: has_controller_permissions`).
5. **Sharing** (DocShare) grants read/write/share on one document to one user.

## Role rules

Define them in the DocType (the app spec's `permissions` list), not by hand on each site.
Frappe enforces these dependencies:
- `cancel` needs `submit`; `submit`, `cancel` and `amend` need `write`; `amend` and `import` need `create`.
- `submit` and `amend` need a submittable DocType; `import` needs `allow_import`.
- Single DocTypes cannot grant `report`, `import` or `export`.
- A rule at `permlevel` > 0 needs a rule for the same role at permlevel 0, and only grants read/write.
- `if_owner: 1` limits that rule to documents the user created.

Roles referenced in DocType permissions are created automatically on migrate. Ship role
descriptions, desk access and Role Profiles as fixtures if you need them to be exact.

## Field-level access with permlevel

Give sensitive fields `permlevel: 1`, then grant level 1 only to the roles that may see or edit
them:

```json
{"fieldname": "diagnosis", "fieldtype": "Small Text", "permlevel": 1}
```
```json
"permissions": [
  {"role": "Clinic Receptionist", "read": 1, "write": 1, "create": 1},
  {"role": "Clinic Doctor", "read": 1, "write": 1, "create": 1},
  {"role": "Clinic Doctor", "permlevel": 1, "read": 1, "write": 1}
]
```

## Row-level rules in code

```python
# hooks.py
permission_query_conditions = {"Clinic Appointment": "clinic_management.permissions.appointment_query"}
has_permission = {"Clinic Appointment": "clinic_management.permissions.appointment_has_permission"}
```

```python
# clinic_management/permissions.py
import frappe


def _doctor_for(user):
	return frappe.db.get_value("Clinic Doctor", {"user": user}, "name")


def appointment_query(user=None):
	user = user or frappe.session.user
	if "System Manager" in frappe.get_roles(user) or "Clinic Receptionist" in frappe.get_roles(user):
		return ""                                   # no extra condition
	doctor = _doctor_for(user)
	if not doctor:
		return "1=0"                                # sees nothing
	return f"`tabClinic Appointment`.`doctor` = {frappe.db.escape(doctor)}"


def appointment_has_permission(doc, ptype=None, user=None):
	user = user or frappe.session.user
	if "Clinic Doctor" in frappe.get_roles(user) and "System Manager" not in frappe.get_roles(user):
		return doc.doctor == _doctor_for(user)      # False denies; True only means "no objection"
	return True
```

- The query hook returns a SQL condition string. Escape every value with `frappe.db.escape`.
- Keep the two hooks consistent: whatever the list hides, `has_permission` must deny too,
  or users can open hidden records by URL.
- Both hooks affect `frappe.get_list` and the REST API, but not `frappe.get_all` or raw
  `frappe.db.sql`, which ignore permissions.

## Checking permissions in code

```python
frappe.has_permission("Clinic Appointment", "create", throw=True)
doc.check_permission("write")
frappe.only_for(["System Manager", "Clinic Doctor"])
frappe.get_list("Clinic Appointment", ...)        # applies all layers above
```

`doc.insert()` and `doc.save()` check permissions for the session user.
`ignore_permissions=True` bypasses them. Use it only where the code has already decided the
action is allowed (background jobs, install scripts, a guest endpoint with a narrow purpose),
and never on data the caller controls without checks.

## Testing permissions

```python
frappe.set_user("doctor@example.com")
try:
	self.assertRaises(frappe.PermissionError, frappe.get_doc("Clinic Appointment", other).save)
finally:
	frappe.set_user("Administrator")
```

Create test users with `frappe.get_doc({"doctype": "User", "email": ..., "first_name": ...}).insert()`
then `user.add_roles("Clinic Doctor")`. Always reset the user in `finally` or `tearDown`.
