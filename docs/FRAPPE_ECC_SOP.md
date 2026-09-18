# STANDARD OPERATING PROCEDURE (SOP)
## Engineering Coordination Center for Frappe Framework (Frappe ECC)
**Document ID:** SOP-ENG-FRAPPE-ECC-001  
**Version:** 1.0.0  
**Effective Date:** 2026-09-18  
**Applicability:** Full-Stack Frappe Framework (v14, v15, v16), ERPNext Customizations, AI Pair Programming  

---

## 1. PURPOSE & SCOPE

### 1.1 Purpose
This Standard Operating Procedure (SOP) defines the end-to-end methodology for utilizing **Frappe ECC (Engineering Coordination Center)** to plan, architect, build, test, secure, and deploy Frappe applications and ERPNext extensions using AI coding assistants (Antigravity, Claude Code, Cursor, Codex, Gemini CLI).

### 1.2 Scope
This procedure applies to all software engineers, technical leads, QA testers, and DevOps engineers developing on Frappe Framework. It covers:
- Initial environment setup and verification
- 10-phase feature development lifecycle
- Automated quality enforcement and security auditing with **Frappe Shield**
- Bench operations, troubleshooting, and production deployment checklists

---

## 2. SYSTEM ARCHITECTURE & COMPONENTS

Frappe ECC provides a coordinated engineering layer specifically tuned for the Frappe/ERPNext runtime:

```
Frappe ECC Runtime Architecture
├── 12 Specialist AI Agents (Planning, Architecture, Controllers, Desk UI, TDD, Review, Security, DevOps)
├── 14 Production Workflow Skills (DocType modeling, QueryBuilder, hooks, REST APIs, permissions, patches)
├── 13 Slash Commands (/frappe:plan, /frappe:doctype, /frappe:controller, /frappe:test, /frappe:security)
├── 5 Always-Loaded Coding Rules (Core standards, Python backend, Desk JS, Security, Database)
└── Frappe Shield Engine (AST-based static analyzer for SQLi, transaction safety & API defense)
```

---

## 3. PHASE 0: INSTALLATION & VERIFICATION

### Step 0.1: Verify Prerequisites
Ensure the host machine or development container meets the required specifications:
```bash
# 1. Python version (>= 3.10 required)
python --version

# 2. Node.js version (>= 18 required for multi-editor CLI)
node --version

# 3. Git version
git --version

# 4. Frappe Bench CLI (if running site commands locally)
bench --version
```

### Step 0.2: Install Frappe ECC into Antigravity
Run the installation command from the `frappe-ecc` repository root:
```bash
# On Linux / macOS / WSL:
./install.sh --profile minimal --target antigravity

# On Windows PowerShell:
.\install.ps1 -Profile minimal -Target antigravity
```
**Expected Outcome:**
- Workflow skills installed to: `~/.gemini/config/skills/`
- Plugin manifest and specialist agents registered in: `~/.gemini/config/plugins/frappe-ecc/`
- Coding rules registered in: `~/.gemini/config/rules/`

### Step 0.3: Install into Other Code Editors (Optional)
- **Claude Code:** `./install.sh --profile minimal --target claude`
- **Cursor:** `./install.sh --profile minimal --target cursor`
- **All Editors:** `./install.sh --profile minimal --target all`

### Step 0.4: Execute System Diagnostic Check
Run the built-in diagnostic doctor:
```bash
python bin/frappe_ecc_install.py doctor
```
Confirm that Python, Platform, and editor configuration directories display `[EXISTS]`.

---

## 4. THE 10-PHASE FEATURE DEVELOPMENT SOP

Follow this strict phased sequence when developing any new Frappe feature, DocType, or module:

```
[Phase 1: Plan Architecture] ──> [Phase 2: Model DocType] ──> [Phase 3: TDD Failing Tests]
         │
         ▼
[Phase 4: Implement Controller] ──> [Phase 5: Desk UI Scripts] ──> [Phase 6: Wire Hooks]
         │
         ▼
[Phase 7: Expose Secure APIs] ──> [Phase 8: Create DB Patches] ──> [Phase 9: Code Review]
         │
         ▼
[Phase 10: Frappe Shield Security Audit] ──> [Deploy to Bench]
```

---

### PHASE 1: FEATURE PLANNING & ARCHITECTURE BLUEPRINTING

**Goal:** Establish the complete database schema, module layout, relationships, and build order before writing code.

