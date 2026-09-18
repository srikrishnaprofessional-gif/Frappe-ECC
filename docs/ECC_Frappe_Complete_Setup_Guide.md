# THE COMPLETE FRAPPE ECC SETUP GUIDE
### 12 AI Agents • 14 Skills • 13 Commands • Frappe Shield
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
8. Key Agents Explained
9. Common Frappe Workflows
10. Token Optimization (Save Money)
11. Troubleshooting & Diagnostics
12. Command Reference & Resources

---

## 1. WHAT IS FRAPPE ECC?

**Frappe ECC** (Frappe Engineering Coordination Center) is an open-source engineering system that transforms your AI code editor — Antigravity, Claude Code, Cursor, Codex, or Gemini CLI — into a coordinated, senior Frappe Framework engineering team.

Frappe Framework is unique. It isn't just Python or JavaScript; it is an opinionated full-stack architecture built on DocTypes, lifecycle controller hooks (`before_insert`, `validate`, `on_submit`), the Frappe ORM and QueryBuilder (`frappe.qb`), Bench CLI, MariaDB/PostgreSQL schemas, Redis queues, and Desk UI scripting (`frappe.ui.form.on`).

Generic AI assistants often make critical mistakes with Frappe:
- Calling `frappe.db.commit()` inside controller events, breaking database transactions.
- Concatenating f-strings into `frappe.db.sql()`, introducing severe SQL injection vulnerabilities.
- Direct DOM manipulation in client scripts instead of using Desk APIs.
- N+1 query loops loading full documents with `frappe.get_doc()` inside list iterations.

**Frappe ECC eliminates these mistakes.** It equips your AI assistant with 12 specialist agents, 14 reusable workflow skills, 13 slash commands, and **Frappe Shield** — a dedicated AST static security scanner that catches Frappe anti-patterns before your code hits production.

> 💡 **Key Point**  
> Frappe ECC is NOT a separate desktop software or bloated daemon. It installs directly into your code editor (Antigravity, Claude Code, Cursor, etc.) and supercharges it from the inside.

---

## 2. WHAT'S INSIDE — THE NUMBERS

| Component | Count | What It Does |
|---|---|---|
| **Agents** | 12 | Specialist AI workers: planning, backend controllers, desk UI, testing, code review, security, DevOps, migrations, and reporting |
| **Skills** | 14 | Reusable workflows: DocType modeling, QueryBuilder, `hooks.py`, client scripts, REST APIs, permissions, TDD, and background jobs |
| **Commands** | 13 | Slash commands: `/frappe:plan`, `/frappe:doctype`, `/frappe:controller`, `/frappe:test`, `/frappe:security`, `/frappe:bench` |
| **Rules** | 5 | Always-loaded coding standards: Core architecture, Python backend, Desk JS, Security, and Database optimization |
| **Frappe Shield** | Included | AST static security analyzer that detects SQLi in `frappe.db.sql`, `commit()` violations, and unvalidated guest endpoints |

### Supported Frappe & ERPNext Versions
- Frappe Framework v14, v15, and v16
- ERPNext v14, v15, and v16
- Frappe UI (Vue 3 + Tailwind CSS SPAs)
- Custom Apps & Bench multi-tenant sites

---

## 3. WHAT CAN FRAPPE ECC ACTUALLY DO?

### Planning & Schema Architecture
Give Frappe ECC a business requirement (e.g., *"Build an IT Asset Management lifecycle with maintenance scheduling and warranty alerts"*), and the **frappe-planner** generates a complete blueprint: DocType taxonomy, child tables, field types (`Link`, `Dynamic Link`, `Table`, `Currency`), naming rules, and module file manifests before a single line of code is written.

### Bulletproof Backend Controllers
ECC writes idiomatic Python DocType controllers implementing Frappe's exact lifecycle hooks (`before_insert`, `validate`, `on_submit`, `on_cancel`). It automatically uses `frappe.qb` for complex joins, wraps translatable strings with `_("...")`, and strictly avoids illegal `db.commit()` calls.

### Reactive Desk UI & Client Scripts
The **frappe-desk-builder** generates clean, event-driven JavaScript for Frappe Desk. It leverages `frm.add_custom_button`, dynamic field property toggles (`frm.set_df_property`), child table grid calculations, and native `frappe.ui.Dialog` popups without direct DOM manipulation.

