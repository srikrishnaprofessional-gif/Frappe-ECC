---
description: Diagnose and fix a Frappe error, failing test or failing bench command
argument-hint: "<error message, traceback or failing command>"
---
Debug this Frappe problem: $ARGUMENTS

Use the **frappe-debugger** agent. Report the root cause, the fix, and the command output that
shows it now works. If the cause is environmental (redis, missing app, migrate not run), give the
user the exact command instead of changing code.
