# Changelog

## 3.0.0

A rebuild. Earlier versions described capabilities the code did not have; this release keeps
only what works and is tested.

### Added
- `frappe-ecc` CLI (stdlib only): `validate`, `new`, `add-doctypes`, `verify`, `shield`,
  `install`, `uninstall`, `doctor`.
- App spec format with validation mirroring Frappe's DocType rules (v15–v17), including permission
  dependencies, naming rules, reserved fieldnames and name collisions with Frappe/ERPNext/HRMS.
- Generator producing `bench new-app`-compatible apps with DocType JSON, controllers, form
  scripts, v15/v16-compatible tests, a `make_doc` test-data factory, and optional CI. The app is
  initialised as a git repository.
- `verify`: real `bench get-app --soft-link` → `install-app` → `migrate` → `run-tests`, with
  exact commands, exit codes and test counts in the report.
- Frappe Shield rewritten: comprehension loops, string concatenation in SQL, guest APIs with
  `ignore_permissions`, `subprocess(shell=True)`, hard-coded secrets, JS eval/innerHTML, syntax
  errors reported, `# shield: ignore` suppression, `--fail-on` threshold.
- Proper Claude Code plugin (`.claude-plugin/plugin.json` + marketplace), PostToolUse Shield hook,
  16 skills checked against Frappe source, 12 agents, 17 commands.
- CI: unit tests, strict plugin validation, and end-to-end verification of a generated app on
  Frappe v15 and v16.

### Fixed (from 2.x)
- Agents declared `model: claude-3-7-sonnet`, which no longer resolves; agents now inherit the session model.
- `install.sh` was not executable, and `--target claude` copied files where Claude Code does not
  load them. Replaced by marketplace-based install.
- The app builder ignored the prompt and always produced the same template, with DocType folder
  names Frappe could not import (`clinic_ops/` for `ClinicOps`). It also wrote Git tokens into
  `.git/config` and tagged untested code.
- Skills taught invalid naming (`format:AST-.YYYY.-.#####`), claimed Link fields are indexed
  automatically, described per-test rollback, showed `has_permission` hooks granting access, and
  recommended `@frappe.rate_limit` (which does not exist).

### Removed
- The "53 native Python agents", live engine, runtime server and studio. The agents returned
  fixed template text. The last 2.x commit added a Claude call to the prompt builder, but it asks
  for a single DocType as JSON, stores simulated records in SQLite instead of building a Frappe
  app, uses a retired model ID (`claude-3-5-sonnet-20241022`), falls back to templates when the
  call fails, and saves the API key in plain text.
- Mock-based test suite and generated "100% passed" reports, the sample project tested against
  `MockFrappe`, iOS/Windows "installables", and marketing documents with unsupported claims.
- Antigravity target (its plugin format could not be verified).
