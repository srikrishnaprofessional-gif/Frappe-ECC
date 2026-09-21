# 🚀 Frappe Autonomous Enterprise Studio (Frappe AES / ECC v2.0)
### The Complete Autonomous No-Code & Low-Code AI Operating Platform for Modern Enterprises
#### Built on the Frappe Framework & ERPNext Engine — 52 Specialized Autonomous Agents & 50 Commands

[![Frappe Framework](https://img.shields.io/badge/Frappe-v14%20%7C%20v15%20%7C%20v16-blue.svg)](https://frappeframework.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security: Frappe Shield](https://img.shields.io/badge/Security-Frappe%20Shield-orange.svg)](#frappe-shield)
[![Autonomous Agents](https://img.shields.io/badge/Agents-52%20Specialists-teal.svg)](#the-52-autonomous-specialist-agents)
[![Slash Commands](https://img.shields.io/badge/Commands-50%20Commands-indigo.svg)](#complete-roster-of-50-slash-commands)

**Frappe Autonomous Enterprise Studio (Frappe AES)** is a commercial-grade, full **No-Code & Low-Code AI Operating Platform** designed for AI code editors (**Antigravity**, **Claude Code**, **Cursor**, **Codex**, **Gemini CLI**).

It enables non-technical founders, operations managers, and enterprise IT leaders to turn **natural language prompts, legacy Excel spreadsheets, spoken voice commands, or scanned paper forms** into mission-critical, enterprise-grade ERP and business software in **under 5 minutes** — with **$0 per-seat licensing fees**, zero vendor lock-in, and 100% data sovereignty.

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

## 📊 Platform Architecture Matrix

| Component | Count | Description |
|---|---|---|
| **Agents** | 52 | Autonomous & specialist AI workers covering all 8 enterprise pillars: Ingestion, Architecture, Logic, BI Analytics, Multi-Experience, Fullstack Dev, Security/GDPR, and SaaS Support |
| **Skills** | 18 | Production workflows: HLD/LLD design, Wireframing & Prototyping, QA test automation, Turnkey scaffolding, DocType modeling, QueryBuilder, `hooks.py`, client scripts, REST APIs, permissions, TDD, background jobs, reports, patches, Bench CLI, Frappe UI, Portal |
| **Commands** | 50 | Comprehensive slash commands for instant 1-line execution: `/frappe:auto`, `/frappe:prompt-to-app`, `/frappe:import-sheets`, `/frappe:voice`, `/frappe:ocr`, `/frappe:workflow`, `/frappe:dashboard`, `/frappe:chat-data`, `/frappe:sop`, `/frappe:saas`, etc. |
| **Rules** | 5 | Always-loaded coding standards: Core architecture, Python backend, Desk JS, Security, and Database optimization |
| **Frappe Shield** | Included | AST-based static security analyzer detecting SQLi in `frappe.db.sql`, `commit()` violations, and unvalidated guest APIs |

---

## 🏛️ The 8 Enterprise Pillars & 52 Autonomous Agents

### Pillar 1: No-Code Front Door & Ingestion (5 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-autonomous-orchestrator` | Master autonomous director driving prompt-to-production DAG pipelines |
| `frappe-prompt-to-app-builder` | 1-prompt natural-language-to-complete-app autonomous synthesizer |
| `frappe-excel-csv-app-converter` | Converts spreadsheets & CSVs into normalized 3NF DocTypes & seeds records |
| `frappe-voice-command-copilot` | Audio-to-action engine for voice navigation, spoken record updates & audio KPI briefings |
| `frappe-ocr-document-ingestor` | Vision/OCR engine extracting structured data from paper invoices, receipts & PDFs |

### Pillar 2: Product Architecture & System Design (5 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-product-manager` | Domain discovery, PRD specification & user story acceptance criteria |
| `frappe-hld-architect` | High-Level Design (HLD) with Mermaid C4 architecture diagrams |
| `frappe-lld-designer` | Low-Level Design (LLD) with Mermaid ER diagrams & state machines |
| `frappe-planner` | Architectural blueprinting, DocType taxonomy & build sequence |
| `frappe-architect` | System-level design, bench multi-tenancy & RQ queue topology |

### Pillar 3: Visual Workflows & Omnichannel Automations (6 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-bpmn-visual-workflow-builder` | Visual BPMN 2.0 drag-and-drop state machines & approval hierarchies |
| `frappe-notification-omnichannel-agent` | Real-time alerts across WhatsApp, Twilio SMS, Slack, Email & MS Teams |
| `frappe-cron-scheduler-optimizer` | Visual background job scheduler & Redis RQ worker load balancer |
| `frappe-sla-escalation-manager` | Real-time SLA tracking, breach timers & supervisory escalation chains |
| `frappe-integrations-broker` | Third-party adapters (Stripe, PayPal, WhatsApp Cloud API, S3/GCS) |
| `frappe-api-integrator` | REST APIs, webhook listeners & OAuth2 client integration |

### Pillar 4: Enterprise Analytics, BI & AI Intelligence (5 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-bi-dashboard-synthesizer` | Real-time executive BI workspaces, KPI scorecards & board deck exporter |
| `frappe-natural-language-query-agent` | "Chat with your ERP Data" (Text-to-SQL / QueryBuilder) conversational AI |
| `frappe-predictive-ai-forecaster` | ML time-series demand forecasting, cash flow prediction & anomaly detection |
| `frappe-audit-trail-forensic-inspector` | Tamper-proof audit logger, fraud detector & Segregation of Duties (SoD) scanner |
| `frappe-report-builder` | Script Reports (Python + JS) & Dashboard Charts |

### Pillar 5: UI/UX, Multi-Experience & Theming (8 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-ui-ux-designer` | UI/UX design, desk ergonomics, workspace dashboards, mobile UX |
| `frappe-wireframe-builder` | Visual ASCII, Markdown, and SVG wireframe mockups |
| `frappe-interactive-prototyper` | Clickable interactive single-file HTML/Vue prototypes |
| `frappe-white-label-branding-themer` | 1-click corporate visual identity customizer (logos, palettes, typography, custom CSS) |
| `frappe-mobile-app-pwa-generator` | Mobile Progressive Web App (PWA) with offline sync & camera barcode scanner |
| `frappe-portal-ecommerce-builder` | Customer and supplier self-service web portals, catalogs & extranets |
| `frappe-accessibility-wcag-compliance` | WCAG 2.1 AA accessibility auditing & screen reader optimization |
| `frappe-print-format-designer` | Print-ready Jinja2 HTML/CSS templates for invoices, slips & QR barcodes |

### Pillar 6: Turnkey Development & Autonomous Healing (6 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-fullstack-developer` | Turnkey end-to-end fullstack feature synthesis without placeholders |
| `frappe-backend-builder` | Python DocType controllers, lifecycle hooks & QueryBuilder |
| `frappe-desk-builder` | Desk client scripts, form UI events, dialogs & buttons |
| `frappe-data-synthesizer` | Domain-accurate seed fixtures (`fixtures/`) & relational test data |
| `frappe-migration-patcher` | Database schema migrations & idempotent `patches.txt` scripts |
| `frappe-self-healing-debugger` | Automated root-cause isolation & surgical patch repair for test crashes |

### Pillar 7: Enterprise QA, Security & Governance (7 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-tdd-guide` | Test-driven development with `FrappeTestCase` unit tests |
| `frappe-manual-qa` | Comprehensive manual test plans, edge-case matrices & sign-off |
| `frappe-automated-tester` | Playwright E2E browser automation & REST API regression tests |
| `frappe-code-reviewer` | Fresh-context reviewer detecting Frappe anti-patterns |
| `frappe-security-reviewer` | Security auditing for SQLi, broken access control & XSS |
| `frappe-rbac-compliance-guardian` | Role-based access control, Custom DocPerms & permission query filters |
| `frappe-gdpr-data-privacy-officer` | PII anonymization, GDPR Right-to-be-Forgotten & consent audit logs |

### Pillar 8: Commercial SaaS, Support & Continuous Operations (10 Agents)
| Agent | Responsibility |
|---|---|
| `frappe-saas-multitenancy-orchestrator` | Multi-tenant site provisioning, Stripe subscription tiers & seat metering |
| `frappe-multilingual-localization-agent` | 100+ language localization, auto-translation & RTL layout support |
| `frappe-data-migration-concierge` | Legacy ERP migration wizards (SAP, Odoo, QuickBooks, Zoho, Salesforce) |
| `frappe-interactive-guided-tour-author` | In-app interactive guided walkthroughs (Driver.js / Shepherd.js) |
| `frappe-helpdesk-customer-support-copilot` | 24/7 AI-powered customer support bot trained on system docs & SOPs |
| `frappe-training-video-scriptwriter` | Structured video narration scripts, quizzes & certification rubrics |
| `frappe-working-sop-author` | Visual Working SOPs & operator manuals with embedded UI screenshots |
| `frappe-doc-updater` | Auto-documentation for DocTypes, APIs & hooks registries |
| `frappe-bench-devops` | Bench CLI operations, Redis/RQ worker tuning & site repair |
| `frappe-release-devops` | CI/CD GitHub Actions workflows, Dockerfiles & Frappe Cloud deployment |

---

## ⚡ Complete Roster of 50 Slash Commands

```
/frappe:auto           - Autonomous end-to-end prompt-to-production pipeline
/frappe:prompt-to-app  - Instant 1-prompt application synthesizer
/frappe:import-sheets  - Ingest Excel/CSV and synthesize relational DocTypes
/frappe:voice          - Setup voice commands and spoken audio briefings
/frappe:ocr            - Extract structured data from scanned invoices & paper forms
/frappe:workflow       - Visual BPMN state machine & approval hierarchy designer
/frappe:notify         - Setup WhatsApp, SMS, Slack, Email & Teams notifications
/frappe:cron           - Visual background job scheduler & queue load balancer
/frappe:sla            - Setup real-time SLA tracking, countdowns & tier escalations
/frappe:dashboard      - Build executive BI workspaces & KPI scorecards
/frappe:chat-data      - Natural language conversational query engine
/frappe:predict        - Train ML models for demand forecasting & risk scoring
/frappe:audit          - Forensic audit, fraud detection & SoD verification
/frappe:white-label    - 1-click corporate visual identity customizer
/frappe:pwa            - Package mobile Progressive Web App with camera barcode scanner
/frappe:portal         - Customer & supplier self-service web portal builder
/frappe:accessibility  - Audit & enforce WCAG 2.1 AA accessibility standards
/frappe:gdpr           - Setup PII encryption & GDPR Right-to-be-Forgotten workflows
/frappe:saas           - Multi-tenant SaaS subscription monetization & Stripe billing
/frappe:i18n           - Localize application into 100+ languages & RTL layouts
/frappe:migrate        - Legacy ERP data migration wizard (SAP, Odoo, etc.)
/frappe:tour           - In-app interactive guided walkthrough tour author
/frappe:helpdesk       - Deploy 24/7 AI customer support copilot
/frappe:training       - Generate video scripts, quizzes & operator certifications
/frappe:sop            - Author visual Working SOPs with annotated UI screenshots
/frappe:hld            - High-Level Design (HLD) architecture with Mermaid C4
/frappe:lld            - Low-Level Design (LLD) schemas & state machines
/frappe:wireframe      - Generate visual ASCII & SVG wireframe mockups
/frappe:prototype      - Generate clickable standalone HTML/Vue prototype
/frappe:build-e2e      - Turnkey fullstack feature synthesis without placeholders
/frappe:manual-qa      - Manual test plans & edge-case test matrices
/frappe:e2e-test       - Playwright automated browser test suite execution
/frappe:heal           - Self-healing test debugger & surgical patch fixer
/frappe:plan           - Architectural blueprinting & build sequence
/frappe:doctype        - Scaffold DocType schemas & controllers
/frappe:controller     - Python backend controller logic & QueryBuilder
/frappe:client-script  - Desk client scripts & form UI dialogs
/frappe:fixtures       - Generate seed data & domain-accurate test records
/frappe:rbac           - Custom DocPerms & permission query filters
/frappe:print-format   - Jinja2 print formats, vouchers & QR barcodes
/frappe:api            - REST APIs & webhook endpoints
/frappe:report         - Script Reports & Dashboard Charts
/frappe:hook           - Configure hooks.py events & cron schedules
/frappe:patch          - Idempotent database schema migration patches
/frappe:review         - Fresh-context code review for Frappe anti-patterns
/frappe:security       - Static security scan for SQLi & access control
/frappe:test           - Unit tests with FrappeTestCase
/frappe:bench          - Bench CLI site operations & health diagnostics
/frappe:deploy         - GitHub Actions CI/CD & cloud deployment
/frappe:help           - Interactive command reference & help index
```

---

## 🛡️ Frappe Shield Scanner

Run static analysis against any Frappe application:
```bash
python bin/frappe-shield.py path/to/your/frappe_app
```

---

### Master Executive Deliverables & System Specifications
- **Master Executive Deliverables Report**: [FRAPPE_AES_MASTER_PROJECT_DELIVERABLES_REPORT.md](docs/FRAPPE_AES_MASTER_PROJECT_DELIVERABLES_REPORT.md)
- **Master High-Level Design (HLD)**: [FRAPPE_AES_HLD_ARCHITECTURE.md](docs/FRAPPE_AES_HLD_ARCHITECTURE.md)
- **Master Low-Level Design (LLD)**: [FRAPPE_AES_LLD_SPECIFICATION.md](docs/FRAPPE_AES_LLD_SPECIFICATION.md)
- **Commercial Pitch Deck (Investor & Enterprise)**: [FRAPPE_AES_COMMERCIAL_PITCH_DECK.md](docs/FRAPPE_AES_COMMERCIAL_PITCH_DECK.md)
- **Simple English Non-Tech Project Report**: [FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.md](docs/FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.md)
- **Simple English Report Word Document**: [FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.docx](docs/FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.docx)
- **Simple English Report PDF Document**: [FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.pdf](docs/FRAPPE_AES_SIMPLE_ENGLISH_EXECUTIVE_REPORT.pdf)

### Interactive Prototype & Native Installers
- **Interactive Working Prototype Studio**: [studio/index.html](studio/index.html)
- **Windows 1-Click Desktop Launcher**: [Launch_FrappeAES_Studio.bat](installers/windows/Launch_FrappeAES_Studio.bat)
- **Windows Desktop Shortcut Installer**: [Install_FrappeAES_Shortcut.ps1](installers/windows/Install_FrappeAES_Shortcut.ps1)
- **iOS 1-Tap Safari Installation Guide**: [IOS_INSTALLATION_GUIDE.md](installers/ios/IOS_INSTALLATION_GUIDE.md)
- **Apple iOS WebClip Profile**: [FrappeAES.mobileconfig](installers/ios/FrappeAES.mobileconfig)
- **iOS PWA Manifest**: [manifest.json](installers/ios/manifest.json)

### Commercial Product & Strategy
- **Commercial Product Specification**: [FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.md](docs/FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.md)
- **Commercial Product Spec Word Document**: [FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.docx](docs/FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.docx)
- **Commercial Product Spec PDF Document**: [FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.pdf](docs/FRAPPE_NO_CODE_COMMERCIAL_PRODUCT_SPEC.pdf)
- **Executive Pitch Deck**: [FRAPPE_ECC_PITCH_DECK.md](docs/FRAPPE_ECC_PITCH_DECK.md)
- **Pitch Deck Word Document**: [FRAPPE_ECC_PITCH_DECK.docx](docs/FRAPPE_ECC_PITCH_DECK.docx)
- **Pitch Deck PDF Document**: [FRAPPE_ECC_PITCH_DECK.pdf](docs/FRAPPE_ECC_PITCH_DECK.pdf)

### Multi-Agent Architecture & Engineering
- **Multi-Agent Architecture & Pipeline Spec**: [FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.md](docs/FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.md)
- **Architecture Spec Word Document**: [FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx](docs/FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.docx)
- **Architecture Spec PDF Document**: [FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf](docs/FRAPPE_ECC_AGENT_ARCHITECTURE_AND_PIPELINE.pdf)
- **Master Setup Guide**: [ECC_Frappe_Complete_Setup_Guide.md](docs/ECC_Frappe_Complete_Setup_Guide.md)

### Framework SOP & Visual Working SOPs
- **Framework Standard Operating Procedure (SOP)**: [FRAPPE_ECC_SOP.md](docs/FRAPPE_ECC_SOP.md)
- **Framework SOP Word Document**: [FRAPPE_ECC_SOP.docx](docs/FRAPPE_ECC_SOP.docx)
- **Framework SOP PDF Document**: [FRAPPE_ECC_SOP.pdf](docs/FRAPPE_ECC_SOP.pdf)
- **Project Working SOP with Screenshots (Equipment Loan)**: [WORKING_SOP_EQUIPMENT_LOAN.md](test_project/docs/WORKING_SOP_EQUIPMENT_LOAN.md)
- **Project Working SOP Word Document**: [WORKING_SOP_EQUIPMENT_LOAN.docx](test_project/docs/WORKING_SOP_EQUIPMENT_LOAN.docx)
- **Project Working SOP PDF Document**: [WORKING_SOP_EQUIPMENT_LOAN.pdf](test_project/docs/WORKING_SOP_EQUIPMENT_LOAN.pdf)
