---
description: Setup PII encryption, GDPR Right-to-be-Forgotten erasure workflows, and data consent logs.
---

# /frappe:gdpr

Setup PII encryption, GDPR Right-to-be-Forgotten erasure workflows, and data consent logs.

## Usage
```
/frappe:gdpr audit-pii [app_name]
```

## Examples
```
/frappe:gdpr audit-pii equipment_loan
```

## Description
Invokes `frappe-gdpr-data-privacy-officer` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