1. **Invoke the Planner:**
   - In Antigravity: Ask your assistant: *"Use frappe-planner to plan the <Feature Name> feature."*
   - In Claude Code: Run `/frappe:plan "<Feature Description>"`
2. **Review the Generated Blueprint:**
   - Confirm DocType taxonomy: Standard DocType vs Single DocType vs Child Table vs Submittable.
   - Verify autonaming series (e.g. `format:AST-.YYYY.-.#####`).
   - Verify field types (`Link`, `Dynamic Link`, `Table`, `Select`, `Currency`, `Check`).
   - Verify role permission matrix (System Manager, Operator, Auditor).
3. **Approval Gate:** Do not proceed to code creation until the schema blueprint is reviewed and confirmed.

---

### PHASE 2: DOCTYPE MODELING & SCHEMA SCAFFOLDING

**Goal:** Generate standard Frappe schema definitions (`.json`), Python controller stubs (`.py`), client scripts (`.js`), and test files (`test_*.py`).

1. **Execute Scaffolding:**
   - In Antigravity: *"Use frappe-doctype-design to scaffold DocType <DocType Name> in module <Module Name>."*
   - Slash Command: `/frappe:doctype "<DocType Name>" --module "<Module Name>"`
2. **Verify File Layout:**
   Ensure files are created under `<app_name>/<module_name>/doctype/<doctype_slug>/`:
   - `<doctype_slug>.json`
   - `<doctype_slug>.py`
   - `<doctype_slug>.js`
   - `test_<doctype_slug>.py`
3. **Standard Field Rules:**
   - Set `"search_index": 1` on fields queried frequently (e.g. serial numbers, device tags).
   - Set `"in_list_view": 1` and `"in_standard_filter": 1` for primary search filters.
   - Ensure child table field has `"fieldtype": "Table"` with `"options": "<Child DocType>"`.

---

### PHASE 3: TEST-DRIVEN DEVELOPMENT (TDD) — WRITE TESTS FIRST

**Goal:** Guarantee code correctness and prevent regressions by writing automated tests with `FrappeTestCase` before implementing controller logic.

1. **Activate TDD Guide:**
   - In Antigravity: *"Use frappe-testing-tdd to scaffold unit tests for <DocType Name>."*
   - Slash Command: `/frappe:test "<DocType Name>"`
2. **Draft Test Assertions in `test_<doctype_slug>.py`:**
   - Test 1: Autoname generation and initial draft status.
   - Test 2: Mandatory field validation and expected exceptions (`frappe.ValidationError`).
   - Test 3: Submittable lifecycle transitions (`doc.submit()`, `doc.cancel()`).
   - Test 4: Duplicate entry rejection (`frappe.DuplicateEntryError`).
3. **Run Tests to Verify Failure (RED State):**
   ```bash
   bench --site <site_name> run-tests --app <app_name> --doctype "<DocType Name>"
   ```
   Confirm tests fail for the expected reasons before writing controller code.

---

### PHASE 4: BACKEND CONTROLLER & LIFECYCLE IMPLEMENTATION

**Goal:** Implement business logic, state transitions, calculations, and data validations inside the Python controller.

1. **Invoke Controller Builder:**
   - In Antigravity: *"Use frappe-backend-builder to implement lifecycle validations for <DocType Name>."*
   - Slash Command: `/frappe:controller "<DocType Name>"`
2. **Implement Appropriate Lifecycle Hooks:**
   - `before_insert()`: Defaults, calculated sequences, initial status.
   - `validate()`: Cross-field assertions, date comparisons, range validations.
   - `before_save()` / `on_update()`: Secondary document synchronization.
   - `on_submit()`: Immutability triggers, financial/asset ledger posts.
   - `on_cancel()`: Reversals and cancellation tracking.
3. **MANDATORY CODING RULES:**
   - 🚫 **NEVER call `frappe.db.commit()` inside controller events.** Frappe manages database transactions automatically.
   - 🚫 **NEVER use Python string formatting in SQL.** Use `frappe.qb` (QueryBuilder) or parameterized queries (`values={...}`).
   - 🚫 **NEVER call `frappe.get_doc()` inside high-volume loops.** Use `frappe.get_all()` with explicit `fields` list.
   - Wrap all user-facing strings in `_("...")` for multi-language translation.
4. **Re-run Tests (GREEN State):**
   Verify all unit tests pass:
   ```bash
   bench --site <site_name> run-tests --app <app_name> --doctype "<DocType Name>"
   ```

---

### PHASE 5: DESK UI & REACTIVE CLIENT SCRIPTING

