---
name: frappe-hooks-and-events
description: Guide for mastering Frappe hooks.py, document event triggers, scheduled cron jobs, doctype class overrides, and fixtures.
---

# Frappe Hooks & Event Orchestration

Frappe's `hooks.py` is the central nervous system connecting custom applications to the framework and ERPNext.

## 1. Document Events (`doc_events`)
Hook into document events of any DocType (core ERPNext or custom):
```python
doc_events = {
    "Asset Item": {
        "validate": "your_app.events.asset.validate_warranty",
        "on_submit": "your_app.events.asset.create_ledger_entry",
        "on_cancel": "your_app.events.asset.revert_ledger_entry"
    },
    "*": {
        "after_insert": "your_app.events.audit.log_global_insert"
    }
}
```

The event handler receives the document and method name:
```python
def validate_warranty(doc, method=None):
    if doc.purchase_date and not doc.warranty_expiry_date:
        frappe.throw(_("Warranty Expiry Date is mandatory for new assets"))
```

## 2. Scheduled Cron Jobs (`scheduler_events`)
```python
scheduler_events = {
    "hourly": [
        "your_app.tasks.sync_hardware_telemetry"
    ],
    "daily": [
        "your_app.tasks.send_maintenance_alerts"
    ],
    "cron": {
        "0 3 * * *": [
            "your_app.tasks.nightly_depreciation_calc"
        ]
    }
}
```

## 3. Overriding DocType Controllers (`override_doctype_class`)
Safely extend or override core logic:
```python
override_doctype_class = {
    "Asset": "your_app.overrides.custom_asset.CustomAsset"
}
```
In `custom_asset.py`:
```python
from erpnext.assets.doctype.asset.asset import Asset

class CustomAsset(Asset):
    def validate(self):
        super().validate()
        self.custom_telemetry_check()

    def custom_telemetry_check(self):
        pass
```

## 4. Exporting Fixtures
Ensure custom roles, custom fields, and property setters persist across site migrations:
```python
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["IT Manager", "Asset Custodian"]]]},
    {"dt": "Custom Field", "filters": [["dt", "in", ["Asset", "Employee"]]]},
    {"dt": "Property Setter", "filters": [["doc_type", "in", ["Asset"]]]}
]
```
Export fixtures:
`bench --site itam.localhost export-fixtures`
