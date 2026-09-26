---
name: frappe-patches
description: Write Frappe data migrations - patches.txt with pre_model_sync and post_model_sync, idempotent execute() functions, renaming fields and DocTypes without losing data, and backfilling values. Use when a schema change needs existing data moved or fixed on sites that already run the app.
---

# Patches

A patch is a Python module with `execute()` listed in `<app>/patches.txt`. `bench migrate` runs
each patch once per site and records it in the `Patch Log` DocType.

```text
[pre_model_sync]
# runs BEFORE DocType JSON is synced: old columns still exist
clinic_management.patches.v1_1.copy_phone_to_mobile

[post_model_sync]
# runs AFTER sync: new columns exist, removed ones are gone
clinic_management.patches.v1_1.set_default_status
```

Layout: `<app>/patches/v1_1/__init__.py` and `<app>/patches/v1_1/set_default_status.py`. Create
it with `bench create-patch` or by hand.

## Pick the section

| Change | Section |
|---|---|
| Rename a field or DocType and keep its data | `pre_model_sync` (move data while the old column still exists) |
| Fill a new field, fix values, create records | `post_model_sync` |
| Remove a field whose data must be archived first | `pre_model_sync` |

## Examples

```python
# post_model_sync: backfill a new field
import frappe


def execute():
	frappe.db.sql(
		"""update `tabClinic Appointment` set status = 'Scheduled'
		where ifnull(status, '') = '' and docstatus < 2"""
	)
```

```python
# pre_model_sync: field renamed from `phone` to `mobile` in the JSON
import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	if frappe.db.has_column("Clinic Patient", "phone"):
		frappe.reload_doc("clinic", "doctype", "clinic_patient")   # load the new schema
		rename_field("Clinic Patient", "phone", "mobile")         # copies data, updates reports/filters
```

```python
# rename a DocType
import frappe


def execute():
	if frappe.db.exists("DocType", "Patient Visit") and not frappe.db.exists("DocType", "Clinic Appointment"):
		frappe.rename_doc("DocType", "Patient Visit", "Clinic Appointment", force=True)
```

## Rules

- **Idempotent**: a patch may meet a site where the data is already fixed, or be re-run after a
  failure. Guard with `has_column`, `exists` and `where` clauses.
- **Don't commit** in the middle unless you process large batches on purpose. Migrate commits
  after each patch.
- **Large tables**: update in SQL, or loop over `frappe.get_all(..., pluck="name")` in chunks.
  Don't call `doc.save()` for a million rows.
- **Never edit a patch that has shipped.** Sites that ran it won't run it again; add a new patch.
- In `pre_model_sync`, the DocType JSON on disk is newer than the database. Call
  `frappe.reload_doc(module, "doctype", name)` before using the new schema.
- One-line patches can be written inline: `execute:frappe.delete_doc_if_exists("Report", "Old Report")`.
- Test a patch on a copy of production data: `bench --site <copy> migrate`, then check the data.