**Goal:** Deliver responsive, interactive Desk form UX without direct DOM manipulation.

1. **Invoke Desk Builder:**
   - In Antigravity: *"Use frappe-client-scripts to build the form client script for <DocType Name>."*
   - Slash Command: `/frappe:client-script "<DocType Name>"`
2. **Implement Event Handlers in `<doctype_slug>.js`:**
   - `onload(frm)`: Set query filters on Link fields (`frm.set_query`).
   - `refresh(frm)`: Add custom action buttons (`frm.add_custom_button`), status indicators.
   - `validate(frm)`: Fast pre-save client validation.
   - Field triggers: Dynamic field visibility (`frm.toggle_display`), mandatory toggles (`frm.toggle_reqd`).
   - Child table grid calculations: Use `frappe.model.set_value(cdt, cdn, field, value)`.
3. **MANDATORY UI RULES:**
   - 🚫 **NEVER manipulate DOM directly** using jQuery (`$('input[...]')`). Always use Frappe Desk APIs.
   - Display alerts using `frappe.show_alert({ message: __('...'), indicator: 'green' })`.

---

### PHASE 6: HOOK REGISTRATION & EVENT ORCHESTRATION

**Goal:** Wire document event listeners, scheduled background cron jobs, and class overrides into `hooks.py`.

1. **Invoke Hooks Specialist:**
   - In Antigravity: *"Use frappe-hooks-and-events to configure hooks for <task>."*
   - Slash Command: `/frappe:hook [doc-event | cron | override | fixture]`
2. **Update `<app_name>/hooks.py`:**
   - Document events: `doc_events = { "<DocType>": { "on_submit": "path.to.handler" } }`
   - Scheduled tasks: `scheduler_events = { "daily": ["path.to.daily_task"] }`
   - Class overrides: `override_doctype_class = { "<Core DocType>": "path.to.CustomClass" }`
3. **Export Fixtures (if applicable):**
   ```bash
   bench --site <site_name> export-fixtures
   ```

---

### PHASE 7: WHITELISTED APIS & EXTERNAL INTEGRATIONS

**Goal:** Create secure HTTP REST endpoints and webhook receivers.

1. **Invoke API Integrator:**
   - In Antigravity: *"Use frappe-rest-api to create a whitelisted endpoint for <feature>."*
   - Slash Command: `/frappe:api "<endpoint_name>" --method POST`
2. **Enforce Security Controls:**
   - Role authorization: `frappe.only_for(["Role Name"])` or `frappe.has_permission(...)`.
   - Rate limiting on public endpoints: `@frappe.rate_limit(limit=10, seconds=60)`.
   - Input sanitization: `frappe.utils.escape_html()` for free-text inputs.
   - Return structured response envelopes: `{"status": "success", "data": ...}`.

---

### PHASE 8: DATABASE SCHEMA MIGRATIONS & PATCHES

**Goal:** Ensure schema transitions and data transformations are strictly idempotent across bench migrations.

1. **Invoke Migration Specialist:**
   - In Antigravity: *"Use frappe-patches-migrations to create patch <patch_name>."*
   - Slash Command: `/frappe:patch "<patch_description>"`
2. **Author Patch in `<app_name>/patches/vX_Y/<patch_name>.py`:**
   - Call `frappe.reload_doc("<module>", "doctype", "<doctype>")` first.
   - Check if changes are already present before executing database writes.
   - Register patch in `<app_name>/patches.txt`.
3. **Verify Migration Execution:**
   ```bash
   bench --site <site_name> migrate
   ```

---

### PHASE 9: FRESH-CONTEXT CODE REVIEW

**Goal:** Run an independent code review to detect Frappe anti-patterns and performance bottlenecks before committing code.

1. **Invoke Code Reviewer:**
   - In Antigravity: *"Use frappe-code-reviewer to review recent changes in <file or app>."*
   - Slash Command: `/frappe:review [file or path]`
2. **Review Checklist:**
   - Check for stray `frappe.db.commit()` in controllers.
   - Check for N+1 queries (`get_doc` inside loops).
   - Verify all user strings are enclosed in `_("...")`.
   - Verify child table calculations trigger dirty states properly.

---

### PHASE 10: SECURITY AUDIT WITH FRAPPE SHIELD

**Goal:** Execute AST-based static vulnerability scanning against the codebase.

1. **Run Frappe Shield Scanner:**
   From the repository root or terminal:
   ```bash
   python bin/frappe-shield.py path/to/your_app
   ```
   Or via command: `/frappe:security`
