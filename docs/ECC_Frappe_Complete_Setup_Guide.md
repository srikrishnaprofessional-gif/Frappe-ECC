# THE COMPLETE FRAPPE ECC SETUP GUIDE
### 20 AI Agents • 18 Skills • 20 Commands • Frappe Shield
**Turn your AI code editor into a full-stack Frappe & ERPNext engineering team**

---

## TABLE OF CONTENTS
1. What is Frappe ECC?
2. What's Inside — The Numbers
3. What Can Frappe ECC Actually Do?
4. Prerequisites
5. Installation — Antigravity (Recommended)
6. Installation — Claude Code & Cursor
7. Getting Started — Your First Commands
8. Key Agents Explained (The Full 20-Agent Catalog)
9. Common Frappe Workflows (HLD/LLD -> Wireframes -> Prototyping -> Turnkey Build -> QA -> Deployment)
10. Token Optimization (Save Money)
11. Troubleshooting & Diagnostics
12. Command Reference & Resources

---

## 1. WHAT IS FRAPPE ECC?

**Frappe ECC** (Frappe Engineering Coordination Center) is an open-source engineering system that transforms your AI code editor — Antigravity, Claude Code, Cursor, Codex, or Gemini CLI — into a coordinated, senior Frappe Framework engineering team.

Frappe Framework is unique. It isn't just Python or JavaScript; it is an opinionated full-stack architecture built on DocTypes, lifecycle controller hooks (`before_insert`, `validate`, `on_submit`), the Frappe ORM and QueryBuilder (`frappe.qb`), Bench CLI, MariaDB/PostgreSQL schemas, Redis queues, and Desk UI scripting (`frappe.ui.form.on`).

**Frappe ECC eliminates common AI mistakes.** It equips your AI assistant with **20 specialist agents**, **18 reusable workflow skills**, **20 slash commands**, and **Frappe Shield** — a dedicated AST static security scanner that catches Frappe anti-patterns before your code hits production.

---

## 2. WHAT'S INSIDE — THE NUMBERS

| Component | Count | What It Does |
|---|---|---|
| **Agents** | 20 | Specialist AI workers: HLD, LLD, UI/UX, Wireframing, Clickable Prototyping, Fullstack Turnkey Dev, Manual QA, Automated Testing (Playwright), Planning, Controllers, Desk UI, TDD, Code Review, Security, DevOps, Migrations, Reporting, APIs, Docs |
| **Skills** | 18 | Reusable workflows: HLD/LLD design, Wireframing & Prototyping, QA testing & Playwright automation, Turnkey scaffolding, DocType modeling, QueryBuilder, `hooks.py`, client scripts, REST APIs, permissions, TDD, background jobs, reports, patches, Bench CLI, Frappe UI, Portal, Security Audit |
| **Commands** | 20 | Slash commands: `/frappe:hld`, `/frappe:lld`, `/frappe:wireframe`, `/frappe:prototype`, `/frappe:build-e2e`, `/frappe:manual-qa`, `/frappe:e2e-test`, `/frappe:plan`, `/frappe:doctype`, `/frappe:controller`, `/frappe:test`, `/frappe:security`, `/frappe:bench`, etc. |
| **Rules** | 5 | Always-loaded coding standards: Core architecture, Python backend, Desk JS, Security, and Database optimization |
| **Frappe Shield** | Included | AST static security analyzer that detects SQLi in `frappe.db.sql`, `commit()` violations, and unvalidated guest endpoints |

---

## 3. WHAT CAN FRAPPE ECC ACTUALLY DO?

### 1. High-Level (HLD) & Low-Level (LLD) Design
The **frappe-hld-architect** and **frappe-lld-designer** create enterprise-grade architecture packages with Mermaid C4 diagrams, container topologies, entity-relationship diagrams (`erDiagram`), controller class diagrams, and state machine transition tables.

