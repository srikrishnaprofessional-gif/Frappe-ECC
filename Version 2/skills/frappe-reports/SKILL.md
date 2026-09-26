---
name: frappe-reports
description: Build Frappe reports and dashboards - Script Reports (Python execute + JS filters), Query Reports, Report Builder, columns and formatting, charts and summary cards, Number Cards, Dashboard Charts and Workspaces. Use when a user needs tables, totals, KPIs or charts over app data.
---

# Reports and dashboards

Pick the simplest option that works:

| Need | Use |
|---|---|
| Filter and group one DocType's fields | **Report Builder** (saved from any list view, no code) |
| Fixed SQL with simple filters | **Query Report** |
| Joins, calculations, permissions logic, charts | **Script Report** |
| A single KPI tile | **Number Card** |
| A chart over time or by group | **Dashboard Chart** |

## Script Report

Files live in `<app>/<module>/report/<report_name>/`: `__init__.py`, `<report_name>.json`,
`<report_name>.py`, `<report_name>.js`. The easiest way to create them is on a site with
`developer_mode: 1`: create a **Report** with type Script Report, Is Standard = Yes, module set to
your module. Frappe writes the files, then you fill them in.

`<report_name>.json` (the record Frappe syncs on migrate):

```json
{
 "doctype": "Report",
 "name": "Doctor Revenue",
 "report_name": "Doctor Revenue",
 "report_type": "Script Report",
 "ref_doctype": "Clinic Appointment",
 "module": "Clinic",
 "is_standard": "Yes",
 "add_total_row": 1,
 "roles": [{"role": "System Manager"}, {"role": "Clinic Doctor"}]
}
```

Users need read access to `ref_doctype` **and** one of `roles` to open it.

`<report_name>.py`:

```python
import frappe
from frappe import _
from frappe.query_builder.functions import Count, Sum


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"fieldname": "doctor", "label": _("Doctor"), "fieldtype": "Link", "options": "Clinic Doctor", "width": 200},
		{"fieldname": "visits", "label": _("Visits"), "fieldtype": "Int", "width": 100},
		{"fieldname": "revenue", "label": _("Revenue"), "fieldtype": "Currency", "width": 140},
	]
	data = get_data(filters)
	chart = {
		"data": {"labels": [d.doctor for d in data], "datasets": [{"name": _("Revenue"), "values": [d.revenue for d in data]}]},
		"type": "bar",
	}
	summary = [{"label": _("Total Revenue"), "value": sum(d.revenue or 0 for d in data), "datatype": "Currency", "indicator": "Green"}]
	return columns, data, None, chart, summary


def get_data(filters):
	Apt = frappe.qb.DocType("Clinic Appointment")
	query = (
		frappe.qb.from_(Apt)
		.select(Apt.doctor, Count(Apt.name).as_("visits"), Sum(Apt.fee).as_("revenue"))
		.where(Apt.docstatus == 1)
		.where(Apt.appointment_date.between(filters.from_date, filters.to_date))
		.groupby(Apt.doctor)
	)
	if filters.doctor:
		query = query.where(Apt.doctor == filters.doctor)
	return query.run(as_dict=True)
```

`execute` returns `columns, data` and optionally `message, chart, report_summary`.

`<report_name>.js`:

```javascript
frappe.query_reports["Doctor Revenue"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_start() },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_end() },
		{ fieldname: "doctor", label: __("Doctor"), fieldtype: "Link", options: "Clinic Doctor" },
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "revenue" && data?.revenue > 100000) value = `<b>${value}</b>`;
		return value;
	},
};
```

Rules:
- Script reports query with `frappe.qb` or `frappe.get_all`, which **ignore** user permissions.
  If users must only see their own rows, filter explicitly, or use `frappe.get_list`.
- Parameterise every filter value (qb does this; with raw SQL, pass a values dict).
- Heavy reports: set `prepared_report: 1` in the JSON so they run in the background and cache the result.
- Test `execute()` directly in a unit test with fixed filters.

## Query Report

Same folder and JSON with `"report_type": "Query Report"` and a `query` field. Filters from the JS
file are available as `%(from_date)s`. Use it only for simple SQL; switch to a Script Report as
soon as logic appears.

## Number Cards, Dashboard Charts, Workspaces

- **Number Card**: type Document Type (count/sum/avg of a field with filters), Report (a report's
  summary value) or Custom (a whitelisted method returning `{"value": ..., "fieldtype": ...}`).
- **Dashboard Chart**: Count, Sum, Average or Group By over a DocType, with a time series based on
  a date field; or a Report chart; or a Custom whitelisted source.
- **Workspace**: the Desk page that holds shortcuts, cards and charts for a module.

With `developer_mode: 1`, set these records to standard (`is_standard: 1`, `module` set) and
Frappe writes them into `<module>/number_card/`, `<module>/dashboard_chart/` and
`<module>/workspace/`, so they ship with the app. Otherwise export them as fixtures.
