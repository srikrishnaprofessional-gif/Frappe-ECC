---
name: frappe-api
description: Build and call Frappe REST APIs - @frappe.whitelist methods, /api/resource CRUD, /api/v2, token and OAuth auth, rate limiting, input validation, webhooks and calling external services. Use when exposing endpoints from a Frappe app or integrating it with another system.
---

# APIs and integrations

## Built-in REST (no code needed)

Every DocType is available, subject to the caller's permissions:

| Request | Does |
|---|---|
| `GET /api/resource/Clinic Patient?fields=["name","mobile"]&filters=[["gender","=","Female"]]&limit_page_length=50` | list |
| `GET /api/resource/Clinic Patient/PAT-00001` | read one |
| `POST /api/resource/Clinic Patient` (JSON body) | create |
| `PUT /api/resource/Clinic Patient/PAT-00001` | update |
| `DELETE /api/resource/Clinic Patient/PAT-00001` | delete |
| `GET/POST /api/method/<dotted.path>` | call a whitelisted function |

v15 and later also serve `/api/v2/document/<doctype>` and `/api/v2/method/<path>`.
Authenticate with `Authorization: token <api_key>:<api_secret>` (keys are generated on the User
record), OAuth 2 bearer tokens, or a session cookie from `/api/method/login`.

Prefer these endpoints over custom ones for plain CRUD. They already apply permissions,
validation and controller hooks.

## Whitelisted methods

```python
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit


@frappe.whitelist(methods=["POST"])
def reschedule(appointment: str, new_date: str):
	doc = frappe.get_doc("Clinic Appointment", appointment)
	doc.check_permission("write")                 # raise if the caller may not edit it
	doc.appointment_date = new_date
	doc.save()                                    # runs validate() and permission checks
	return {"name": doc.name, "appointment_date": doc.appointment_date}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60)
def request_callback(mobile: str, name: str):
	if not frappe.utils.validate_phone_number(mobile, throw=False):
		frappe.throw(_("Enter a valid mobile number"))
	frappe.get_doc({"doctype": "Clinic Callback", "mobile": mobile, "patient_name": name[:140]}).insert(
		ignore_permissions=True  # guest may create exactly this record and nothing else
	)
	return {"ok": True}
```

Rules:
- Restrict HTTP methods: state-changing methods take `methods=["POST"]` (or PUT/DELETE).
- Whitelisted methods are callable by any logged-in user. Check permissions inside
  (`doc.check_permission(...)`, `frappe.has_permission(doctype, "read", throw=True)`,
  `frappe.only_for("Role")`) or use `frappe.get_list`, which applies them.
- Type-annotate parameters. Frappe v15+ validates arguments against the annotations.
- Guest methods (`allow_guest=True`) need `@rate_limit`, strict validation, and the narrowest
  possible `ignore_permissions`. Never return other users' data from them.
- Return plain dicts/lists; Frappe wraps them in `{"message": ...}`.
- Raise errors with `frappe.throw`. The HTTP status follows the exception
  (`frappe.PermissionError` → 403, `frappe.DoesNotExistError` → 404, `frappe.ValidationError` → 417).

## Calling from the browser

```javascript
frappe.call({
	method: "clinic_management.api.reschedule",
	args: { appointment: frm.doc.name, new_date },
	freeze: true,
}).then((r) => frappe.show_alert({ message: __("Rescheduled"), indicator: "green" }));

// or, returning a promise of the message:
const res = await frappe.xcall("clinic_management.api.reschedule", { appointment, new_date });
```

## Outbound calls

```python
from frappe.integrations.utils import make_get_request, make_post_request

settings = frappe.get_single("Lab Integration Settings")
data = make_post_request(
	settings.endpoint,
	headers={"Authorization": f"Bearer {settings.get_password('api_token')}"},
	json={"patient": patient_id},
)
```

- Keep credentials in a Single DocType with Password fields (read them with `get_password`) or in
  `site_config.json` (`frappe.conf.get("lab_api_token")`). Never in code.
- Make slow or retry-prone calls in a background job, not in the request (see
  `frappe-background-jobs`). Log failures with `frappe.log_error(title=..., message=...)`.

## Inbound webhooks and outbound Webhook records

- For third-party callbacks, write a guest-allowed POST method. Verify the provider's signature
  header (HMAC) against a secret before trusting the body, and make the handler idempotent,
  because providers retry.
- To notify other systems when documents change, create a **Webhook** record (DocType
  `Webhook`: doctype, event, request URL, JSON body template, optional HMAC secret). Ship it as a
  fixture if the app depends on it.
