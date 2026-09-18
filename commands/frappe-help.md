# /frappe:help

**Purpose**: Display the quick-reference cheat sheet for all Frappe ECC agents, skills, and slash commands.

## Frappe ECC Commands Quick Reference
| Command | Purpose | Agent Involved |
|---|---|---|
| `/frappe:plan "<feature>"` | Architect a new feature or app | frappe-planner |
| `/frappe:doctype "<name>"` | Scaffold DocType schema, py, js & test | frappe-doctype-design |
| `/frappe:controller "<name>"` | Implement DocType controller lifecycle | frappe-backend-builder |
| `/frappe:client-script "<name>"` | Create Desk UI form script | frappe-desk-builder |
| `/frappe:hook [event/cron]` | Wire events or cron jobs in `hooks.py` | frappe-hooks-and-events |
| `/frappe:api "<name>"` | Create whitelisted REST API endpoint | frappe-api-integrator |
| `/frappe:test "<name>"` | Scaffold & run tests with FrappeTestCase | frappe-tdd-guide |
| `/frappe:review [file]` | Fresh-context review for anti-patterns | frappe-code-reviewer |
| `/frappe:security [path]` | Scan code for SQLi, permission flaws & XSS | frappe-security-reviewer |
| `/frappe:patch "<desc>"` | Generate idempotent DB migration patch | frappe-migration-patcher |
| `/frappe:report "<name>"` | Scaffold Script Report (Python + JS) | frappe-report-builder |
| `/frappe:bench [task]` | Run & diagnose bench commands | frappe-bench-devops |
| `/frappe:help` | Display this command summary | - |
