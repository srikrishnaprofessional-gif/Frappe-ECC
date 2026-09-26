# Frappe JavaScript & Desk Client Script Rules

## 1. Form Event Standard Pattern
Always namespace client scripts using `frappe.ui.form.on`:
```javascript
frappe.ui.form.on('Asset Ticket', {
    setup(frm) {
        // Runs once when the form route is initialized
    },
    onload(frm) {
        // Runs whenever document loads in form
    },
    refresh(frm) {
        // Triggered after load and save
        if (!frm.is_new() && frm.doc.status === 'Open') {
            frm.add_custom_button(__('Resolve Ticket'), () => {
                frm.events.resolve_ticket(frm);
            }, __('Actions'));
        }
    },
    validate(frm) {
        // Client-side pre-save validation
        if (frm.doc.expected_resolution_date < frappe.datetime.get_today()) {
            frappe.msgprint(__('Expected Resolution Date cannot be in the past'));
            frappe.validated = false;
        }
    },
    resolve_ticket(frm) {
        frappe.call({
            method: 'your_app.api.tickets.resolve',
            args: { ticket_id: frm.doc.name },
            freeze: true,
            freeze_message: __('Resolving ticket...'),
            callback(r) {
                if (!r.exc) {
                    frm.reload_doc();
                }
            }
        });
    }
});
```

## 2. Child Table Event Handling
Define child table events with table DocType name:
```javascript
frappe.ui.form.on('Asset Maintenance Item', {
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.db.get_value('Item', row.item_code, ['item_name', 'standard_rate'])
                .then(r => {
                    let values = r.message;
                    frappe.model.set_value(cdt, cdn, 'item_name', values.item_name);
                    frappe.model.set_value(cdt, cdn, 'rate', values.standard_rate);
                });
        }
    },
    qty(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', (row.qty || 0) * (row.rate || 0));
        frm.trigger('calculate_total');
    }
});
```

## 3. UI Commandments
- **Never manipulate DOM directly**: Avoid `$('input[name="..."]')`. Use Desk APIs (`frm.set_value`, `frm.set_df_property`, `frm.toggle_display`, `frm.toggle_reqd`).
- **Use `frappe.model.set_value` for Child Tables**: Direct row mutation won't trigger dirty state or recalculations.
- **Always provide feedback**: Use `frappe.show_alert({ message: __('...'), indicator: 'green' })` or `frm.dashboard`.
