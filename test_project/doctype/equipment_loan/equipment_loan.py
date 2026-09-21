import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import getdate, date_diff

class EquipmentLoan(Document):
    def validate(self):
        self.validate_dates()
        self.validate_borrower_eligibility()
        self.validate_items()
        self.calculate_total_value()

    def validate_dates(self):
        if not self.loan_date:
            self.loan_date = frappe.utils.today()
            
        if self.expected_return_date:
            if getdate(self.expected_return_date) < getdate(self.loan_date):
                frappe.throw(
                    _("Expected Return Date ({0}) cannot be before Loan Date ({1}).").format(
                        self.expected_return_date, self.loan_date
                    ),
                    frappe.ValidationError
                )
            
            # Policy check: Maximum loan duration is 30 days
            duration = date_diff(self.expected_return_date, self.loan_date)
            if duration > 30:
                frappe.throw(
                    _("Loan duration ({0} days) exceeds maximum policy limit of 30 days.").format(duration),
                    frappe.ValidationError
                )

    def validate_borrower_eligibility(self):
        if not self.borrower:
            return

        # Check for any active overdue loans for this borrower
        overdue_loans = frappe.get_all(
            "Equipment Loan",
            filters={
                "borrower": self.borrower,
                "status": "Overdue",
                "docstatus": 1
            },
            fields=["name"]
        )
        if overdue_loans:
            overdue_ref = overdue_loans[0].get("name") if isinstance(overdue_loans[0], dict) else getattr(overdue_loans[0], "name", str(overdue_loans[0]))
            frappe.throw(
                _("Borrower {0} has overdue equipment loan ({1}). Return overdue items before requesting new loans.").format(
                    self.borrower, overdue_ref
                ),
                frappe.PermissionError
            )

    def validate_items(self):
        if not self.items:
            frappe.throw(_("At least one hardware item must be added to the loan."), frappe.ValidationError)

        seen_assets = set()
        for row in self.items:
            if row.asset in seen_assets:
                frappe.throw(_("Duplicate item {0} in loan table.").format(row.asset), frappe.ValidationError)
            seen_assets.add(row.asset)

            # Check asset availability
            asset_status = frappe.db.get_value("Loanable Asset", row.asset, "status")
            if not asset_status:
                frappe.throw(_("Asset {0} does not exist.").format(row.asset), frappe.DoesNotExistError)

            if asset_status != "Available" and self.docstatus == 0:
                frappe.throw(
                    _("Asset {0} is currently '{1}' and unavailable for lending.").format(row.asset, asset_status),
                    frappe.ValidationError
                )

    def calculate_total_value(self):
        total = 0.0
        for row in self.items:
            total += float(row.item_value or 0.0)
        self.total_loan_value = total

    def on_submit(self):
        self.status = "Active"
        self.update_asset_statuses(new_status="Loaned Out")

    def on_cancel(self):
        self.status = "Cancelled"
        self.update_asset_statuses(new_status="Available")

    def update_asset_statuses(self, new_status):
        for row in self.items:
            frappe.db.set_value("Loanable Asset", row.asset, "status", new_status)
