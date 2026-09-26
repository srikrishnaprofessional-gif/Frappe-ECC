---
name: frappe-controllers
description: Write Frappe DocType controllers and data access - lifecycle hook order (validate, before_save, on_submit...), frappe.get_doc / frappe.db / frappe.qb, transactions, errors and translations. Use when writing server-side Python business logic in a Frappe app.
---

# Controllers, ORM and queries

## Lifecycle order (from `frappe/model/document.py`)

| Action | Methods called, in order |
|---|---|
| `doc.insert()` | `before_insert` → naming (`autoname`) → `before_validate` → `validate` → `before_save` → *row inserted* → `after_insert` → `on_update` → `on_change` |
| `doc.save()` (draft) | `before_validate` → `validate` → `before_save` → *row updated* → `on_update` → `on_change` |
| `doc.submit()` | `before_validate` → `validate` → `before_submit` → *docstatus=1* → `on_update` → `on_submit` → `on_change` |
| `doc.cancel()` | `before_cancel` → *docstatus=2* → `on_cancel` → `on_change` |
| save of a submitted doc | `before_update_after_submit` → `on_update_after_submit` → `on_change` |
| `frappe.delete_doc()` | `on_trash` → *deleted* → `after_delete` |

Put checks and derived values in `validate` (it runs for insert, save and submit). Put side
effects on other documents in `on_update`, `on_submit` or `on_cancel`, which run after this
document is written. Anything raised in any hook rolls back the whole request.

```python
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class ClinicAppointment(Document):
	def validate(self):
		self.validate_dates()
		self.total = sum(flt(row.amount) for row in self.items)

	def validate_dates(self):
		if self.appointment_date and getdate(self.appointment_date) < getdate():
			frappe.throw(_("Appointment date cannot be in the past"), title=_("Invalid Date"))

	def on_submit(self):
		frappe.db.set_value("Clinic Patient", self.patient, "last_visit", self.appointment_date)

	def on_cancel(self):
		...  # undo what on_submit did
```

Rules:
- Wrap every user-facing string in `_()` (Python) or `__()` (JS) so it can be translated.
- Raise with `frappe.throw(msg, exc=frappe.ValidationError)`. Use `frappe.msgprint` for
  non-blocking messages.
- Never call `frappe.db.commit()` inside a controller or whitelisted method. Frappe commits at
  the end of the request and rolls back on error; a manual commit makes partial writes permanent.
  Commits belong only in long background jobs that process batches.
- Compare values with `doc.has_value_changed("status")` or `doc.get_doc_before_save()`.
- Use `flt`, `cint`, `cstr`, `getdate`, `get_datetime` from `frappe.utils` for type-safe conversion.
- Do not set `docstatus` by hand; call `submit()` / `cancel()`.

## Reading and writing

```python
doc = frappe.get_doc("Clinic Patient", name)            # full document, runs permission checks on save
doc = frappe.get_cached_doc("Clinic Settings")           # cached; do not modify
frappe.get_single("Clinic Settings")                     # single DocType
frappe.db.get_single_value("Clinic Settings", "clinic_name")

new = frappe.new_doc("Clinic Patient")
new.patient_name = "Asha"
new.append("contacts", {"phone": "+91..."})
new.insert()                                             # permission-checked

frappe.db.get_value("Clinic Patient", name, "mobile")
frappe.db.get_value("Clinic Patient", {"mobile": m}, ["name", "patient_name"], as_dict=True)
frappe.db.exists("Clinic Patient", {"mobile": m})
frappe.db.set_value("Clinic Patient", name, "status", "Inactive")   # skips controller hooks
frappe.get_all("Clinic Appointment", filters={"status": "Scheduled"}, fields=["name", "patient"],
               order_by="appointment_date asc", limit=100)          # ignores permissions
frappe.get_list(...)                                     # same, but applies the user's permissions
```

`frappe.get_all` ignores permissions and `frappe.get_list` applies them. In a whitelisted API,
use `get_list` or check permissions first.

`frappe.db.set_value` and `doc.db_set` write directly and skip validation. Use them only for
fields that are safe to change without hooks (status flags, counters).

## Query builder

```python
from frappe.query_builder.functions import Count, Sum

Apt = frappe.qb.DocType("Clinic Appointment")
Pat = frappe.qb.DocType("Clinic Patient")
rows = (
	frappe.qb.from_(Apt)
	.join(Pat).on(Apt.patient == Pat.name)
	.select(Pat.patient_name, Count(Apt.name).as_("visits"), Sum(Apt.fee).as_("fees"))
	.where((Apt.docstatus == 1) & (Apt.appointment_date >= from_date))
	.groupby(Pat.name)
	.orderby(Sum(Apt.fee), order=frappe.qb.desc)
	.limit(20)
).run(as_dict=True)
```

Values in `frappe.qb` are parameterised. With raw SQL, always pass values separately:

```python
frappe.db.sql(
	"select name from `tabClinic Patient` where mobile = %(mobile)s",
	{"mobile": mobile},
	as_dict=True,
)
```

Never build SQL with f-strings, `%` or `.format()` from user input. Frappe Shield flags it.

## Performance

- No `frappe.get_doc` / `frappe.db.get_value` inside loops over many rows. Fetch once with
  `frappe.get_all(..., filters={"name": ["in", names]})` and build a dict.
- Use `frappe.get_cached_value` / `get_cached_doc` for masters and settings that rarely change.
- Add `search_index` to fields you filter on (see `frappe-doctypes`).
- Move work over a few seconds to a background job (see `frappe-background-jobs`).
