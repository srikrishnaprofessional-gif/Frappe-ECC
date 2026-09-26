# Frappe Security & Access Control Rules

## 1. SQL Injection Prevention
- **CRITICAL**: Never concatenate or format strings into `frappe.db.sql()`!
  ```python
  # DEADLY VULNERABLE:
  frappe.db.sql(f"SELECT name FROM `tabAsset` WHERE serial_no = '{user_input}'")
  frappe.db.sql("SELECT name FROM `tabAsset` WHERE serial_no = '%s'" % user_input)

  # SAFE & ENFORCED:
  frappe.db.sql(
      "SELECT name FROM `tabAsset` WHERE serial_no = %(serial)s AND status = %(status)s",
      values={"serial": user_input, "status": "In Use"},
      as_dict=True
  )
  ```

## 2. Authorization & Whitelist Guardrails
- Every method annotated with `@frappe.whitelist()` is exposed to HTTP requests.
- Unless explicitly designed as a public signup or contact endpoint, verify permissions:
  ```python
  @frappe.whitelist()
  def sensitive_operation(docname):
      frappe.has_permission("Asset", "write", docname, throw=True)
      # or:
      frappe.only_for(["System Manager", "Auditor"])
  ```
- If `allow_guest=True` is used, enforce strict rate-limiting:
  ```python
  @frappe.whitelist(allow_guest=True)
  @frappe.rate_limit(limit=5, seconds=60)
  def public_inquiry(email, message):
      # sanitize and validate
  ```

## 3. ORM Permission Checks
- Note that `frappe.get_all()` bypasses user permissions by default! If querying data on behalf of a regular user, use `frappe.get_list()` or pass `ignore_permissions=False`:
  ```python
  # Respects user permissions and user permission conditions:
  assets = frappe.get_list("Asset", filters={"company": user_company})
  ```

## 4. XSS & Jinja Template Safety
- Frappe Jinja templates auto-escape HTML by default. Never use `{{ var | safe }}` on untrusted user inputs.
- When generating emails or PDF HTML with dynamic content, wrap inputs with `frappe.utils.escape_html()`.
