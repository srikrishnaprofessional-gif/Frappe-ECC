# /frappe:api

**Purpose**: Generate a secure, whitelisted Frappe REST API endpoint with parameter validation, permission checks, and rate-limiting.

## Usage
`/frappe:api "<endpoint name>" [--method GET|POST] [--allow-guest]`

## Execution Workflow
1. Invoke the **frappe-api-integrator** agent.
2. Generate the `@frappe.whitelist()` Python function.
3. If `--allow-guest` is specified, add `@frappe.rate_limit(limit=10, seconds=60)` and input escaping.
4. If authenticated, add `frappe.only_for(["Role Name"])` or `frappe.has_permission(throw=True)`.
5. Return standardized response JSON: `{"status": "success", "data": ...}`.
