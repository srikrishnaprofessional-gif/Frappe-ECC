---
description: Run the Frappe Shield static scanner on a path
argument-hint: "[path] [--fail-on critical|high|medium|low]"
---
Run `frappe-ecc shield $ARGUMENTS` (default path: current directory) and summarise the findings
by severity. For each HIGH or CRITICAL finding, open the code, say whether it is a real problem or
a false positive, and propose the fix.
