# /frappe:build-e2e

**Purpose**: Execute fullstack feature synthesis, generating the entire vertical stack (schema, controller, client script, hooks, APIs, tests, patches) without placeholders.

## Usage
`/frappe:build-e2e "<feature or spec path>"`

## Execution Workflow
1. Invoke the **frappe-fullstack-developer** agent.
2. Activate `frappe-fullstack-scaffolding`, `frappe-doctype-design`, `frappe-orm-and-queries`, and `frappe-client-scripts`.
3. Synthesize the complete vertical feature:
   - DocType `.json` schema with permissions and indexes.
   - Python controller `.py` with lifecycle hooks and validations.
   - Desk JavaScript `.js` with event listeners, buttons, and dialogs.
   - Updates to `hooks.py` and `modules.txt`.
   - Whitelisted REST API methods.
   - Complete `FrappeTestCase` unit tests.
   - Database migration patch in `patches.txt`.
4. Run `frappe-shield` to verify zero security or transaction flaws.
