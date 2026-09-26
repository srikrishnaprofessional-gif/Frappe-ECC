---
description: Show what Frappe ECC can do and how to start
---
Explain Frappe ECC to the user briefly:

- **Start a new app**: `/frappe-ecc:new-app <requirements>`: model → confirm → generate → verify on a
  real site → implement → test → scan.
- **Work on an existing app**: `/frappe-ecc:add-doctype`, `:api`, `:report`, `:workflow`,
  `:print-format`, `:patch`, `:import-data`.
- **Quality**: `/frappe-ecc:verify` (real install + migrate + tests), `:test`, `:review`,
  `:security`, `:shield`, `:debug`.
- **Ops and docs**: `/frappe-ecc:deploy`, `:docs`.
- **CLI** (also usable without Claude): `frappe-ecc validate | new | add-doctypes | verify | shield | doctor`.
- Skills load automatically when relevant (DocTypes, controllers, hooks, APIs, permissions,
  client scripts, tests, patches, jobs, reports, workflows, print formats, portal, bench, security).
- Agents: frappe-architect, backend-developer, frontend-developer, test-engineer, code-reviewer,
  security-reviewer, debugger, report-builder, workflow-designer, data-engineer, devops, docs-writer.

Then run `frappe-ecc doctor` and show its result.
