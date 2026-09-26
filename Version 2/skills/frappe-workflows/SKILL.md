---
name: frappe-workflows
description: Add approval flows and automation to Frappe DocTypes without custom code - Workflow (states, transitions, roles, conditions), Notification (email/system alerts on events or dates), Assignment Rule, Auto Repeat, and shipping them as fixtures. Use for approvals, alerts, reminders, escalations and task routing.
---

# Workflows, notifications and assignment

These are configuration records, not code. Build them in Desk on a development site, then ship
them with the app as fixtures so every site gets the same setup.

## Workflow

A **Workflow** record attaches a state machine to one DocType:

| Part | Meaning |
|---|---|
| `document_type` | The DocType it controls. Only one active workflow per DocType |
| `workflow_state_field` | Field holding the state (default `workflow_state`; Frappe creates a Custom Field if the DocType has none) |
| States (`Workflow Document State`) | `state` (a **Workflow State** record), `doc_status` (0 draft, 1 submitted, 2 cancelled), `allow_edit` (role that may edit in this state), optional `update_field` / `update_value` |
| Transitions (`Workflow Transition`) | `state` → `action` → `next_state`, `allowed` role, optional `condition` (Python expression, e.g. `doc.grand_total > 50000`), `allow_self_approval` |

Rules:
- A state with `doc_status` 1 or 2 requires a submittable DocType. Moving to a `doc_status` 1
  state submits the document; moving to 2 cancels it.
- Every `state` must exist as a **Workflow State** record and every `action` as a **Workflow
  Action Master** record. Frappe ships common ones (Pending, Approved, Rejected; Approve, Reject,
  Review). Create others and include them in fixtures.
- While a workflow is active, users change state only through the action buttons. Submit/Cancel
  buttons are replaced by transitions.
- Conditions are evaluated with `frappe.safe_eval`; keep them simple and use `doc.<field>`.
- Transitions show up for users in the **Workflow Action** list and in email if "Send Email
  Alert" is on.

Example: `Draft (0) --Submit for Approval [Clinic Receptionist]--> Pending (0)`,
`Pending --Approve [Clinic Doctor]--> Approved (1)`, `Pending --Reject [Clinic Doctor]--> Rejected (0)`.

Server-side hooks still run: submitting through a workflow calls `before_submit` / `on_submit`.
To react to a specific state, check `doc.has_value_changed("workflow_state")` in `on_update`.

## Notification

A **Notification** record sends email, a system notification, or SMS when:
- a document is created, saved, submitted or cancelled (`event`: New, Save, Submit, Cancel);
- a field changes to a value (`Value Change`) or a condition becomes true (`condition`);
- a date field is N days before or after today (`Days Before` / `Days After`, checked daily);
- a custom method fires (`Method`: the event name, e.g. `on_update`).

Recipients can be fixed emails, roles, or fields on the document (e.g. `owner`, a Link to User,
or an email field). Subject and message are Jinja templates with `doc` in context:

```jinja
Appointment {{ doc.name }} for {{ doc.patient_name }} on {{ frappe.utils.formatdate(doc.appointment_date) }}
```

Email needs a working outgoing Email Account on the site.

## Assignment Rule

An **Assignment Rule** assigns documents to users automatically: pick the DocType, an
`assign_condition` (e.g. `status == "Open"`), an optional `unassign_condition`, and a strategy
(Round Robin, Load Balancing, or Based on Field). Assigned users see the document in their ToDo
list. Use this for queues such as support tickets or approvals that need an owner.

## Other built-ins worth knowing

- **Auto Repeat**: recurring copies of a document (monthly invoices). Enable `allow_auto_repeat` on the DocType.
- **Service Level Agreement** (ships with ERPNext, not Frappe): response/resolution deadlines
  with priorities and working hours. Without ERPNext, store a `due_by` Datetime on the document,
  set it in `validate`, and escalate from a scheduled job or a `Days After` Notification.
- **Server Script** / **Client Script** DocTypes: site-level scripts made in the UI. In an app,
  write real controllers and form scripts instead so the code is versioned and tested.

## Ship as fixtures

```python
# hooks.py (order matters: states and actions before the workflow)
fixtures = [
	{"dt": "Workflow State", "filters": [["name", "in", ["Pending Doctor Review"]]]},
	{"dt": "Workflow Action Master", "filters": [["name", "in", ["Send to Doctor"]]]},
	{"dt": "Workflow", "filters": [["name", "in", ["Clinic Appointment Approval"]]]},
	{"dt": "Notification", "filters": [["name", "in", ["Appointment Reminder"]]]},
	{"dt": "Assignment Rule", "filters": [["name", "in", ["Appointment Triage"]]]},
]
```

Then `bench --site <dev-site> export-fixtures --app <app>`, commit `<app>/fixtures/`, and verify
on a fresh site with `bench --site <site> migrate`.

Alternatively, standard Notifications can live in the app's module folder: set `is_standard`
with developer mode on and Frappe writes them to `<module>/notification/<name>/`.