2. **Evaluation Criteria:**
   - **CRITICAL**: SQL Injection in `frappe.db.sql()` (f-strings, %, or .format). Must be remediated immediately.
   - **CRITICAL**: Manual `frappe.db.commit()` inside controller event hooks.
   - **HIGH**: Public `@frappe.whitelist(allow_guest=True)` lacking `@frappe.rate_limit`.
   - **HIGH**: Direct `docstatus = 1` assignment.
   - **MEDIUM**: `frappe.get_doc()` called inside loops (N+1 query).
3. **Remediate all CRITICAL and HIGH issues** before submitting code for deployment.

---

## 5. DEVOPS, BENCH OPERATIONS & TROUBLESHOOTING

| Symptom / Error | Root Cause | Standard Remediation Procedure |
|---|---|---|
| `redis.exceptions.ConnectionError` | Redis server offline or socket misconfigured | Run `bench start` or `sudo systemctl restart redis-server`. Check `config/redis_cache.conf`. |
| `DuplicateEntryError` during migrate | Unique index violated by existing records | Inspect table in `bench mariadb`. Deduplicate records or run cleanup patch before applying unique constraint. |
| `ModuleNotFoundError` during bench migrate | App uninstalled or module missing in `modules.txt` | Verify app is in `sites/apps.txt`. Run `bench build --app <app_name>`. |
| Desk Form UI changes not reflecting | Asset cache or Redis boot cache stale | Run `bench --site <site> clear-cache` and `bench build --app <app_name>`. Hard refresh browser (`Ctrl+F5`). |
| Background jobs stuck in queue | RQ worker processes died | Inspect queues with `bench doctor`. Restart workers: `bench worker --queue default,short,long`. |

---

## 6. TOKEN OPTIMIZATION BEST PRACTICES

1. **Always Plan First:** Running `/frappe:plan` upfront defines schemas cleanly, preventing 5+ iterative re-prompts.
2. **Use Local Static Analysis:** Run `python bin/frappe-shield.py` locally on your machine. It executes in milliseconds and consumes **0 LLM tokens**.
3. **Target Specific DocTypes:** Avoid pasting whole application repositories into prompt context. Provide only the target `.py` and `.json` files.
4. **Context Breakpoints:** Type `/clear` when transitioning between completely unrelated DocTypes or modules.

---

## 7. QUICK REFERENCE COMMAND MATRIX

| Slash Command | Specialist Agent | Primary Workflow Skill | Standard Action |
|---|---|---|---|
| `/frappe:plan` | `frappe-planner` | `frappe-doctype-design` | Create feature architecture blueprint |
| `/frappe:doctype` | `frappe-planner` | `frappe-doctype-design` | Scaffold `.json`, `.py`, `.js`, and `test_*.py` |
| `/frappe:controller` | `frappe-backend-builder` | `frappe-orm-and-queries` | Implement lifecycle hooks (`validate`, `on_submit`) |
| `/frappe:client-script` | `frappe-desk-builder` | `frappe-client-scripts` | Build Desk form UI interactions & dialogs |
| `/frappe:hook` | `frappe-architect` | `frappe-hooks-and-events` | Register `doc_events`, cron, or class overrides |
| `/frappe:api` | `frappe-api-integrator` | `frappe-rest-api` | Create whitelisted REST API endpoint |
| `/frappe:test` | `frappe-tdd-guide` | `frappe-testing-tdd` | Scaffold unit tests with `FrappeTestCase` |
| `/frappe:review` | `frappe-code-reviewer` | `frappe-orm-and-queries` | Fresh-context review for anti-patterns |
| `/frappe:security` | `frappe-security-reviewer` | `frappe-shield-security-audit` | Run AST security scanner (SQLi, auth, XSS) |
| `/frappe:patch` | `frappe-migration-patcher` | `frappe-patches-migrations` | Draft idempotent DB patch in `patches.txt` |
| `/frappe:report` | `frappe-report-builder` | `frappe-reports-and-dashboards` | Scaffold Script Report (Python + JS) |
| `/frappe:bench` | `frappe-bench-devops` | `frappe-bench-cli` | Diagnose bench errors & site operations |
| `/frappe:help` | All Agents | - | Display quick cheat sheet |

---
**Document Approved By:** Antigravity Engineering Systems  
**Repository Path:** `C:\Users\srikrishna.rg_quanti\.gemini\antigravity-ide\scratch\frappe-ecc`
