---
description: Write missing tests for a Frappe app or DocType and run them
argument-hint: "<app, DocType or feature>"
---
Add and run tests for: $ARGUMENTS

Use the **frappe-test-engineer** agent (it follows ${CLAUDE_PLUGIN_ROOT}/skills/frappe-testing/SKILL.md). Report the
command run, tests passed/failed, the rules now covered and anything still untested. If a test
exposes a bug, show the failing test and ask before changing application code.
