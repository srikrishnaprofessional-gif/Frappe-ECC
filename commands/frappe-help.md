# /frappe:help

**Purpose**: Display the master cheat sheet for all 20 Frappe ECC specialist agents, 18 skills, and 20 slash commands.

## Master Commands & Agent Quick Reference

| Command | Purpose | Specialist Agent | Primary Workflow Skill |
|---|---|---|---|
| `/frappe:hld "<feature>"` | Generate High-Level Design (HLD) with C4 diagrams | `frappe-hld-architect` | `frappe-hld-lld-design` |
| `/frappe:lld "<name>"` | Generate Low-Level Design (LLD) with ER & class diagrams | `frappe-lld-designer` | `frappe-hld-lld-design` |
| `/frappe:wireframe "<name>"` | Generate visual ASCII/SVG wireframe layouts | `frappe-wireframe-builder` | `frappe-wireframing-prototyping` |
| `/frappe:prototype "<name>"` | Generate interactive clickable HTML prototype | `frappe-interactive-prototyper` | `frappe-wireframing-prototyping` |
| `/frappe:plan "<feature>"` | Architect feature blueprint & schema taxonomy | `frappe-planner` | `frappe-doctype-design` |
| `/frappe:doctype "<name>"` | Scaffold DocType schema, py, js & test stubs | `frappe-planner` | `frappe-doctype-design` |
| `/frappe:build-e2e "<spec>"` | Turnkey fullstack synthesis (zero placeholders) | `frappe-fullstack-developer` | `frappe-fullstack-scaffolding` |
| `/frappe:controller "<name>"` | Implement DocType controller lifecycle validations | `frappe-backend-builder` | `frappe-orm-and-queries` |
| `/frappe:client-script "<name>"` | Create Desk UI form scripts, dialogs & buttons | `frappe-desk-builder` | `frappe-client-scripts` |
| `/frappe:hook [event/cron]` | Wire events, cron jobs, or class overrides | `frappe-architect` | `frappe-hooks-and-events` |
| `/frappe:api "<name>"` | Create whitelisted REST API endpoint | `frappe-api-integrator` | `frappe-rest-api` |
| `/frappe:test "<name>"` | Scaffold & run tests with FrappeTestCase | `frappe-tdd-guide` | `frappe-testing-tdd` |
| `/frappe:manual-qa "<name>"` | Generate manual test scenarios & QA checklist | `frappe-manual-qa` | `frappe-qa-testing-automation` |
| `/frappe:e2e-test "<name>"` | Generate Playwright automated browser test script | `frappe-automated-tester` | `frappe-qa-testing-automation` |
| `/frappe:review [file]` | Fresh-context review for Frappe anti-patterns | `frappe-code-reviewer` | `frappe-orm-and-queries` |
| `/frappe:security [path]` | Scan code for SQLi, permission flaws & XSS | `frappe-security-reviewer` | `frappe-shield-security-audit` |
| `/frappe:patch "<desc>"` | Generate idempotent DB migration patch | `frappe-migration-patcher` | `frappe-patches-migrations` |
| `/frappe:report "<name>"` | Scaffold Script Report (Python backend + JS frontend) | `frappe-report-builder` | `frappe-reports-and-dashboards` |
| `/frappe:bench [task]` | Run & diagnose bench commands | `frappe-bench-devops` | `frappe-bench-cli` |
| `/frappe:help` | Display this master command summary | All Agents | - |
