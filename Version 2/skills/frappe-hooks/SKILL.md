---
name: frappe-hooks
description: Configure a Frappe app's hooks.py - doc_events on other apps' DocTypes, scheduler_events, override_doctype_class, extend_doctype_class, fixtures, doctype_js, app_include_js, boot and install hooks. Use when wiring an app into Frappe/ERPNext or exporting configuration records.
---

# hooks.py

`<app>/<app>/hooks.py` is read at startup and cached. After editing it, run
`bench --site <site> clear-cache` (and `bench restart` in production).

## React to documents from any app

```python
doc_events = {
	"Sales Invoice": {
		"validate": "clinic_management.events.sales_invoice.validate",
		"on_submit": "clinic_management.events.sales_invoice.on_submit",
	},
	"*": {"on_update": "clinic_management.events.audit.on_any_update"},
}
```

```python
# clinic_management/events/sales_invoice.py
import frappe
from frappe import _


def validate(doc, method=None):
	if doc.customer_group == "Patients" and not doc.get("patient"):
		frappe.throw(_("Patient is required"))
```

Handlers get `(doc, method)` and run after the DocType's own controller method of the same
name. Use `doc_events` for other apps' DocTypes; for your own DocTypes, write the logic in the
controller. `"*"` runs for every DocType, so keep it cheap.

## Scheduled jobs

```python
scheduler_events = {
	"daily": ["clinic_management.tasks.send_reminders"],
	"hourly_long": ["clinic_management.tasks.sync_lab_results"],
	"cron": {"0 7 * * 1-5": ["clinic_management.tasks.weekday_digest"]},
}
```

Keys: `all` (every scheduler run, a few minutes apart; avoid for heavy work), `hourly`, `daily`, `weekly`, `monthly`,
their `_long` variants (run on the long queue), and `cron`. Scheduled methods take no arguments.
The scheduler must be enabled (`bench --site <site> enable-scheduler`) and workers running.
New or changed entries are picked up on `bench migrate`.

## Change another app's controller

```python
# Preferred when available (v16+): add methods/overrides without replacing the class
extend_doctype_class = {"Sales Invoice": ["clinic_management.overrides.SalesInvoiceMixin"]}

# Works on v15 and later: replace the class. Only one app can override a DocType.
override_doctype_class = {"Sales Invoice": "clinic_management.overrides.CustomSalesInvoice"}
```

```python
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class CustomSalesInvoice(SalesInvoice):
	def validate(self):
		super().validate()
		...
```

Always call `super()`. Prefer `doc_events` when you only need to add behaviour.

Other overrides: `override_whitelisted_methods = {"erpnext...get_item_details": "your.fn"}`.

## Client-side includes

```python
doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}      # extra form script for another app's DocType
doctype_list_js = {"Sales Invoice": "public/js/sales_invoice_list.js"}
app_include_js = "/assets/clinic_management/js/clinic.js"          # loaded on every Desk page
web_include_css = "/assets/clinic_management/css/web.css"
```

Files under `public/` are served from `/assets/<app>/` after `bench build --app <app>`.

## Fixtures: ship configuration records with the app

```python
fixtures = [
	{"dt": "Role", "filters": [["name", "in", ["Clinic Doctor", "Clinic Receptionist"]]]},
	{"dt": "Custom Field", "filters": [["module", "=", "Clinic"]]},
	{"dt": "Property Setter", "filters": [["module", "=", "Clinic"]]},
	{"dt": "Workflow", "filters": [["name", "in", ["Clinic Appointment Approval"]]]},
]
```

Export with `bench --site <site> export-fixtures --app clinic_management`. This writes
`<app>/fixtures/*.json`, which are imported on install and every migrate. Always filter fixtures
so you never export another app's or a user's records. Set `module` on Custom Fields and Property
Setters you create so the filter above catches them.

## Install, boot and permissions hooks

```python
after_install = "clinic_management.install.after_install"     # create default records
before_uninstall = "clinic_management.install.before_uninstall"
after_migrate = ["clinic_management.install.after_migrate"]   # must be idempotent
boot_session = "clinic_management.boot.boot_session"          # add values to frappe.boot
permission_query_conditions = {"Clinic Appointment": "clinic_management.permissions.appointment_query"}
has_permission = {"Clinic Appointment": "clinic_management.permissions.appointment_has_permission"}
required_apps = ["erpnext"]
```

See `frappe-permissions` for the permission hooks.
