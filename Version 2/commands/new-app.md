---
description: Build a new Frappe app from a requirements description: spec, review, generate, verify on a real site, implement business logic, test and scan
argument-hint: "<requirements or path to a requirements file>"
---
Build a Frappe app for these requirements:

$ARGUMENTS

Work through these stages in order. Don't skip verification, and don't describe anything as
working unless a command you ran showed it.

## 1. Model
Use the **frappe-architect** agent to produce `<app_name>.spec.json` and `<app_name>.design.md`
from the requirements (if the argument is a file path, read it). Then show the user a short
summary: DocTypes with their kind, the roles, the permission table, the business rules, and the
agent's open questions. **Stop and ask the user to confirm or correct** before generating code.

## 2. Generate
Run `frappe-ecc validate <spec>`, then `frappe-ecc new <spec> --dest <dir> --ci`. Ask the user
where to create it if unclear (default: the current directory). Initialise git in the new app and
commit the generated baseline.

## 3. Verify the skeleton
Find a bench (current directory upwards, or ask) and a **throwaway** site. Never use a
production site. If no site exists, give the user the exact `bench new-site` command to run.
Run `frappe-ecc verify <app_path> --bench <bench> --site <site>`. Fix anything that fails before continuing.

## 4. Implement
For each business rule in the design note, use the **frappe-backend-developer** agent (controllers,
APIs, jobs) and **frappe-frontend-developer** agent (form scripts, list views, print formats), and
**frappe-workflow-designer** / **frappe-report-builder** agents where the design calls for them.
Each rule gets a test. Commit after each working rule.

## 5. Prove it
- `frappe-ecc verify <app_path> --bench <bench> --site <site>`: must print `VERIFIED`.
- `frappe-ecc shield <app_path>`: no HIGH or CRITICAL findings (or each one justified).
- Use the **frappe-code-reviewer** agent on the full app and fix confirmed findings.

## 6. Hand over
Report: what was built (DocTypes, roles, rules), the verify result (tests run/failed), shield
result, anything not done or not verified, and how to install it on another site. Publish to a
git remote only if the user asks, using their existing git credentials. Never put tokens in URLs.
