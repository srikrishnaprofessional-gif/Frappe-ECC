---
name: frappe-portal-web
description: Designing public websites, customer portals, Jinja template rendering, routing rules, and web forms in Frappe.
---

# Frappe Web Pages & Customer Portals

## 1. Portal Routing in `hooks.py`
Map web routes to custom page generators or Jinja files:
```python
website_route_rules = [
    {"from_route": "/itam/track/<asset_id>", "to_route": "itam_track_asset"},
    {"from_route": "/portal/my-assets", "to_route": "my_assets"}
]
```

## 2. Web Page Controller (`<page_name>.py`)
Context builder for Jinja templates:
```python
import frappe

def get_context(context):
    context.no_cache = 1
    # Check login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    user_email = frappe.session.user
    context.user_name = frappe.utils.get_fullname(user_email)
    context.my_assets = frappe.get_all(
        "Asset Item",
        filters={"assigned_user": user_email},
        fields=["name", "asset_name", "serial_no", "status", "purchase_date"]
    )
```

## 3. Web Page Jinja Template (`<page_name>.html`)
```html
{% extends "templates/web.html" %}

{% block page_content %}
<div class="container py-5">
    <h2 class="mb-4">{{ _("My Assigned Assets") }}</h2>
    <div class="table-responsive">
        <table class="table table-bordered table-hover">
            <thead class="thead-light">
                <tr>
                    <th>{{ _("Asset Name") }}</th>
                    <th>{{ _("Serial Number") }}</th>
                    <th>{{ _("Status") }}</th>
                </tr>
            </thead>
            <tbody>
                {% for asset in my_assets %}
                <tr>
                    <td>{{ asset.asset_name }}</td>
                    <td><code>{{ asset.serial_no }}</code></td>
                    <td><span class="badge badge-success">{{ asset.status }}</span></td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="3" class="text-center text-muted">{{ _("No assets currently assigned to you.") }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```
