---
description: Visually schedule recurring background tasks and optimize Redis RQ worker queues.
---

# /frappe:cron

Visually schedule recurring background tasks and optimize Redis RQ worker queues.

## Usage
```
/frappe:cron [schedule] [method_path]
```

## Examples
```
/frappe:cron daily 'equipment_loan.tasks.check_overdue'
```

## Description
Invokes `frappe-cron-scheduler-optimizer` to execute the specialized workflow within the Frappe Framework and ERPNext runtime environment.
