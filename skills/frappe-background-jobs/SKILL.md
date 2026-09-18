---
name: frappe-background-jobs
description: Asynchronous task execution using frappe.enqueue, Redis RQ queues, scheduling, error logging, and progress tracking.
---

# Frappe Background Jobs & RQ Queues

## 1. Enqueueing Asynchronous Work
Offload slow operations (emails, batch updates, external API calls, PDF generation) from the HTTP request cycle:
```python
import frappe

def trigger_asset_sync(category):
    # Enqueue task to background worker
    frappe.enqueue(
        method="your_app.tasks.sync_assets",
        queue="default",            # 'short', 'default', 'long'
        timeout=600,                # Max seconds before timeout
        is_async=True,
        job_name=f"sync_assets_{category}",
        category=category,
        now=frappe.flags.in_test    # Synchronous during tests
    )
```

## 2. Queue Categorization
- `short`: High-priority jobs taking < 300 seconds (e.g. single transactional email, webhook dispatch).
- `default`: Standard jobs taking < 600 seconds.
- `long`: Heavy reports, batch data imports, bulk sync jobs taking up to 1500+ seconds.

## 3. Worker Job Implementation Pattern
```python
def sync_assets(category):
    try:
        frappe.publish_progress(percent=10, title=_("Starting Asset Sync"))
        assets = frappe.get_all("Asset Item", filters={"asset_category": category}, fields=["name", "serial_no"])
        
        total = len(assets)
        for idx, asset in enumerate(assets):
            # Do work
            percent = int(((idx + 1) / total) * 100)
            if idx % 20 == 0:
                frappe.publish_progress(percent=percent, title=_("Syncing Assets..."))
        
        frappe.publish_realtime("asset_sync_completed", {"category": category})
    except Exception as e:
        frappe.log_error(title=_("Asset Sync Failed"), message=frappe.get_traceback())
        raise e
```
