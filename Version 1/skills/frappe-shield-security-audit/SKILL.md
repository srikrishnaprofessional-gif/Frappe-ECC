---
name: frappe-shield-security-audit
description: Static code analysis and security auditing rules for identifying vulnerabilities and anti-patterns in Frappe Framework applications.
---

# Frappe Shield Security Audit & Vulnerability Scanner

Frappe Shield is an automated vulnerability detection skill modeled after AgentShield in ECC. It actively flags dangerous coding patterns before deployment.

## 1. High-Risk Security Anti-Patterns
1. **Unparameterized SQL Queries (`frappe.db.sql`)**:
   - Threat: SQL Injection.
   - Dangerous Pattern:
     `frappe.db.sql(f"SELECT ... WHERE id = '{val}'")`
     `frappe.db.sql("SELECT ... WHERE id = '%s'" % val)`
   - Safe Pattern:
     `frappe.db.sql("SELECT ... WHERE id = %(id)s", values={"id": val})`
     Or prefer `frappe.qb`.

2. **Commit Inside Controller Event (`frappe.db.commit()`)**:
   - Threat: Broken transactions, phantom reads, failure to rollback on errors.
   - Rule: Never invoke `frappe.db.commit()` inside `validate()`, `before_save()`, `on_update()`, `on_submit()`, or `on_cancel()`.

3. **Public Whitelist without Rate Limit / Validation (`allow_guest=True`)**:
   - Threat: Unauthenticated Denial of Service / Credential Brute-force / Spam.
   - Rule: Any `@frappe.whitelist(allow_guest=True)` method MUST have `@frappe.rate_limit(limit=X, seconds=Y)` and input sanitation.

4. **Direct Docstatus Manipulation**:
   - Threat: Inconsistent database state and bypass of ledger submission hooks.
   - Rule: Never write `doc.docstatus = 1`. Use `doc.submit()`.

5. **Raw HTML Rendering in Jinja without Escaping**:
   - Threat: Stored XSS.
   - Rule: Do not apply `| safe` filter to fields filled by untrusted users. Use `frappe.utils.escape_html()`.
