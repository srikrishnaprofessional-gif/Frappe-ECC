---
name: frappe-security-review
description: Review a Frappe app for security problems - run Frappe Shield, then check whitelisted APIs, guest endpoints, permission bypasses, SQL injection, XSS, file uploads, secrets and data exposure. Use before releasing an app, when reviewing a pull request, or when asked whether Frappe code is secure.
---

# Security review

## 1. Run Frappe Shield

```bash
frappe-ecc shield <app_path>                 # human-readable; exits 1 on HIGH or CRITICAL
frappe-ecc shield <app_path> --json          # for tools
frappe-ecc shield <app_path> --fail-on medium
```

It flags: SQL built with f-strings/`%`/`.format()`/`+`, `frappe.db.commit()` in controller hooks,
guest APIs without `@rate_limit`, `ignore_permissions=True` in whitelisted APIs, direct
`docstatus` assignment, `eval`/`exec`, `subprocess(shell=True)`, hard-coded secrets, queries in
loops, swallowed exceptions, and JS `eval`/unescaped `innerHTML`. A finding on a line marked
`# shield: ignore` is skipped. Every ignore needs a reason in the code.

Shield finds patterns. It does not prove code is safe, so do the manual review below too.

## 2. Manual checklist

**Every `@frappe.whitelist()` function**
- Who can call it? Any logged-in user can, unless it checks. Look for `check_permission`,
  `has_permission(..., throw=True)`, `only_for`, or `get_list`.
- Does it take a DocType or fieldname from the caller (`frappe.get_doc(doctype, name)`)? Then the
  caller can read any DocType. Allow-list the values.
- State-changing functions should set `methods=["POST"]`.
- Does it return more fields than the caller should see (password hashes, other users' data)?

**Guest access (`allow_guest=True`, www pages, Web Forms)**
- Rate limited, inputs validated (types, length, formats), minimal `ignore_permissions`.
- Nothing returns records the guest didn't create. Don't reveal whether an email or record exists.

**Permissions**
- DocType permission rules match the intended roles; no `All`/`Guest` read on business data.
- `permission_query_conditions` and `has_permission` agree (list and form show the same records).
- `frappe.get_all` / `frappe.db.sql` in user-facing code are filtered for the user.
- Sensitive fields use `permlevel` > 0 and Password fields, not Data.

**Injection and XSS**
- All SQL parameterised or in `frappe.qb`. Identifiers (table/column names) from input are
  allow-listed, since they can't be parameterised.
- Jinja: no `| safe` on user data. JS: no `innerHTML`/`$(...).html()` with unescaped values; use
  `frappe.utils.escape_html`.
- `frappe.safe_eval` only for expressions from trusted admins; never `eval`.

**Files**
- Attach fields that must stay private use `is_private` files; check who can read the parent document.
- Validate file type and size for uploads from portals.

**Secrets and config**
- API keys in Password fields or `site_config.json`; never in code, fixtures or git history.
- No debug output of `frappe.conf` or request headers.

**Data integrity**
- No `frappe.db.commit()` in request code; no direct `docstatus` writes; `db_set` only for fields
  that need no validation.

## 3. Report

For each problem give: file:line, what an attacker or wrong user can do (concrete scenario),
severity, and the fix. Separate confirmed problems from ones that need a closer look. Don't report
style issues as security issues.
