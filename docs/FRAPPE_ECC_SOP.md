# STANDARD OPERATING PROCEDURE (SOP)
## Engineering Coordination Center for Frappe Framework (Frappe ECC)
**Document ID:** SOP-ENG-FRAPPE-ECC-001  
**Version:** 1.1.0  
**Effective Date:** 2026-09-18  
**Applicability:** Full-Stack Frappe Framework (v14, v15, v16), ERPNext Customizations, AI Pair Programming  

---

## 1. PURPOSE & SCOPE

### 1.1 Purpose
This Standard Operating Procedure (SOP) defines the end-to-end methodology for utilizing **Frappe ECC (Engineering Coordination Center)** to plan, architect (HLD/LLD), wireframe, prototype, build turnkey code, manually and automatically test (Playwright), secure, and deploy Frappe applications and ERPNext extensions using AI coding assistants (Antigravity, Claude Code, Cursor, Codex, Gemini CLI).

### 1.2 Scope
This procedure applies to all software engineers, technical architects, UI/UX designers, QA testers, and DevOps engineers developing on Frappe Framework.

---

## 2. SYSTEM ARCHITECTURE & COMPONENTS

Frappe ECC provides a coordinated engineering layer specifically tuned for the Frappe/ERPNext runtime:

```
Frappe ECC Runtime Architecture
├── 20 Specialist AI Agents (HLD, LLD, UI/UX, Wireframes, Prototypes, Turnkey Dev, Manual QA, Playwright Automation, Planner, Controllers, Desk UI, TDD, Review, Security, DevOps)
├── 18 Production Workflow Skills (HLD/LLD, Wireframing/Prototyping, QA automation, Turnkey scaffolding, DocType modeling, QueryBuilder, hooks, REST APIs, permissions, patches)
├── 20 Slash Commands (/frappe:hld, /frappe:lld, /frappe:wireframe, /frappe:prototype, /frappe:build-e2e, /frappe:manual-qa, /frappe:e2e-test, /frappe:plan, etc.)
├── 5 Always-Loaded Coding Rules (Core standards, Python backend, Desk JS, Security, Database)
└── Frappe Shield Engine (AST-based static analyzer for SQLi, transaction safety & API defense)
```

---

## 3. PHASE 0: INSTALLATION & VERIFICATION

### Step 0.1: Verify Prerequisites
Ensure the host environment meets the required specifications:
```bash
python --version   # >= 3.10 required
node --version     # >= 18 required
git --version
bench --version    # Optional for local site execution
```

### Step 0.2: Install Frappe ECC into Antigravity
Run the installation command from the `frappe-ecc` repository root:
```bash
# On Linux / macOS / WSL:
./install.sh --profile full --target antigravity

# On Windows PowerShell:
.\install.ps1 -Profile full -Target antigravity
```

### Step 0.3: Execute System Diagnostic Check
```bash
python bin/frappe_ecc_install.py doctor
```

---

## 4. THE COMPLETE 12-PHASE FEATURE DEVELOPMENT SOP

```
[Phase 1: HLD Architecture] ──> [Phase 2: LLD & ER Diagrams] ──> [Phase 3: Wireframes & Prototypes]
         │
         ▼
[Phase 4: Schema Modeling]  ──> [Phase 5: Unit Tests (TDD)]  ──> [Phase 6: Turnkey Fullstack Dev]
         │
         ▼
[Phase 7: Wire Hooks & Cron] ─> [Phase 8: Secure REST APIs]  ──> [Phase 9: DB Schema Patches]
         │
         ▼
[Phase 10: Manual QA Matrix] ─> [Phase 11: Playwright E2E]   ──> [Phase 12: Frappe Shield Audit]
```

---

### Phase 1: High-Level Design (HLD) & System Context
1. **Trigger:** Run `/frappe:hld "<Feature Description>"` or invoke `frappe-hld-architect`.
2. **Deliverable:** C4 Container Architecture Diagram (Mermaid), integration topology, caching strategy (Redis), and NFRs.

### Phase 2: Low-Level Design (LLD) & Entity-Relationship Modeling
1. **Trigger:** Run `/frappe:lld "<Feature Name>"` or invoke `frappe-lld-designer`.
2. **Deliverable:** Mermaid ER diagram (`erDiagram`) with exact data types, class hierarchy diagrams, state transition matrices, and API schemas.

### Phase 3: Visual Wireframing & Clickable Interactive Prototyping
1. **Trigger:**
   - Visual Wireframes: Run `/frappe:wireframe "<DocType Name>"` or invoke `frappe-wireframe-builder`.
   - Clickable Demo: Run `/frappe:prototype "<DocType Name>"` or invoke `frappe-interactive-prototyper`.
2. **Deliverable:** Standalone, clickable single-file HTML/Vue prototype for stakeholder preview before database writes.

### Phase 4: Schema Modeling & DocType Scaffolding
1. **Trigger:** Run `/frappe:doctype "<DocType Name>" --module "<Module Name>"` or invoke `frappe-planner`.
2. **Deliverable:** `.json` schema with sections, columns, indexed fields, and role permissions array.

