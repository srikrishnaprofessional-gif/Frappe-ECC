---
name: frappe-permissions-security
description: Comprehensive security model for Frappe apps, Role Permission Manager, Permission Queries, User Permissions, and SQLi defense.
---

# Frappe Permissions & Security Architecture

## 1. Multi-Layer Permission Model
Frappe enforces security through 4 complementary layers:
1. **Role Permissions (DocPerm)**: Defined per DocType (Role, Level, Read, Write, Create, Delete, Submit, Cancel).
2. **User Permissions**: Row-level constraints (e.g., restrict User A to `Company == 'Acme India'`).
3. **Permission Queries (`get_permission_query_conditions`)**: Programmatic SQL conditions appended to list queries.
4. **Document Controller Permission Checks (`has_permission`)**: Python method called per document instance.

## 2. Dynamic Permission Queries
Filter records in list views and queries based on dynamic session rules:
In `hooks.py`:
```python
permission_query_conditions = {
    "Asset Item": "your_app.security.get_asset_permission_query"
}

has_permission = {
    "Asset Item": "your_app.security.has_asset_permission"
}
```
In `security.py`:
```python
def get_asset_permission_query(user):
    if not user:
        user = frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Restrict users to assets assigned to their department
    user_dept = frappe.db.get_value("Employee", {"user_id": user}, "department")
    if not user_dept:
        return "1=0"
    
    return f"`tabAsset Item`.department = {frappe.db.escape(user_dept)}"

def has_asset_permission(doc, ptype="read", user=None):
    if "System Manager" in frappe.get_roles(user or frappe.session.user):
        return True
    user_dept = frappe.db.get_value("Employee", {"user_id": user or frappe.session.user}, "department")
    return doc.department == user_dept
```

## 3. SQL Injection Prevention
Always use parameterized queries:
```python
# CORRECT:
frappe.db.sql(
    """
    SELECT name, asset_name 
    FROM `tabAsset Item`
    WHERE status = %(status)s AND purchase_date >= %(from_date)s
    """,
    values={"status": "In Use", "from_date": "2026-01-01"},
    as_dict=True
)
```