### Test-Driven Development (TDD)
The **frappe-tdd-guide** enforces writing tests first with `FrappeTestCase`. It scaffolds test fixtures, mock data, and test assertions in `test_<doctype>.py`, verifying validation rules, autoname generation, and transaction rollbacks.

### Fresh-Context Code Review
ECC provides an independent code reviewer that inspects diffs for Frappe anti-patterns:
- Accidental `frappe.db.commit()` inside controller events.
- N+1 queries (`frappe.get_doc` inside loops).
- Unindexed fields used in search filters.

### Automated Security & Red-Teaming (Frappe Shield)
Frappe Shield scans your codebase using Python's AST parser, catching:
- SQL injection vulnerabilities in `frappe.db.sql()`.
- Missing `@frappe.rate_limit` on `@frappe.whitelist(allow_guest=True)` endpoints.
- Direct `docstatus` assignment bypassing submission logic.
- Broken access controls and missing permission checks.

---

## 4. PREREQUISITES

| Requirement | Details | Check Command |
|---|---|---|
| **Node.js** | Version 18 or newer | `node --version` |
| **Python** | Version 3.10 or newer | `python --version` |
| **Git** | Recent version | `git --version` |
| **Frappe Bench** | (Optional for site execution) v5.15+ | `bench --version` |
| **Code Editor** | Antigravity, Claude Code (2.1+), Cursor, or Gemini CLI | - |

---

## 5. INSTALLATION — ANTIGRAVITY (RECOMMENDED)

You can install Frappe ECC into Antigravity with a single command:

```bash
./install.sh --profile minimal --target antigravity
```

On Windows PowerShell:
```powershell
.\install.ps1 -Profile minimal -Target antigravity
```

### What this does:
1. Installs the 14 Frappe workflow skills directly into your Antigravity skills registry (`~/.gemini/config/skills/`).
2. Registers the `frappe-ecc` plugin manifest with all 12 specialist agents.
3. Deploys the Frappe coding standards into Antigravity rules (`~/.gemini/config/rules/`).
4. Makes all Frappe skills instantly accessible to your Antigravity agent!

---

## 6. INSTALLATION — CLAUDE CODE & CURSOR

### Claude Code
```bash
./install.sh --profile minimal --target claude
```
This installs the full set of slash commands (`/frappe:plan`, `/frappe:doctype`, etc.), agents, skills, and the `post_file_edit` hook into `~/.claude/`.

### Cursor
```bash
./install.sh --profile minimal --target cursor
```
This generates `.cursor/rules/` within your project with the complete Frappe rule packs.

---

## 7. GETTING STARTED — YOUR FIRST COMMANDS

| What You Want To Do | Command | What Happens |
|---|---|---|
| **Plan a feature or app** | `/frappe:plan "Asset Maintenance Tracking"` | `frappe-planner` designs the full DocType hierarchy and schema blueprint |
| **Scaffold a DocType** | `/frappe:doctype "Asset Ticket" --module "itam_core"` | Generates `.json`, `.py`, `.js`, and `test_*.py` files |
| **Implement controller** | `/frappe:controller "Asset Ticket"` | Generates lifecycle validations (`validate`, `on_submit`) |
| **Create Desk script** | `/frappe:client-script "Asset Ticket"` | Generates Desk UI events, custom buttons, and dialogs |
| **Wire hook or cron** | `/frappe:hook cron` | Adds scheduled tasks to `hooks.py` |
| **Scaffold REST API** | `/frappe:api "telemetry_ping" --method POST` | Creates `@frappe.whitelist()` endpoint with permission checks |
| **Run unit tests** | `/frappe:test "Asset Ticket"` | Creates and runs tests with `FrappeTestCase` |
| **Review code** | `/frappe:review` | Fresh-context reviewer checks for Frappe anti-patterns |
| **Run security audit** | `/frappe:security` | Frappe Shield audits code for SQLi and permission bypass |
| **Generate DB patch** | `/frappe:patch "migrate_legacy_tags"` | Creates idempotent patch in `patches.txt` |
| **Diagnose bench issue** | `/frappe:bench "Redis connection refused"` | `frappe-bench-devops` provides exact root cause and fix |

---

## 8. KEY AGENTS EXPLAINED

