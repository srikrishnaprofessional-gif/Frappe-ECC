# 🚀 Frappe ECC (Engineering Coordination Center)
### Turn your AI code editor into a full-stack Frappe & ERPNext engineering team

[![Frappe Framework](https://img.shields.io/badge/Frappe-v14%20%7C%20v15%20%7C%20v16-blue.svg)](https://frappeframework.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security: Frappe Shield](https://img.shields.io/badge/Security-Frappe%20Shield-orange.svg)](#frappe-shield)

**Frappe ECC** is an open-source engineering system for AI code editors (**Antigravity**, **Claude Code**, **Cursor**, **Codex**, **Gemini CLI**) tailored specifically for developers building on the **Frappe Framework** and **ERPNext**.

It covers the complete engineering lifecycle: **HLD/LLD Architecture**, **UI/UX & Wireframing**, **Interactive Clickable Prototyping**, **Turnkey Fullstack Development**, **Manual & Automated Testing (Playwright)**, **Security Auditing**, and **DevOps**.

---

## ⚡ Quick Install

### Antigravity (Recommended)
```bash
./install.sh --profile full --target antigravity
```
*Or on Windows PowerShell:*
```powershell
.\install.ps1 -Profile full -Target antigravity
```

### Claude Code
```bash
./install.sh --profile full --target claude
```

### Cursor
```bash
./install.sh --profile full --target cursor
```

---

## 📊 What's Inside

| Component | Count | Description |
|---|---|---|
| **Agents** | 29 | Autonomous & specialist AI workers: Orchestration, Product Management, HLD, LLD, UI/UX, Wireframing, Prototyping, Fullstack Dev, TDD, Manual QA, Playwright Testing, Self-Healing Debugger, Data Synthesis, RBAC Compliance, Integrations Broker, Print Formats, DevOps, Security, Working SOP Author |
| **Skills** | 18 | Production workflows: HLD/LLD design, Wireframing & Prototyping, QA test automation, Turnkey scaffolding, DocType modeling, QueryBuilder, `hooks.py`, client scripts, REST APIs, permissions, TDD, background jobs, reports, patches, Bench CLI, Frappe UI, Portal |
| **Commands** | 27 | Slash commands: `/frappe:auto`, `/frappe:sop`, `/frappe:heal`, `/frappe:fixtures`, `/frappe:rbac`, `/frappe:print-format`, `/frappe:deploy`, `/frappe:hld`, `/frappe:lld`, `/frappe:wireframe`, `/frappe:prototype`, `/frappe:build-e2e`, `/frappe:manual-qa`, `/frappe:e2e-test`, `/frappe:plan`, `/frappe:doctype`, `/frappe:controller`, `/frappe:test`, `/frappe:security`, `/frappe:bench`, etc. |
| **Rules** | 5 | Always-loaded coding standards: Core architecture, Python backend, Desk JS, Security, and Database optimization |
| **Frappe Shield** | Included | AST-based static security analyzer detecting SQLi in `frappe.db.sql`, `commit()` violations, and unvalidated guest APIs |

---

## 🛠️ The 29 Autonomous & Specialist Agents

| Agent | Responsibility |
|---|---|
| `frappe-autonomous-orchestrator`| Master autonomous director driving prompt-to-production DAG pipelines |
| `frappe-product-manager` | Domain discovery, PRD specification & user story acceptance criteria |
| `frappe-hld-architect` | High-Level Design (HLD) with Mermaid C4 architecture diagrams |
| `frappe-lld-designer` | Low-Level Design (LLD) with Mermaid ER diagrams & state machines |
| `frappe-data-synthesizer` | Domain-accurate seed fixtures (`fixtures/`) & relational test data |
| `frappe-rbac-compliance-guardian`| Role-based access control, Custom DocPerms & permission query filters |
| `frappe-ui-ux-designer` | UI/UX design, desk ergonomics, workspace dashboards, mobile UX |
| `frappe-wireframe-builder` | Visual ASCII, Markdown, and SVG wireframe mockups |
| `frappe-interactive-prototyper`| Clickable interactive single-file HTML/Vue prototypes |
| `frappe-fullstack-developer` | Turnkey end-to-end fullstack feature synthesis without placeholders |
| `frappe-planner` | Architectural blueprinting, DocType taxonomy & build sequence |
| `frappe-backend-builder` | Python DocType controllers, lifecycle hooks & QueryBuilder |
| `frappe-desk-builder` | Desk client scripts, form UI events, dialogs & buttons |
| `frappe-integrations-broker` | Third-party adapters (Stripe, PayPal, WhatsApp Cloud API, S3/GCS) |
| `frappe-print-format-designer` | Print-ready Jinja2 HTML/CSS templates for invoices, slips & QR barcodes |
| `frappe-tdd-guide` | Test-driven development with `FrappeTestCase` unit tests |
| `frappe-manual-qa` | Comprehensive manual test plans, edge-case matrices & sign-off |
| `frappe-automated-tester` | Playwright E2E browser automation & REST API regression tests |
| `frappe-self-healing-debugger` | Automated root-cause isolation & surgical patch repair for test crashes |
| `frappe-code-reviewer` | Fresh-context reviewer detecting Frappe anti-patterns |
| `frappe-security-reviewer` | Security auditing for SQLi, broken access control & XSS |
| `frappe-architect` | System-level design, bench multi-tenancy & RQ queue topology |
| `frappe-bench-devops` | Bench CLI operations, Redis/RQ worker tuning & site repair |
| `frappe-migration-patcher` | Database schema migrations & idempotent `patches.txt` scripts |
| `frappe-report-builder` | Script Reports (Python + JS) & Dashboard Charts |
| `frappe-api-integrator` | REST APIs, webhook listeners & OAuth2 client integration |
| `frappe-release-devops` | CI/CD GitHub Actions workflows, Dockerfiles & Frappe Cloud deployment |
| `frappe-doc-updater` | Auto-documentation for DocTypes, APIs & hooks registries |
| `frappe-working-sop-author` | Visual Working SOPs & operator manuals with embedded UI screenshots, RACI & failsafes |

---

## 🛡️ Frappe Shield Scanner

Run static analysis against any Frappe application:
```bash
python bin/frappe-shield.py path/to/your/frappe_app
```

---

## 📖 Complete Documentation
- **Executive Pitch Deck (Product Presentation)**: [FRAPPE_ECC_PITCH_DECK.md](docs/FRAPPE_ECC_PITCH_DECK.md)
- **Pitch Deck Word Document**: [FRAPPE_ECC_PITCH_DECK.docx](docs/FRAPPE_ECC_PITCH_DECK.docx)
- **Pitch Deck PDF Document**: [FRAPPE_ECC_PITCH_DECK.pdf](docs/FRAPPE_ECC_PITCH_DECK.pdf)
- **Master Setup Guide**: [ECC_Frappe_Complete_Setup_Guide.md](docs/ECC_Frappe_Complete_Setup_Guide.md)
- **Multi-Agent Architecture & Pipeline Spec**: [FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.md](docs/FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.md)
- **Architecture Spec Word Document**: [FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx](docs/FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx)
- **Architecture Spec PDF Document**: [FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf](docs/FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf)
- **Framework Standard Operating Procedure (SOP)**: [FRAPPE_ECC_SOP.md](docs/FRAPPE_ECC_SOP.md)
- **Framework SOP Word Document**: [FRAPPE_ECC_SOP.docx](docs/FRAPPE_ECC_SOP.docx)
- **Framework SOP PDF Document**: [FRAPPE_ECC_SOP.pdf](docs/FRAPPE_ECC_SOP.pdf)
- **Project Working SOP with Screenshots (Equipment Loan)**: [WORKING_SOP_EQUIPMENT_LOAN.md](test_project/docs/WORKING_SOP_EQUIPMENT_LOAN.md)
- **Project Working SOP Word Document**: [WORKING_SOP_EQUIPMENT_LOAN.docx](test_project/docs/WORKING_SOP_EQUIPMENT_LOAN.docx)
- **Project Working SOP PDF Document**: [WORKING_SOP_EQUIPMENT_LOAN.pdf](test_project/docs/WORKING_SOP_EQUIPMENT_LOAN.pdf)
