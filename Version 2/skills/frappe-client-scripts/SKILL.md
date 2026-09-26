---
name: frappe-client-scripts
description: Write Frappe Desk form and list scripts in JavaScript - frappe.ui.form.on events, child table events, set_query filters, custom buttons, dialogs, list view settings, and frappe.call. Use when changing how a DocType's form or list behaves in the browser.
---

# Form and list scripts

A DocType's form script lives next to its JSON: `<doctype>/<doctype>.js`. For another app's
DocType, add `doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}` in hooks.py. After
changing JS, run `bench build --app <app>` (or keep `bench watch` running) and reload the browser.

Client scripts improve the user experience. They do not enforce rules: anything a script
blocks, an API call can still do. Put every rule that matters in the Python controller as well.

## Form events

```javascript
frappe.ui.form.on("Clinic Appointment", {
	setup(frm) {
		// runs once per form; set queries here
		frm.set_query("doctor", () => ({ filters: { is_active: 1 } }));
		frm.set_query("item", "prescriptions", (doc, cdt, cdn) => ({ filters: { disabled: 0 } }));
	},

	refresh(frm) {
		// runs on every load and after save
		if (frm.doc.docstatus === 1 && frm.doc.status === "Scheduled") {
			frm.add_custom_button(__("Mark Completed"), () => mark_completed(frm), __("Actions"));
		}
		frm.toggle_display("diagnosis", !frm.is_new());
		frm.set_intro(frm.doc.status === "No Show" ? __("Patient did not attend") : "");
	},

	// field change handler: named after the fieldname
	patient(frm) {
		if (!frm.doc.patient) return;
		frappe.db.get_value("Clinic Patient", frm.doc.patient, "allergies").then(({ message }) => {
			if (message?.allergies) frappe.msgprint(__("Allergies: {0}", [message.allergies]));
		});
	},

	validate(frm) {
		// runs before save; throw to stop it
		if (!frm.doc.prescriptions?.length && frm.doc.status === "Completed") {
			frappe.throw(__("Add at least one prescription"));
		}
	},
});
```

Common events: `setup`, `onload`, `refresh`, `validate`, `before_save`, `after_save`,
`before_submit`, `on_submit`, `before_cancel`, `after_cancel`, `timeline_refresh`, and one per fieldname.

## Child table events

```javascript
frappe.ui.form.on("Clinic Prescription Item", {
	days(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "total_doses", (row.days || 0) * (row.per_day || 0));
	},
	prescriptions_remove(frm) {
		// <tablefieldname>_add / _remove fire on row add/remove
		frm.trigger("recalculate");
	},
});
```

Set child values with `frappe.model.set_value(cdt, cdn, field, value)` so the grid refreshes.
Set parent values with `frm.set_value("field", value)`, which returns a promise.

## Useful form APIs

| Call | Does |
|---|---|
| `frm.set_value(field, value)` | set and trigger that field's handler |
| `frm.set_df_property(field, "read_only", 1)` | change a field property for this form |
| `frm.toggle_reqd / toggle_enable / toggle_display(field, bool)` | quick property toggles |
| `frm.add_custom_button(label, fn, group)` | button in the toolbar, optionally in a group |
| `frm.call("method_name", args)` | call a `@frappe.whitelist()` method on the document's controller class |
| `frm.reload_doc()` | reload after server-side changes |
| `frm.is_new()`, `frm.is_dirty()` | state checks |
| `frappe.new_doc("DocType", { field: value })` | open a new form with values |

Prefer DocType properties (`depends_on`, `mandatory_depends_on`, `read_only_depends_on`, e.g.
`eval:doc.status=="Completed"`) over scripts for show/hide/required rules.

## Dialogs

```javascript
function mark_completed(frm) {
	const d = new frappe.ui.Dialog({
		title: __("Complete Appointment"),
		fields: [
			{ fieldname: "diagnosis", fieldtype: "Small Text", label: __("Diagnosis"), reqd: 1 },
			{ fieldname: "follow_up", fieldtype: "Date", label: __("Follow-up Date") },
		],
		primary_action_label: __("Complete"),
		primary_action(values) {
			frm.call("mark_completed", values).then(() => {
				d.hide();
				frm.reload_doc();
			});
		},
	});
	d.show();
}
```

The matching controller method:

```python
@frappe.whitelist()
def mark_completed(self, diagnosis, follow_up=None):
	self.check_permission("write")
	self.db_set({"status": "Completed", "diagnosis": diagnosis, "follow_up": follow_up})
```

## List view

`<doctype>/<doctype>_list.js`:

```javascript
frappe.listview_settings["Clinic Appointment"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const colors = { Scheduled: "blue", Completed: "green", "No Show": "red" };
		return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
	},
	onload(listview) {
		listview.page.add_inner_button(__("Today"), () => listview.filter_area.add([["Clinic Appointment", "appointment_date", "=", frappe.datetime.get_today()]]));
	},
};
```

## Rules

- Wrap user-visible strings in `__()`; use `{0}` placeholders, never string concatenation.
- Escape values you insert as HTML: `frappe.utils.escape_html(value)`.
- Don't call the server in a loop. Fetch once with `frappe.db.get_list` or a whitelisted method.
- To wait for a server check before saving, return the promise from `validate` or `before_save`; Frappe waits for it.