- **frappe-planner**: Analyzes business specs and outputs DocType schemas, naming series, child table links, and execution blueprints before code is written.
- **frappe-architect**: Handles macro system choices: multi-site bench layouts, RQ queue distribution (`short`, `default`, `long`), and ERPNext vs custom app boundaries.
- **frappe-backend-builder**: Writes clean Python controllers extending `Document`, using `frappe.qb`, and enforcing validations.
- **frappe-desk-builder**: Builds event-driven JavaScript for Frappe Desk forms, lists, and custom dialogs.
- **frappe-tdd-guide**: Drives test-driven development using `FrappeTestCase`, ensuring test isolation and 80%+ test coverage.
- **frappe-code-reviewer**: Evaluates code in a fresh context, flagging performance issues, unindexed queries, and `db.commit()` violations.
- **frappe-security-reviewer**: Runs AST security audits, identifying SQLi, insecure whitelist functions, and unvalidated parameters.
- **frappe-bench-devops**: Diagnoses bench failures: migration locks, asset builds, and Redis worker bottlenecks.
- **frappe-migration-patcher**: Writes safe, idempotent database migration patches for `patches.txt`.

---

## 9. COMMON FRAPPE WORKFLOWS

### Workflow A: Building a New Frappe Feature (Start to Finish)
1. **Plan Architecture**:  
   `/frappe:plan "Asset Check-In and Check-Out System"`  
   *Output: Complete blueprint with DocType schemas, fields, and relationships.*
2. **Scaffold DocTypes**:  
   `/frappe:doctype "Asset Movement" --module "itam_core"`
3. **Build with TDD**:  
   Activate `frappe-testing-tdd`. Write failing assertions in `test_asset_movement.py`.
4. **Implement Controller Logic**:  
   `/frappe:controller "Asset Movement"` — Implement `validate()` and state checks.
5. **Add Desk Form Interactivity**:  
   `/frappe:client-script "Asset Movement"` — Add dynamic buttons and alerts.
6. **Code Review**:  
   `/frappe:review` — Review for anti-patterns and performance traps.
7. **Security Scan**:  
   `/frappe:security` — Verify zero SQLi and proper authorization checks.

### Workflow B: Fixing a Bug or Refactoring
1. Reproduce the bug with a failing test using `frappe-testing-tdd`.
2. Implement the fix in the controller or client script.
3. Run `bench --site <site> run-tests` to confirm test passes.
4. Run `/frappe:review` to verify no regressions were introduced.

---

## 10. TOKEN OPTIMIZATION (SAVE MONEY)

Frappe projects involve many interrelated files (DocType JSONs, Python controllers, JS scripts, hooks). Follow these habits to minimize token usage:
1. **Plan first with `/frappe:plan`**: Clarifying the architecture up front prevents wasteful iterative re-writes.
2. **Target specific DocTypes**: When asking for controller changes, provide only the target DocType rather than entire app trees.
3. **Use `/frappe:security` locally**: Frappe Shield runs locally via Python AST, consuming zero LLM tokens for static scanning.
4. **Clear context between tasks**: Use `/clear` or start fresh sessions when switching between unrelated modules.

---

## 11. TROUBLESHOOTING & DIAGNOSTICS

### Run the System Doctor
```bash
node bin/frappe-ecc.js doctor
```
Checks Node.js version, platform, and editor installation paths.

### Frappe Shield Flags Issues
If `python bin/frappe-shield.py` flags an issue:
- **`Manual DB Commit Inside Controller Hook`**: Remove `frappe.db.commit()`. Let Frappe handle transaction commit after `on_update` or `on_submit`.
- **`SQL Injection: f-string in frappe.db.sql`**: Replace f-strings with `values={"param": val}` or convert to `frappe.qb`.
- **`Unrestricted Guest Whitelist API`**: Add `@frappe.rate_limit(limit=10, seconds=60)` and sanitize inputs with `frappe.utils.escape_html()`.

---

## 12. COMMAND REFERENCE & RESOURCES

- **Frappe Documentation**: [frappeframework.com/docs](https://frappeframework.com/docs)
- **ERPNext Documentation**: [docs.erpnext.com](https://docs.erpnext.com)
- **Frappe UI**: [frappeui.com](https://frappeui.com)
- **Bench CLI Guide**: [github.com/frappe/bench](https://github.com/frappe/bench)
