---
description: Setup real-time SLA tracking, breach warnings, and automated supervisory escalation chains.
---

# /frappe:sla

Setup real-time SLA tracking, breach warnings, and automated supervisory escalation chains.

## Usage
```
/frappe:sla [doctype_name] [duration_hours]
```

## Examples
```
/frappe:sla 'Equipment Loan' 48
```

## Description
Invokes `frappe-sla-escalation-manager` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
