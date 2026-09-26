---
name: frappe-rest-api
description: Architectural patterns for building secure, high-performance REST APIs in Frappe using @frappe.whitelist(), token auth, and rate limiting.
---

# Frappe REST API Design & Implementation

## 1. Whitelisted Methods Pattern
Expose secure endpoints with `@frappe.whitelist()`:
```python
import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def register_device(device_uid: str, device_type: str, metadata: dict = None):
    """
    POST /api/method/your_app.api.devices.register_device
    Headers:
        Authorization: token <api_key>:<api_secret>
    """
    # 1. Permission check
    frappe.only_for(["System Manager", "Device Administrator"])

    # 2. Input validation
    if not device_uid or not device_type:
        frappe.throw(_("Missing required fields: device_uid, device_type"), frappe.ValidationError)

    # 3. Idempotent record lookup or creation
    if frappe.db.exists("Registered Device", device_uid):
        doc = frappe.get_doc("Registered Device", device_uid)
        doc.last_seen = frappe.utils.now_datetime()
        if metadata:
            doc.metadata_json = frappe.as_json(metadata)
        doc.save(ignore_permissions=True)
        return {"status": "updated", "device": doc.name}

    new_device = frappe.get_doc({
        "doctype": "Registered Device",
        "device_uid": device_uid,
        "device_type": device_type,
        "metadata_json": frappe.as_json(metadata or {}),
        "status": "Active",
        "last_seen": frappe.utils.now_datetime()
    })
    new_device.insert(ignore_permissions=True)

    return {
        "status": "created",
        "device_uid": new_device.name,
        "registered_at": str(new_device.creation)
    }
```

## 2. Public / Guest Endpoint with Rate Limiting
```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
@frappe.rate_limit(limit=10, seconds=60)
def submit_public_ticket(reporter_email: str, subject: str, message: str):
    frappe.utils.validate_email_address(reporter_email, throw=True)
    
    ticket = frappe.get_doc({
        "doctype": "Support Ticket",
        "reporter_email": reporter_email,
        "subject": frappe.utils.escape_html(subject),
        "message": frappe.utils.escape_html(message),
        "source": "Web Form"
    })
    ticket.insert(ignore_permissions=True)
    return {"ticket_id": ticket.name}
```

## 3. Standard HTTP Responses & Status Codes
- Success: Return dictionary or list directly. Frappe automatically wraps in `{"message": ...}` with HTTP 200.
- Custom HTTP status:
  ```python
  frappe.response["http_status_code"] = 201
  ```
- Error:
  ```python
  frappe.throw(_("Asset is not available for check-out"), exc=frappe.ValidationError)
  # Automatically returns HTTP 417 / 500 with {"exc": "...", "_server_messages": "..."}
  ```
