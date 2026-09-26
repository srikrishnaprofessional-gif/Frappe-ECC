---
name: frappe-print-formats
description: Design Frappe print formats and PDFs - Print Format Builder vs Jinja print formats, doc and child table access, formatting helpers, letterheads, page breaks, wkhtmltopdf vs Chrome PDF generation, and shipping standard print formats in an app. Use for invoices, receipts, labels, certificates and other printable documents.
---

# Print formats

Options, simplest first:
1. **Standard** print view: automatic from the DocType's fields; hide fields with `print_hide`.
2. **Print Format Builder**: drag-and-drop in Desk, no code.
3. **Jinja print format** (`print_format_type: Jinja`, `custom_format: 1`): full HTML/CSS control.

## Jinja format

Context: `doc` (the document), `frappe`, `_` (translate), `letter_head`, `footer`, `no_letterhead`.

```jinja
<div class="print-heading">
	<h2>{{ _("Prescription") }}</h2>
	<div>{{ doc.name }} · {{ doc.get_formatted("appointment_date") }}</div>
</div>

<table class="table table-bordered">
	<tr><th>{{ _("Patient") }}</th><td>{{ doc.patient_name }}</td></tr>
	<tr><th>{{ _("Doctor") }}</th><td>{{ frappe.db.get_value("Clinic Doctor", doc.doctor, "doctor_name") }}</td></tr>
</table>

<table class="table table-bordered">
	<thead><tr><th>#</th><th>{{ _("Medicine") }}</th><th>{{ _("Dosage") }}</th><th class="text-right">{{ _("Days") }}</th></tr></thead>
	<tbody>
	{% for row in doc.prescriptions %}
		<tr>
			<td>{{ row.idx }}</td>
			<td>{{ row.medicine }}</td>
			<td>{{ row.dosage or "" }}</td>
			<td class="text-right">{{ row.days }}</td>
		</tr>
	{% endfor %}
	</tbody>
</table>

<div class="page-break"></div>
```

Rules:
- Format values with `doc.get_formatted("field")` (dates, currency, numbers follow the site's
  settings) or `frappe.format_value(value, {"fieldtype": "Currency"}, currency=doc.currency)`.
- Jinja autoescapes values. Only use `| safe` on HTML you control (e.g. a Text Editor field you trust).
- Put CSS in the print format's `css` field, not inline `<style>` in loops. Use Bootstrap classes
  (`table`, `text-right`, `row`, `col-xs-6`), which the print stylesheet provides.
- Queries in a print format run per print. Keep them few; never query inside a loop over rows.
- `<div class="page-break"></div>` forces a new page.
- Test with **Print → PDF**, not just the HTML preview. PDF rendering differs.

## PDF engine

Frappe renders PDFs with **wkhtmltopdf** by default. It supports only old CSS: no flexbox or
grid, limited web fonts. Use tables for layout. From v16, a print format's **PDF Generator** can
be set to `chrome`, which supports modern CSS. On v15 only wkhtmltopdf is available.

Generate a PDF in code:

```python
pdf = frappe.get_print("Clinic Appointment", name, print_format="Clinic Prescription", as_pdf=True)
frappe.attach_print("Clinic Appointment", name, print_format="Clinic Prescription")  # for email attachments
```

## Ship it with the app

With `developer_mode: 1`, create the Print Format with **Standard = Yes** and your module set.
Frappe writes `<module>/print_format/<name>/<name>.json`, which syncs on migrate. To make it the
default for a DocType, set `default_print_format` in the DocType JSON.

**Letter Head** records (logo, address header/footer) are per site. Create them in setup, or ship
one as a fixture if every site uses the same.
