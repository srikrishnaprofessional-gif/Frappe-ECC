# Frappe ECC

**Build Frappe Framework apps with Claude Code and prove they work.**

Frappe ECC has two parts that work together:

1. **A Claude Code plugin**: 16 Frappe skills written against Frappe's own source code (v15 and
   v16), 12 specialist agents, and 17 slash commands that take an app from requirements to a tested,
   security-scanned result.
2. **The `frappe-ecc` CLI** (Python 3.10+, no dependencies), which Claude uses and you can run
   yourself:
   - `validate`: checks an app spec against the rules Frappe applies when it saves a DocType
     (fieldtypes, reserved names, naming, permission dependencies, links).
   - `new` / `add-doctypes`: generates an installable app (DocType JSON, controllers, form
     scripts, tests, hooks, pyproject, CI) in the layout `bench new-app` uses.
   - `verify`: links the app into a real bench, installs it on a site, migrates, runs its tests,
     and reports the actual exit codes and test counts.
   - `shield`: static checks for SQL injection, transaction misuse, unsafe guest APIs,
     permission bypasses, secrets and N+1 queries.

## What it does and doesn't do

| It does | It doesn't |
|---|---|
| Generate the data model (DocTypes, fields, naming, permissions) and boilerplate from a spec, deterministically | Guess your business rules. Claude writes those from your requirements, with tests, and you review them |
| Refuse specs Frappe would reject, before you install anything | Replace testing on a real site. `verify` runs on your bench |
| Give Claude accurate Frappe knowledge so its code follows Frappe conventions | Run without Claude Code for the AI parts. The CLI alone generates, validates, verifies and scans |
| Flag common security mistakes on every file Claude edits | Prove code is secure. Shield finds patterns, and the security review adds a manual checklist |

## Install

Requirements: [Claude Code](https://code.claude.com), Python 3.10+, git. A Frappe bench is needed
for `verify` and for running apps.

**For your team (from GitHub):**

```bash
claude plugin marketplace add srikrishnaprofessional-gif/Frappe-ECC
claude plugin install frappe-ecc@frappe-ecc
```

**From a local clone:**

```bash
git clone https://github.com/srikrishnaprofessional-gif/Frappe-ECC.git
cd "Frappe-ECC/Version 2"
./install.sh              # Windows: .\install.ps1
```

`./install.sh` registers the clone as a plugin marketplace and installs the plugin. It also
removes files that installers before v3 copied into `~/.claude` (`--keep-legacy` to skip). Restart
Claude Code, then run `/frappe-ecc:help`.

**Cursor:** `./install.sh cursor /path/to/project` writes the skills as Cursor rules into
`.cursor/rules/`.

**CLI only:** `pip install "git+https://github.com/srikrishnaprofessional-gif/Frappe-ECC.git#subdirectory=Version 2"`
(add `pyyaml` for YAML specs).

Check your setup with `frappe-ecc doctor`.

## Quick start

In Claude Code, inside or next to your bench:

```text
/frappe-ecc:new-app A clinic app: patients, doctors, appointments that doctors submit after the
consultation, prescriptions per appointment, and clinic settings. Receptionists book, doctors
see only their own appointments.
```

Claude will:
1. design the data model with the **frappe-architect** agent and show it to you for confirmation;
2. write and validate the spec, then generate the app (`frappe-ecc new`) as a git repo;
3. install it on a throwaway site and run its tests (`frappe-ecc verify`);
4. implement the business rules with tests (backend, frontend, workflow and report agents);
5. verify again, run Frappe Shield and a code review, and report what passed and what didn't.

Or by hand with the CLI:

```bash
frappe-ecc validate examples/clinic_management.json
frappe-ecc new examples/clinic_management.json --dest ~/code --ci
frappe-ecc verify ~/code/clinic_management --bench ~/frappe-bench --site test.localhost
frappe-ecc shield ~/code/clinic_management
```

`verify` needs an existing **throwaway** site, because tests write data. Create one with
`bench new-site test.localhost --admin-password admin`.

## Commands

| Command | Does |
|---|---|
| `/frappe-ecc:new-app <requirements>` | Requirements → confirmed model → generated app → verified → business logic → tested and scanned |
| `/frappe-ecc:add-doctype <description>` | New DocTypes in an existing app, migrated and tested |
| `/frappe-ecc:api <description>` | Whitelisted endpoint or integration with permission checks and tests |
| `/frappe-ecc:report <description>` | Script/Query report or dashboard, with a test |
| `/frappe-ecc:workflow <process>` | Workflow, notifications, assignment rules as fixtures |
| `/frappe-ecc:print-format <doctype>` | Jinja print format shipped with the app |
| `/frappe-ecc:patch <change>` | Idempotent data migration patch |
| `/frappe-ecc:import-data <file>` | CSV/Excel import with mapping and reconciliation |
| `/frappe-ecc:verify` | Real install + migrate + tests on a site |
| `/frappe-ecc:test <target>` | Write missing tests and run them |
| `/frappe-ecc:review` | Code review of changes |
| `/frappe-ecc:security` | Security audit (Shield + manual checklist) |
| `/frappe-ecc:shield [path]` | Run the scanner and triage findings |
| `/frappe-ecc:debug <error>` | Root-cause a failure and fix it |
| `/frappe-ecc:deploy <ci\|docker\|production\|upgrade>` | Environments, CI and releases |
| `/frappe-ecc:docs` | User, admin and developer docs from the code |
| `/frappe-ecc:help` | Overview and `doctor` |

**Skills** (loaded automatically when relevant): app-spec, doctypes, controllers, hooks, api,
permissions, client-scripts, testing, patches, background-jobs, reports, workflows,
print-formats, portal, bench, security-review.

**Agents:** architect, backend-developer, frontend-developer, test-engineer, code-reviewer,
security-reviewer, debugger, report-builder, workflow-designer, data-engineer, devops, docs-writer.

**Hook:** after Claude edits a `.py` or `.js` file, Frappe Shield scans it and sends HIGH/CRITICAL
findings back to Claude to fix.

## The app spec

A JSON (or YAML) file describing the app, modules, DocTypes, fields and permissions. See
[`skills/frappe-app-spec/SKILL.md`](skills/frappe-app-spec/SKILL.md) for the format and
[`examples/clinic_management.json`](examples/clinic_management.json) for a complete example
(standard, submittable, child table and single DocTypes; links, fetch_from, roles).

## Compatibility

| | Supported |
|---|---|
| Frappe | v15, v16 (generated apps and skills). The CI workflow verifies a generated app on both. Rules are also checked against v17-dev |
| Python | 3.10+ for the CLI. Generated apps follow the bench's Python |
| Claude Code | Plugin format with `.claude-plugin/`, validated with `claude plugin validate --strict` |
| OS | Linux, macOS, Windows (WSL recommended for bench) |

## Development

Run these from the `Version 2/` folder:

```bash
python3 -m unittest discover -s tests -t .           # unit tests
~/frappe-bench/env/bin/python -m unittest tests.test_spec   # also checks rules against installed Frappe
claude plugin validate --strict .
bin/frappe-ecc shield frappe_ecc
```

CI (`.github/workflows/ci.yml` at the repository root) runs the unit tests on Python 3.10–3.14 and validates the plugin.
It also generates the example app and runs `frappe-ecc verify` against real Frappe v15 and v16
benches.

When Frappe changes a rule, `tests/test_spec.py::TestRulesMatchInstalledFrappe` fails on that
version. Update `frappe_ecc/frappe_rules.py` to match.

## License

MIT. See [LICENSE](LICENSE).