### 2. UI/UX, Visual Wireframing & Interactive Prototyping
- The **frappe-ui-ux-designer** ensures Desk form ergonomics, WCAG accessibility, and workspace layout balance.
- The **frappe-wireframe-builder** generates visual ASCII grids, SVG layouts, and Markdown wireframes.
- The **frappe-interactive-prototyper** creates standalone, clickable single-file HTML/Vue prototypes that stakeholders can test in any web browser before committing database migrations.

### 3. Turnkey End-to-End Fullstack Code Synthesis
The **frappe-fullstack-developer** writes complete, zero-placeholder vertical slices: DocType schema JSONs, Python controllers, Desk client scripts, hooks registrations, whitelisted APIs, unit tests, and migration patches in one cohesive pass.

### 4. Comprehensive Manual & Automated Testing (Playwright)
- The **frappe-manual-qa** agent authors test charters, edge-case matrices, and release sign-off checklists.
- The **frappe-automated-tester** writes headless **Playwright** browser tests that click through Frappe Desk forms and validate submission workflows automatically.

### 5. Automated Security & Code Review
The **frappe-security-reviewer** and **Frappe Shield** perform AST-based static scanning, detecting SQL injection, permission bypasses, and illegal `frappe.db.commit()` calls.

---

## 4. PREREQUISITES

| Requirement | Details | Check Command |
|---|---|---|
| **Python** | Version 3.10 or newer | `python --version` |
| **Node.js** | Version 18 or newer | `node --version` |
| **Git** | Recent version | `git --version` |
| **Frappe Bench** | (Optional for site execution) v5.15+ | `bench --version` |
| **Code Editor** | Antigravity, Claude Code (2.1+), Cursor, or Gemini CLI | - |

---

## 5. INSTALLATION — ANTIGRAVITY (RECOMMENDED)

```bash
./install.sh --profile full --target antigravity
```
*Or on Windows PowerShell:*
```powershell
.\install.ps1 -Profile full -Target antigravity
```

---

## 6. INSTALLATION — CLAUDE CODE & CURSOR

### Claude Code
```bash
./install.sh --profile full --target claude
```

### Cursor
```bash
./install.sh --profile full --target cursor
```

---

## 7. GETTING STARTED — YOUR FIRST COMMANDS

| What You Want To Do | Command | What Happens |
|---|---|---|
| **Draft High-Level Architecture** | `/frappe:hld "Asset Tracking System"` | `frappe-hld-architect` generates C4 diagrams & integration topology |
| **Draft Low-Level Specs** | `/frappe:lld "Asset Maintenance"` | `frappe-lld-designer` outputs Mermaid ER diagrams & state machines |
| **Generate Visual Wireframe** | `/frappe:wireframe "Asset Ticket"` | `frappe-wireframe-builder` creates ASCII form & list layout mocks |
| **Build Clickable Prototype** | `/frappe:prototype "Asset Ticket"` | `frappe-interactive-prototyper` generates standalone HTML prototype |
| **Build Feature Turnkey** | `/frappe:build-e2e "Asset Ticket"` | `frappe-fullstack-developer` writes full stack with zero placeholders |
| **Create Manual Test Plan** | `/frappe:manual-qa "Asset Ticket"` | `frappe-manual-qa` generates test case matrix and edge-case charter |
| **Write Automated E2E Tests** | `/frappe:e2e-test "Asset Ticket"` | `frappe-automated-tester` generates Playwright browser test script |
| **Run Security Scan** | `/frappe:security` | Frappe Shield audits code for SQLi and permission bypass |

---

## 8. THE 20 SPECIALIST AGENTS CATALOG

