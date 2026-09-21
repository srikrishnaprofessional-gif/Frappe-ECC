---
description: Architect role-based access control, Custom DocPerms, and row-level permission query conditions with zero privilege escalation.
---

# /frappe:rbac

Autonomous access control and permission matrix modeling for Frappe Framework.

## Usage
```
/frappe:rbac "<DocType Name>" --roles "Manager,Operator,Auditor"
```

## Description
Invokes `frappe-rbac-compliance-guardian` to model multi-tier role permissions, document-level row filtering hooks (`get_permission_query_conditions`), and field-level `permlevel` protection.
