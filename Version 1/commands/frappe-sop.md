---
description: Author a comprehensive, visual Working Standard Operating Procedure (Working SOP) for any Frappe project with step-by-step operator guides, screenshots, and business rules.
---

# /frappe:sop

Author an executive Working Standard Operating Procedure (SOP) with UI screenshots for a Frappe project.

## Usage
```
/frappe:sop [project_path]
```

## Examples
```
/frappe:sop test_project
/frappe:sop path/to/custom_frappe_app
```

## Description
Invokes `frappe-working-sop-author` to scan the application's DocTypes, business logic, and UI prototype, capture annotated UI screenshots, and author complete, publication-grade Working SOP manuals in Markdown (`.md`), Word (`.docx`), and PDF (`.pdf`) formats.
