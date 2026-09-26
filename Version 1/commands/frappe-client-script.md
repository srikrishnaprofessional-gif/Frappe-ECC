# /frappe:client-script

**Purpose**: Create or refactor a Frappe Desk form client script with UI events, custom buttons, and dynamic fields.

## Usage
`/frappe:client-script "<DocType Name>"`

## Execution Workflow
1. Invoke the **frappe-desk-builder** agent.
2. Structure the client script using `frappe.ui.form.on("<DocType>", { ... })`.
3. Implement `onload`, `refresh`, `validate`, and field trigger functions.
4. If child tables exist, bind child table field events using `frappe.model.set_value`.
5. Avoid direct DOM selection (`$`). Use `frm.set_df_property` and native dialogs.
