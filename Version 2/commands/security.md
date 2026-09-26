---
description: Security audit of a Frappe app with Frappe Shield plus manual review
argument-hint: "[app path]"
---
Run a security review of the Frappe app at: $ARGUMENTS (default: the app in the current directory).

Use the **frappe-security-reviewer** agent. Present confirmed problems first (with exploit
scenario and fix), then suspected ones, then Shield findings triaged as false positives with
reasons. Offer to fix confirmed problems.
