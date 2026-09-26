---
name: frappe-client-scripts
description: Production guide for writing reactive Frappe Desk client scripts, form hooks, child table manipulation, dynamic buttons, and dialogs.
---

# Frappe Client Scripts & Desk UI

## 1. Core Desk Event Handlers
```javascript
frappe.ui.form.on('Asset Item', {
    refresh(frm) {
        // 1. Add status indicator badge
        if (frm.doc.status === 'Under Maintenance') {
            frm.page.set_indicator(__('Maintenance Pending'), 'orange');
        }

        // 2. Custom action buttons
        if (!frm.is_new()) {
            frm.add_custom_button(__('Schedule Maintenance'), () => {
                frm.events.open_schedule_dialog(frm);
            }, __('Actions'));
        }

        // 3. Conditional field display
        frm.toggle_display('decommission_reason', frm.doc.status === 'Decommissioned');
        frm.toggle_reqd('decommission_reason', frm.doc.status === 'Decommissioned');
    },

    status(frm) {
        frm.toggle_display('decommission_reason', frm.doc.status === 'Decommissioned');
        frm.toggle_reqd('decommission_reason', frm.doc.status === 'Decommissioned');
    },

    open_schedule_dialog(frm) {
        let d = new frappe.ui.Dialog({
            title: __('Schedule Maintenance'),
            fields: [
                {
                    label: __('Maintenance Type'),
                    fieldname: 'maintenance_type',
                    fieldtype: 'Select',
                    options: 'Routine Check\nRepair\nCalibration',
                    reqd: 1
                },
                {
                    label: __('Scheduled Date'),
                    fieldname: 'scheduled_date',
                    fieldtype: 'Date',
                    default: frappe.datetime.add_days(frappe.datetime.get_today(), 7),
                    reqd: 1
                }
            ],
            primary_action_label: __('Create Schedule'),
            primary_action(values) {
                frappe.call({
                    method: 'your_app.api.maintenance.create_schedule',
                    args: {
                        asset: frm.doc.name,
                        data: values
                    },
                    freeze: true,
                    callback(r) {
                        d.hide();
                        frappe.show_alert({
                            message: __('Maintenance scheduled successfully'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    }
                });
            }
        });
        d.show();
    }
});
```

## 2. Dynamic Child Table Grid Calculations
```javascript
frappe.ui.form.on('Asset Component Item', {
    component_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.component_code) {
            frappe.db.get_value('Component Item', row.component_code, 'standard_cost')
                .then(r => {
                    frappe.model.set_value(cdt, cdn, 'cost', r.message.standard_cost || 0);
                    frm.trigger('calculate_total_cost');
                });
        }
    },
    cost(frm) {
        frm.trigger('calculate_total_cost');
    }
});

frappe.ui.form.on('Asset Item', {
    calculate_total_cost(frm) {
        let total = 0;
        (frm.doc.items || []).forEach(row => {
            total += flt(row.cost);
        });
        frm.set_value('total_component_cost', total);
    }
});
```