1. **`frappe-hld-architect`**: High-Level Design (HLD) with Mermaid C4 architecture diagrams and scaling strategy.
2. **`frappe-lld-designer`**: Low-Level Design (LLD) with Mermaid ER diagrams, state machines, and API schemas.
3. **`frappe-ui-ux-designer`**: UI/UX design, desk ergonomics, workspace dashboard design, and mobile responsiveness.
4. **`frappe-wireframe-builder`**: Visual ASCII, Markdown, and SVG wireframe layout mockups.
5. **`frappe-interactive-prototyper`**: Clickable interactive single-file HTML/Vue prototypes for stakeholder validation.
6. **`frappe-fullstack-developer`**: Turnkey end-to-end fullstack feature synthesis without placeholders.
7. **`frappe-planner`**: Architectural blueprinting, DocType taxonomy, and execution sequence.
8. **`frappe-architect`**: Enterprise-level architecture, multi-tenant bench topology, and RQ background queues.
9. **`frappe-backend-builder`**: Python DocType controllers, lifecycle hooks, validations, and QueryBuilder.
10. **`frappe-desk-builder`**: Reactive Desk client scripts, form UI events, dialogs, and custom buttons.
11. **`frappe-tdd-guide`**: Test-driven development with `FrappeTestCase` unit tests.
12. **`frappe-manual-qa`**: Comprehensive manual test plans, edge-case matrices, and QA sign-off checklists.
13. **`frappe-automated-tester`**: Playwright browser automation, API regression tests, and CI/CD workflows.
14. **`frappe-code-reviewer`**: Fresh-context reviewer detecting Frappe anti-patterns and performance bottlenecks.
15. **`frappe-security-reviewer`**: Security auditing for SQL injection, broken access control, and XSS.
16. **`frappe-bench-devops`**: Bench CLI operations, Redis/RQ worker tuning, and site diagnostics.
17. **`frappe-migration-patcher`**: Database schema migrations and idempotent `patches.txt` scripts.
18. **`frappe-report-builder`**: Script Reports (Python + JS) and Dashboard Charts.
19. **`frappe-api-integrator`**: REST APIs, webhook listeners, and OAuth2 client integration.
20. **`frappe-doc-updater`**: Auto-documentation for DocTypes, whitelisted APIs, and hooks registries.

---

## 9. COMMON FRAPPE WORKFLOWS

### The Complete 6-Stage Turnkey Feature Lifecycle
1. **Stage 1: Architecture & Specs**  
   Run `/frappe:hld` and `/frappe:lld` to establish C4 diagrams, entity-relationship schemas, and state transitions.
2. **Stage 2: Wireframing & Prototyping**  
   Run `/frappe:wireframe` for form layouts, then `/frappe:prototype` to generate a clickable HTML demo for stakeholders.
3. **Stage 3: Full-Stack Implementation**  
   Run `/frappe:build-e2e` to synthesize DocType JSONs, Python controllers, Desk client scripts, and hooks.
4. **Stage 4: Automated & Manual QA**  
   Run `/frappe:test` for unit tests, `/frappe:e2e-test` for Playwright browser tests, and `/frappe:manual-qa` for QA sign-off.
5. **Stage 5: Security & Code Review**  
   Run `/frappe:review` and `/frappe:security` (Frappe Shield) to verify zero SQLi or transaction errors.
6. **Stage 6: Production Deployment**  
   Generate database patches via `/frappe:patch` and apply via `bench migrate`.

---

## 10. TOKEN OPTIMIZATION (SAVE MONEY)
- Use `/frappe:hld` and `/frappe:lld` to establish specs upfront, eliminating iterative prompting loops.
- Run `python bin/frappe-shield.py` locally for instant static security scanning consuming **0 LLM tokens**.
- Use `/clear` when transitioning between unrelated modules.

---

## 11. TROUBLESHOOTING & DIAGNOSTICS
Run the system doctor:
```bash
python bin/frappe_ecc_install.py doctor
```
Checks Python runtime, platform, and editor installation paths.

---

## 12. COMMAND REFERENCE & RESOURCES
- **Frappe Documentation**: [frappeframework.com/docs](https://frappeframework.com/docs)
- **ERPNext Documentation**: [docs.erpnext.com](https://docs.erpnext.com)
- **GitHub Repository**: [github.com/srikrishnaprofessional-gif/Frappe-ECC](https://github.com/srikrishnaprofessional-gif/Frappe-ECC)