### Phase 5: Test-Driven Development (TDD) — Unit Tests First
1. **Trigger:** Run `/frappe:test "<DocType Name>"` or invoke `frappe-tdd-guide`.
2. **Deliverable:** `test_<doctype>.py` asserting autoname prefixes, mandatory field rules, validation exceptions, and rollbacks.
3. **Execute RED Phase:** `bench run-tests --doctype "<DocType Name>"` (must fail as expected).

### Phase 6: Turnkey Fullstack Implementation
1. **Trigger:** Run `/frappe:build-e2e "<DocType Name>"` or invoke `frappe-fullstack-developer`.
2. **Deliverable:** Complete controller (`validate`, `on_submit`), Desk client script (`frappe.ui.form.on`), dialogs, and auto-math with **zero placeholders**.

### Phase 7: Hook Registration & Event Orchestration
1. **Trigger:** Run `/frappe:hook [event|cron|override]` or invoke `frappe-architect`.
2. **Deliverable:** Updates to `hooks.py` for `doc_events`, `scheduler_events`, and `override_doctype_class`.

### Phase 8: Whitelisted APIs & Webhook Integrations
1. **Trigger:** Run `/frappe:api "<name>" --method POST` or invoke `frappe-api-integrator`.
2. **Deliverable:** Secure `@frappe.whitelist()` endpoint with `frappe.only_for()`, `@frappe.rate_limit`, and input sanitization.

### Phase 9: Database Schema Migrations & Patches
1. **Trigger:** Run `/frappe:patch "<description>"` or invoke `frappe-migration-patcher`.
2. **Deliverable:** Idempotent patch in `patches/` registered in `patches.txt`.

### Phase 10: Manual QA Matrix & Exploratory Verification
1. **Trigger:** Run `/frappe:manual-qa "<DocType Name>"` or invoke `frappe-manual-qa`.
2. **Deliverable:** Structured test scenario matrix, edge-case charter, and release sign-off checklist.

### Phase 11: End-to-End Automated Browser Testing (Playwright)
1. **Trigger:** Run `/frappe:e2e-test "<DocType Name>"` or invoke `frappe-automated-tester`.
2. **Deliverable:** Headless Playwright script simulating Desk login, form entry, saving, and submission badge assertions.

### Phase 12: Security Audit with Frappe Shield & Code Review
1. **Trigger:** Run `/frappe:security` or `python bin/frappe-shield.py <app_path>`.
2. **Evaluation:** Verify zero SQL injection, zero manual `db.commit()` in controllers, and zero unvalidated guest endpoints before production release.

---

## 5. MASTER QUICK REFERENCE COMMAND MATRIX

| Slash Command | Specialist Agent | Standard Operation |
|---|---|---|
| `/frappe:hld '<feature>'` | `frappe-hld-architect` | Generate High-Level Design with C4 architecture diagrams |
| `/frappe:lld '<name>'` | `frappe-lld-designer` | Generate Low-Level Design with ER & state machine diagrams |
| `/frappe:wireframe '<name>'` | `frappe-wireframe-builder` | Generate visual ASCII / SVG wireframe layout mockups |
| `/frappe:prototype '<name>'` | `frappe-interactive-prototyper` | Generate clickable interactive HTML/Vue prototype |
| `/frappe:plan '<feature>'` | `frappe-planner` | Architect feature schema blueprint & module taxonomy |
| `/frappe:doctype '<Name>'` | `frappe-planner` | Scaffold `.json`, `.py`, `.js`, and `test_*.py` files |
| `/frappe:build-e2e '<spec>'`| `frappe-fullstack-developer` | Turnkey fullstack vertical synthesis (zero placeholders) |
| `/frappe:controller '<Name>'`| `frappe-backend-builder` | Implement controller lifecycle hooks and validations |
| `/frappe:client-script '<Name>'`| `frappe-desk-builder` | Build Desk form UI interactions & custom dialogs |
| `/frappe:hook [event|cron]` | `frappe-architect` | Wire `doc_events`, scheduler cron, or class overrides |
| `/frappe:api '<name>'` | `frappe-api-integrator` | Create secure whitelisted REST API endpoint |
| `/frappe:test '<Name>'` | `frappe-tdd-guide` | Scaffold unit tests with `FrappeTestCase` |
| `/frappe:manual-qa '<Name>'` | `frappe-manual-qa` | Generate manual test scenarios & QA sign-off checklist |
| `/frappe:e2e-test '<Name>'` | `frappe-automated-tester` | Generate Playwright automated browser test script |
| `/frappe:review [path]` | `frappe-code-reviewer` | Review diffs in fresh context for Frappe anti-patterns |
| `/frappe:security [path]` | `frappe-security-reviewer` | Execute AST security scanner (SQLi, IDOR, XSS) |
| `/frappe:patch '<desc>'` | `frappe-migration-patcher` | Draft idempotent database migration patch in `patches.txt` |
| `/frappe:report '<name>'` | `frappe-report-builder` | Scaffold Script Report (Python backend + JS frontend) |
| `/frappe:bench [task]` | `frappe-bench-devops` | Diagnose bench errors and site operations |
| `/frappe:help` | All Agents | Display master quick cheat sheet |

---
**Document Approved By:** Antigravity Engineering Systems  
**Repository Path:** `C:\Users\srikrishna.rg_quanti\.gemini\antigravity-ide\scratch\frappe-ecc`
