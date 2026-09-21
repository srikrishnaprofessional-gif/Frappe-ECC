---
description: Run forensic audit inspection, fraud detection, duplicate checks, and Segregation of Duties (SoD) verification.
---

# /frappe:audit

Run forensic audit inspection, fraud detection, duplicate checks, and Segregation of Duties (SoD) verification.

## Usage
```
/frappe:audit [doctype_or_module]
```

## Examples
```
/frappe:audit 'Equipment Loan'
```

## Description
Invokes `frappe-audit-trail-forensic-inspector` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
