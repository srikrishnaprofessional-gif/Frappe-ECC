# /frappe:hook

**Purpose**: Register and wire document events, scheduler cron jobs, or method overrides in `hooks.py`.

## Usage
`/frappe:hook [doc-event | cron | override | fixture]`

## Execution Workflow
1. Activate `frappe-hooks-and-events` skill.
2. Read `<your_app>/hooks.py`.
3. Add the required hook structure:
   - For doc events: add to `doc_events = { "<DocType>": { "<event>": "<handler_path>" } }`.
   - For cron: add to `scheduler_events = { "<interval>": ["<handler_path>"] }`.
   - For overrides: add to `override_doctype_class`.
4. Scaffold the target Python handler function in the specified path with full type signatures and docstrings.
