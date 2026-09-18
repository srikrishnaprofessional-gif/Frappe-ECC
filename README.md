# 🚀 Frappe ECC (Engineering Coordination Center)
### Turn your AI code editor into a full-stack Frappe & ERPNext engineering team

[![Frappe Framework](https://img.shields.io/badge/Frappe-v14%20%7C%20v15%20%7C%20v16-blue.svg)](https://frappeframework.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security: Frappe Shield](https://img.shields.io/badge/Security-Frappe%20Shield-orange.svg)](#frappe-shield)

**Frappe ECC** is an open-source engineering system for AI code editors (**Antigravity**, **Claude Code**, **Cursor**, **Codex**, **Gemini CLI**) tailored specifically for developers building on the **Frappe Framework** and **ERPNext**.

---

## ⚡ Quick Install

### Antigravity (Recommended)
```bash
./install.sh --profile minimal --target antigravity
```
*Or on Windows PowerShell:*
```powershell
.\install.ps1 -Profile minimal -Target antigravity
```

### Claude Code
```bash
./install.sh --profile minimal --target claude
```

### Cursor
```bash
./install.sh --profile minimal --target cursor
```

---

## 📊 What's Inside

| Component | Count | Description |
|---|---|---|
| **Agents** | 12 | Specialist AI workers: planning, backend controllers, desk UI, TDD, code review, security, DevOps, migrations, and reporting |
| **Skills** | 14 | Production-grade workflows: DocType modeling, QueryBuilder, `hooks.py`, client scripts, REST APIs, permissions, TDD, background jobs |
| **Commands** | 13 | Slash commands: `/frappe:plan`, `/frappe:doctype`, `/frappe:controller`, `/frappe:test`, `/frappe:security`, `/frappe:bench` |
| **Rules** | 5 | Always-loaded coding standards: Core architecture, Python backend, Desk JS, Security, and Database optimization |
| **Frappe Shield** | Included | AST-based static security analyzer detecting SQLi in `frappe.db.sql`, `commit()` violations, and unvalidated guest APIs |

---

## 🛠️ Key Slash Commands

- `/frappe:plan "<feature>"` — Architect a new Frappe feature or app with full DocType schema blueprints.
- `/frappe:doctype "<Name>"` — Scaffold complete `.json`, `.py`, `.js`, and `test_*.py` files.
- `/frappe:controller "<Name>"` — Implement controller lifecycle hooks (`validate`, `on_submit`).
- `/frappe:client-script "<Name>"` — Generate reactive Desk UI form scripts and custom dialogs.
- `/frappe:hook [event|cron]` — Wire events or cron schedules in `hooks.py`.
- `/frappe:api "<name>"` — Create secure `@frappe.whitelist()` endpoints.
- `/frappe:test "<Name>"` — Scaffold unit tests with `FrappeTestCase`.
- `/frappe:review [path]` — Fresh-context code reviewer checking for Frappe anti-patterns.
- `/frappe:security [path]` — Audit code for SQL injection, permission bypass, and XSS.
- `/frappe:patch "<desc>"` — Generate safe, idempotent database migration patch in `patches.txt`.
- `/frappe:bench [task]` — Run and troubleshoot bench commands and site issues.
- `/frappe:help` — Show command quick reference.

---

## 🛡️ Frappe Shield Scanner

Run static analysis against any Frappe application:
```bash
python bin/frappe-shield.py path/to/your/frappe_app
```

Detects:
- SQL injection in `frappe.db.sql()`
- Accidental `frappe.db.commit()` inside controller events
- Missing rate limits on public `@frappe.whitelist(allow_guest=True)` APIs
- Direct `docstatus = 1` assignment
- N+1 query bottlenecks

---

## 📖 Complete Documentation
Read the complete guide: [ECC_Frappe_Complete_Setup_Guide.md](docs/ECC_Frappe_Complete_Setup_Guide.md)
