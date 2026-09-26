---
description: Import CSV or Excel data into Frappe DocTypes with mapping and reconciliation
argument-hint: "<file path> [target DocType]"
---
Import this data: $ARGUMENTS

Use the **frappe-data-engineer** agent. Show the user the column mapping and the rows that would be
rejected, and confirm before loading. Load into a development or copy site first. Report counts
loaded and rejected, and the reconciliation result.
