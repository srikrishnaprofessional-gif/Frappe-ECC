# /frappe:security

**Purpose**: Run a comprehensive security audit on Frappe code, identifying SQL injection, broken access control, XSS, and unvalidated APIs.

## Usage
`/frappe:security [directory or app]`

## Execution Workflow
1. Invoke the **frappe-security-reviewer** agent.
2. Execute the AST-based static scanner `bin/frappe-shield.py` on the target code.
3. Review:
   - String concatenation in `frappe.db.sql()`.
   - Missing role or doc permission checks on `@frappe.whitelist()` endpoints.
   - `allow_guest=True` endpoints without rate limiting.
   - Jinja templates applying `| safe` to untrusted variables.
4. Output structured vulnerability findings with exploit vectors and fixes.
