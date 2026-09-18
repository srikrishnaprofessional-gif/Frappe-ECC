# /frappe:prototype

**Purpose**: Generate a self-contained, clickable interactive HTML prototype replicating Frappe Desk UI for immediate stakeholder validation.

## Usage
`/frappe:prototype "<Feature or DocType Name>"`

## Execution Workflow
1. Invoke the **frappe-interactive-prototyper** agent.
2. Activate the `frappe-wireframing-prototyping` skill.
3. Generate a single-file interactive prototype with Tailwind CSS and Vue 3 (CDN):
   - Document state transitions (Draft -> Submitted -> Cancelled).
   - Clickable action buttons popping up native-style modal dialogs.
   - Interactive child table grids with dynamic auto-calculation of totals.
4. Save file to `<app_root>/prototypes/<feature_slug>_prototype.html`.
