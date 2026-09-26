---
name: frappe-background-jobs
description: Run work outside the web request in Frappe - frappe.enqueue with queues and timeouts, deduplication with job_id, enqueue_after_commit, doc.queue_action, scheduled jobs, progress updates, and error logging. Use for slow tasks, bulk operations, imports, external API calls, or anything that should not block a user's request.
---

# Background jobs

Jobs run in RQ workers started by `bench start` (development) or supervisor/systemd
(production). Queues: `short`, `default`, `long`. If no worker is running, jobs wait in Redis.

## Enqueue

```python
import frappe

frappe.enqueue(
	"clinic_management.tasks.send_appointment_sms",   # dotted path (or the function itself)
	queue="short",
	timeout=300,
	enqueue_after_commit=True,     # only run if the current request commits
	job_id=f"sms::{appointment}",  # with deduplicate=True, skip if the same job is queued or running
	deduplicate=True,
	appointment=appointment,       # keyword arguments passed to the function
)
```

- Pass names, not documents. Load the document inside the job; it may have changed.
- Use `enqueue_after_commit=True` when the job reads data written in this request. Otherwise the
  worker can run before the commit and not see the data.
- `timeout` is in seconds. Defaults are 300 (short and default queues) and 1500 (long queue).
- `frappe.enqueue(..., now=True)` runs synchronously. Tests use it.

For a method on a document: `doc.queue_action("submit", timeout=600)` submits in the background
and locks the document meanwhile. This is useful for documents with thousands of rows.

## Write the job

```python
import frappe
from frappe.utils import cint


def recalculate_all(batch_size=500):
	names = frappe.get_all("Clinic Patient", pluck="name")
	for i, name in enumerate(names, 1):
		try:
			frappe.get_doc("Clinic Patient", name).run_method("update_visit_stats")
		except Exception:
			frappe.log_error(title=f"Visit stats failed for {name}")
		if i % batch_size == 0:
			frappe.db.commit()                                   # long job: commit per batch
			frappe.publish_progress(i * 100 / len(names), title="Recalculating")
```

- Jobs run as the user who enqueued them (the session user is restored), so permission checks apply.
- An exception fails the job and rolls back uncommitted work. Frappe records the traceback in
  **Error Log** and **RQ Job**. Use `frappe.log_error()` for failures you catch and continue past.
- A long job may commit per batch so earlier progress survives a later failure. Make the job
  restartable: skip rows already processed.
- `frappe.publish_progress(percent, title=..., doctype=..., docname=...)` shows a progress bar to
  the user who started it. `frappe.publish_realtime("event", data, user=...)` sends custom events.

## Scheduled jobs

Declare them in `hooks.py` under `scheduler_events` (see `frappe-hooks`). They show up as
**Scheduled Job Type** records after `bench migrate`, where you can see last run and failures.
The site's scheduler must be enabled: `bench --site <site> enable-scheduler`.

## Debug

- `bench --site <site> show-pending-jobs` and the **RQ Job** list in Desk.
- `bench worker --queue short` runs a worker in the foreground so you can watch its logs.
- `bench --site <site> execute clinic_management.tasks.recalculate_all` runs a function once,
  synchronously.
