---
name: frappe-portal
description: Build public and customer-facing pages on a Frappe site - www/ pages with Python context, Web Forms for logged-in or guest data entry, website generators (a page per record), portal menu items, and when to use a Vue SPA with frappe-ui instead. Use for customer portals, booking forms, public listings and self-service pages.
---

# Website and portal

Desk (`/app/...`) is for staff. The website side serves everyone else. Pick:

| Need | Use |
|---|---|
| Logged-in customers create or edit their own records with a form | **Web Form** |
| A custom page (landing, dashboard, listing) | **www page** |
| A public page for every record (products, doctors, articles) | **Website generator** |
| An app-like UI with many screens | Vue SPA with `frappe-ui` served from `www/` |

## www pages

Files in `<app>/<app>/www/` map to URLs: `www/doctors/index.html` → `/doctors`,
`www/doctors/index.py` supplies context.

```python
# www/doctors/index.py
import frappe

no_cache = 1   # set when content depends on the user or changes often


def get_context(context):
	context.title = "Our Doctors"
	context.doctors = frappe.get_all(
		"Clinic Doctor",
		filters={"is_active": 1},
		fields=["name", "doctor_name", "specialisation"],
		order_by="doctor_name asc",
	)
```

```html
{% extends "templates/web.html" %}
{% block page_content %}
<h1>{{ title }}</h1>
{% for d in doctors %}
	<div class="card mb-3"><div class="card-body">
		<h5>{{ d.doctor_name }}</h5><p class="text-muted">{{ d.specialisation or "" }}</p>
	</div></div>
{% endfor %}
{% endblock %}
```

- `get_context` runs as the visiting user; `frappe.session.user == "Guest"` when logged out.
  `frappe.get_all` ignores permissions, so only query data that is safe to show that visitor.
- Require login: `if frappe.session.user == "Guest": frappe.throw(_("Log in to continue"), frappe.PermissionError)`.
- Jinja autoescapes output; don't mark user data `| safe`.
- Pages are cached for guests unless `no_cache = 1`.

## Web Forms

A **Web Form** record exposes selected fields of a DocType at `/<route>`. Settings: login required,
allow edit, allow multiple, show list, allow delete, and an optional client script. Logged-in users
see only their own records (matched on `owner`) unless you add permission logic. With
`developer_mode: 1` and **Is Standard**, Frappe writes it to `<module>/web_form/<name>/` so it
ships with the app. Validation still runs in the DocType controller.

For guest submissions (allowed only if "Login Required" is off), add rate limiting and
validation in the controller's `validate`, because the form is open to bots.

## Website generators

Make a DocType render one page per record: set `has_web_view: 1`, `route` field, and
`is_published_field` in the DocType, and subclass `WebsiteGenerator`:

```python
import frappe
from frappe.website.website_generator import WebsiteGenerator


class ClinicDoctor(WebsiteGenerator):
	website = frappe._dict(template="templates/generators/clinic_doctor.html", condition_field="published")
```

Add the template under `templates/generators/`. Pages are public when published.

## Portal menu

Add links to the portal sidebar (`/me`) with `standard_portal_menu_items` in hooks.py:

```python
standard_portal_menu_items = [
	{"title": "My Appointments", "route": "/appointments", "reference_doctype": "Clinic Appointment", "role": "Clinic Patient"},
]
```

Portal users are Website Users (no desk access). Give them a role, and give that role the
permissions the portal needs, usually `read` with `if_owner`, or a `has_permission` hook.

## Vue SPA with frappe-ui

For rich apps (like Frappe CRM or Helpdesk), build a Vite + Vue 3 app with `frappe-ui` in a
`frontend/` folder. Serve the build from `www/<app>.html` and call whitelisted methods with
`createResource`. This is a bigger investment; use it when Desk and Web Forms are not enough.
Follow the structure of an existing Frappe app that does this (e.g. `frappe/crm`) rather than
inventing one.
