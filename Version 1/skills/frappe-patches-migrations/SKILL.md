---
name: frappe-patches-migrations
description: Guidelines for writing idempotent database patches, data migrations, schema synchronization, and registering entries in patches.txt.
---

# Frappe Database Patches & Migrations

## 1. Patch Anatomy
Patches must be strictly idempotent — executing them 5 times consecutively must yield the exact same stable state without throwing exceptions.

Example: `your_app/patches/v1_1/migrate_serial_numbers.py`
```python
import frappe

def execute():
    # 1. Reload schema first to ensure new column exists in MariaDB
    frappe.reload_doc("itam_core", "doctype", "asset_item")

    # 2. Check if work is already completed
    unmigrated = frappe.db.sql(
        """
        SELECT name, legacy_tag 
        FROM `tabAsset Item`
        WHERE (serial_no IS NULL OR serial_no = '')
          AND legacy_tag IS NOT NULL
        LIMIT 5000
        """,
        as_dict=True
    )

    if not unmigrated:
        return

    # 3. Batch update
    for row in unmigrated:
        formatted_serial = f"LEGACY-{row.legacy_tag.strip()}"
        frappe.db.set_value("Asset Item", row.name, "serial_no", formatted_serial, update_modified=False)

    frappe.logger().info(f"Migrated {len(unmigrated)} asset serial numbers")
```

## 2. Registering in `patches.txt`
In `<your_app>/patches.txt`:
```txt
# [pre_model_sync] -> runs before DocType schemas are synced to MariaDB
# standard patches run after DocType schemas are synced
your_app.patches.v1_1.migrate_serial_numbers
```

Run migrations:
```bash
bench --site itam.localhost migrate
```
Frappe records executed patches in `tabPatch Log`, preventing redundant re-runs.
