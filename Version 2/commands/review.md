---
description: Review Frappe code changes for bugs, conventions and performance
argument-hint: "[path, branch or PR]"
---
Review Frappe code: $ARGUMENTS (default: uncommitted changes plus commits not on the main branch).

Use the **frappe-code-reviewer** agent on the target. Then present its findings to the user
grouped by severity, with file:line links. Offer to fix the confirmed ones.
