---
description: Run legacy ERP data migration wizard from SAP, Odoo, QuickBooks, Zoho, or Salesforce with balance reconciliation.
---

# /frappe:migrate

Run legacy ERP data migration wizard from SAP, Odoo, QuickBooks, Zoho, or Salesforce with balance reconciliation.

## Usage
```
/frappe:migrate [source_system] [data_archive]
```

## Examples
```
/frappe:migrate odoo data/odoo_dump.sql
```

## Description
Invokes `frappe-data-migration-concierge` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
