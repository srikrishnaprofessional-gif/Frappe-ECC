---
name: frappe-reports-and-dashboards
description: Comprehensive recipes for building Frappe Script Reports, Query Reports, and Dashboard Charts with column definitions and filters.
---

# Frappe Reports & Analytics Dashboards

## 1. Script Report Backend (`<report_name>.py`)
```python
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    report_summary = get_report_summary(data)
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {
            "fieldname": "asset_name",
            "label": _("Asset Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "asset_category",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Asset Category",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Select",
            "width": 120
        },
        {
            "fieldname": "purchase_date",
            "label": _("Purchase Date"),
            "fieldtype": "Date",
            "width": 110
        }
    ]

def get_data(filters):
    conditions = {}
    if filters.get("category"):
        conditions["asset_category"] = filters.get("category")
    if filters.get("status"):
        conditions["status"] = filters.get("status")

    return frappe.get_all(
        "Asset Item",
        filters=conditions,
        fields=["asset_name", "asset_category", "status", "purchase_date"],
        order_by="creation desc"
    )

def get_chart_data(data):
    counts = {}
    for row in data:
        counts[row.status] = counts.get(row.status, 0) + 1

    return {
        "data": {
            "labels": list(counts.keys()),
            "datasets": [{"name": _("Count"), "values": list(counts.values())}]
        },
        "type": "donut",
        "colors": ["#2ecc71", "#e67e22", "#e74c3c", "#95a5a6"]
    }

def get_report_summary(data):
    total = len(data)
    active = sum(1 for row in data if row.status == "In Use")
    return [
        {"value": total, "label": _("Total Assets"), "indicator": "blue"},
        {"value": active, "label": _("Active Assets"), "indicator": "green"}
    ]
```

## 2. Script Report Frontend (`<report_name>.js`)
```javascript
frappe.query_reports['Asset Inventory Report'] = {
    filters: [
        {
            fieldname: 'category',
            label: __('Category'),
            fieldtype: 'Link',
            options: 'Asset Category'
        },
        {
            fieldname: 'status',
            label: __('Status'),
            fieldtype: 'Select',
            options: '\nIn Use\nUnder Maintenance\nDecommissioned'
        }
    ]
};
```
