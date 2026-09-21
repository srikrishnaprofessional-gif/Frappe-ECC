frappe.ui.form.on('Equipment Loan', {
    setup(frm) {
        frm.set_query('borrower', function() {
            return {
                filters: { 'status': 'Active' }
            };
        });

        frm.set_query('asset', 'items', function() {
            return {
                filters: { 'status': 'Available' }
            };
        });
    },

    refresh(frm) {
        // Dynamic status indicators
        if (frm.doc.status === 'Active') {
            frm.page.set_indicator(__('Active Loan'), 'green');
        } else if (frm.doc.status === 'Overdue') {
            frm.page.set_indicator(__('Overdue'), 'red');
        } else if (frm.doc.status === 'Returned') {
            frm.page.set_indicator(__('Returned'), 'blue');
        }

        // Return button on active submitted loans
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Active') {
            frm.add_custom_button(__('Process Return'), () => {
                frm.events.open_return_dialog(frm);
            }, __('Actions'));
        }
    },

    open_return_dialog(frm) {
        let d = new frappe.ui.Dialog({
            title: __('Process Equipment Return'),
            fields: [
                {
                    label: __('Actual Return Date'),
                    fieldname: 'actual_return_date',
                    fieldtype: 'Date',
                    default: frappe.datetime.get_today(),
                    reqd: 1
                },
                {
                    label: __('Inspector Notes'),
                    fieldname: 'return_notes',
                    fieldtype: 'Small Text',
                    reqd: 1
                }
            ],
            primary_action_label: __('Confirm Return'),
            primary_action(values) {
                frappe.call({
                    method: 'equipment_loan.api.loan_api.process_return',
                    args: {
                        loan_id: frm.doc.name,
                        actual_return_date: values.actual_return_date,
                        return_notes: values.return_notes
                    },
                    freeze: true,
                    freeze_message: __('Processing return and updating inventory...'),
                    callback(r) {
                        d.hide();
                        if (!r.exc) {
                            frappe.show_alert({
                                message: __('Equipment returned successfully!'),
                                indicator: 'green'
                            });
                            frm.reload_doc();
                        }
                    }
                });
            }
        });
        d.show();
    }
});

frappe.ui.form.on('Equipment Loan Item', {
    items_add(frm) {
        frm.trigger('calculate_total');
    },
    items_remove(frm) {
        frm.trigger('calculate_total');
    },
    item_value(frm) {
        frm.trigger('calculate_total');
    },
    asset(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.asset) {
            frappe.db.get_value('Loanable Asset', row.asset, ['serial_no', 'replacement_value'])
                .then(r => {
                    let val = r.message;
                    frappe.model.set_value(cdt, cdn, 'serial_no', val.serial_no);
                    frappe.model.set_value(cdt, cdn, 'item_value', val.replacement_value);
                    frm.trigger('calculate_total');
                });
        }
    }
});

frappe.ui.form.on('Equipment Loan', {
    calculate_total(frm) {
        let total = 0;
        (frm.doc.items || []).forEach(row => {
            total += flt(row.item_value);
        });
        frm.set_value('total_loan_value', total);
    }
});
