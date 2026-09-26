---
description: Design a print format (PDF) for a DocType
argument-hint: "<DocType and what the printout must show>"
---
Create a print format for: $ARGUMENTS

Use the **frappe-frontend-developer** agent with ${CLAUDE_PLUGIN_ROOT}/skills/frappe-print-formats/SKILL.md. Ship it as a
standard print format in the app's module. Check it renders as PDF (`frappe.get_print(..., as_pdf=True)`
in `bench console` or Print → PDF) and report how it looks and any limits of the PDF engine.
