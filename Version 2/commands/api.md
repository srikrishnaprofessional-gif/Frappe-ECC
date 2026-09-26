---
description: Build a secure whitelisted API endpoint or external integration in a Frappe app
argument-hint: "<what the endpoint or integration should do>"
---
Build this API or integration: $ARGUMENTS

Use the **frappe-backend-developer** agent, following ${CLAUDE_PLUGIN_ROOT}/skills/frappe-api/SKILL.md. Every endpoint
must check permissions, restrict HTTP methods for writes, validate input, and have tests for both
allowed and denied callers. Guest endpoints need rate limiting. Report the endpoint paths, an
example request for each, and test results.
