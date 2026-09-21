---
description: Perform autonomous root cause analysis and apply self-healing surgical code patches to failing unit tests, browser tests, or Frappe Shield security warnings.
---

# /frappe:heal

Autonomous root-cause analysis and auto-repair for Frappe applications.

## Usage
```
/frappe:heal [error_traceback_or_log_path]
```

## Description
Invokes `frappe-self-healing-debugger` to parse Python tracebacks, database constraint errors, or AST security violations, isolate the exact line number, and apply minimal, non-destructive surgical patches until all tests pass 100%.
