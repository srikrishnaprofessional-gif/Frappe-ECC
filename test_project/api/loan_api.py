import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def process_return(loan_id: str, actual_return_date: str = None, return_notes: str = None):
    """
    POST /api/method/equipment_loan.api.loan_api.process_return
    Processes equipment return and releases inventory back to Available.
    """
    # 1. Authorization check
    frappe.only_for(["System Manager", "IT Asset Manager"])

    # 2. Input validation
    if not loan_id:
        frappe.throw(_("Loan ID is required."), frappe.ValidationError)

    if not frappe.db.exists("Equipment Loan", loan_id):
        frappe.throw(_("Equipment Loan {0} not found.").format(loan_id), frappe.DoesNotExistError)

    doc = frappe.get_doc("Equipment Loan", loan_id)

    # 3. State verification
    if doc.docstatus != 1 or doc.status not in ["Active", "Overdue"]:
        frappe.throw(
            _("Cannot process return for loan with status '{0}'. Must be Active or Overdue.").format(doc.status),
            frappe.ValidationError
        )

    # 4. Apply return state
    doc.actual_return_date = actual_return_date or frappe.utils.today()
    doc.return_notes = frappe.utils.escape_html(return_notes or _("Returned in good order."))
    doc.status = "Returned"
    
    # Bypass submittable lock on specific audit fields
    doc.flags.ignore_validate_update_after_submit = True
    doc.save(ignore_permissions=True)

    # 5. Release assets back to inventory
    for item in doc.items:
        frappe.db.set_value("Loanable Asset", item.asset, "status", "Available")

    return {
        "status": "success",
        "loan_id": doc.name,
        "returned_on": str(doc.actual_return_date),
        "items_returned": len(doc.items)
    }
