import frappe
from frappe.model.document import Document
from frappe import _

class LoanableAsset(Document):
    def validate(self):
        self.validate_serial_no()

    def validate_serial_no(self):
        if not self.serial_no:
            frappe.throw(_("Serial Number is mandatory."))
        # Clean whitespace
        self.serial_no = self.serial_no.strip().upper()
