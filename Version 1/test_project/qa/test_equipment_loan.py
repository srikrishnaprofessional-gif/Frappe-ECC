#!/usr/bin/env python3
"""
Automated Test Suite for Equipment Loan & Return System
Validates business logic, validations, lifecycle hooks, and return API.
Executable standalone with standard unittest or inside bench test runner.
"""

import os
import sys
import unittest
from datetime import datetime, date, timedelta

# Ensure project root is in sys.path for test_project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create Mock Frappe Environment for standalone execution if frappe is not loaded
try:
    import frappe
except ImportError:
    class MockFrappe:
        class ValidationError(Exception): pass
        class PermissionError(Exception): pass
        class DoesNotExistError(Exception): pass
        class DuplicateEntryError(Exception): pass

        class db:
            _data = {
                "Loanable Asset": {
                    "AST-001": {"name": "AST-001", "status": "Available", "serial_no": "MBP-M3-9901", "replacement_value": 3499.00},
                    "AST-002": {"name": "AST-002", "status": "Available", "serial_no": "MN-4K-2210", "replacement_value": 1599.00},
                    "AST-003": {"name": "AST-003", "status": "Available", "serial_no": "KM-KIT-102", "replacement_value": 299.00},
                    "AST-004": {"name": "AST-004", "status": "Loaned Out", "serial_no": "DL-6K-4001", "replacement_value": 2199.00}
                }
            }

            @classmethod
            def get_value(cls, doctype, name, fieldname):
                doc = cls._data.get(doctype, {}).get(name, {})
                return doc.get(fieldname)

            @classmethod
            def set_value(cls, doctype, name, fieldname, value):
                if doctype in cls._data and name in cls._data[doctype]:
                    cls._data[doctype][name][fieldname] = value

            @classmethod
            def exists(cls, doctype, name):
                return name in cls._data.get(doctype, {})

        @staticmethod
        def throw(msg, exc=ValidationError):
            raise exc(msg)

        @staticmethod
        def _(msg):
            return msg

        class utils:
            @staticmethod
            def today():
                return date.today().strftime("%Y-%m-%d")

            @staticmethod
            def escape_html(text):
                return text

        @staticmethod
        def get_all(doctype, filters=None, fields=None):
            if doctype == "Equipment Loan" and filters and filters.get("borrower") == "EMP-00105":
                return [{"name": "LOAN-2026-00008"}]
            return []

    class MockDocument:
        def __init__(self, **kwargs):
            self.docstatus = 0
            self.name = kwargs.get("name", "MOCK-DOC-001")
            for k, v in kwargs.items():
                setattr(self, k, v)

        def submit(self):
            if hasattr(self, "validate"):
                self.validate()
            if hasattr(self, "before_submit"):
                self.before_submit()
            setattr(self, "docstatus", 1)
            if hasattr(self, "on_submit"):
                self.on_submit()

        def cancel(self):
            if hasattr(self, "before_cancel"):
                self.before_cancel()
            setattr(self, "docstatus", 2)
            if hasattr(self, "on_cancel"):
                self.on_cancel()

    sys.modules["frappe"] = MockFrappe()
    sys.modules["frappe.model.document"] = type("DocumentModule", (), {"Document": MockDocument})
    sys.modules["frappe.utils"] = type("UtilsModule", (), {
        "getdate": lambda d: datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d,
        "date_diff": lambda d1, d2: (datetime.strptime(d1, "%Y-%m-%d").date() - datetime.strptime(d2, "%Y-%m-%d").date()).days
    })
    import frappe

# Import project modules
from test_project.doctype.equipment_loan.equipment_loan import EquipmentLoan

class MockChildRow:
    def __init__(self, asset, item_value=0.0):
        self.asset = asset
        self.item_value = item_value

class TestEquipmentLoanSystem(unittest.TestCase):
    def setUp(self):
        # Reset DB status
        frappe.db.set_value("Loanable Asset", "AST-001", "status", "Available")
        frappe.db.set_value("Loanable Asset", "AST-002", "status", "Available")
        frappe.db.set_value("Loanable Asset", "AST-004", "status", "Loaned Out")

    def test_ts01_happy_path_creation_and_value(self):
        """TS-01: Valid loan creation and total value calculation"""
        loan = EquipmentLoan()
        loan.name = "LOAN-2026-00042"
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-10-05"
        loan.items = [
            MockChildRow("AST-001", 3499.00),
            MockChildRow("AST-002", 1599.00)
        ]
        loan.validate()
        self.assertEqual(loan.total_loan_value, 5098.00)

    def test_ts02_reject_invalid_past_return_date(self):
        """TS-02: Expected Return Date cannot be before Loan Date"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-10" # Past date
        loan.items = [MockChildRow("AST-001", 3499.00)]
        with self.assertRaises(frappe.ValidationError) as cm:
            loan.validate()
        self.assertIn("cannot be before Loan Date", str(cm.exception))

    def test_ts03_reject_loan_exceeding_30_days(self):
        """TS-03: Loan duration policy maximum 30 days"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-01"
        loan.expected_return_date = "2026-10-15" # 44 days
        loan.items = [MockChildRow("AST-001", 3499.00)]
        with self.assertRaises(frappe.ValidationError) as cm:
            loan.validate()
        self.assertIn("exceeds maximum policy limit of 30 days", str(cm.exception))

    def test_ts04_reject_unavailable_asset(self):
        """TS-04: Cannot borrow asset marked Loaned Out"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = [MockChildRow("AST-004", 2199.00)] # AST-004 is Loaned Out
        with self.assertRaises(frappe.ValidationError) as cm:
            loan.validate()
        self.assertIn("is currently 'Loaned Out' and unavailable", str(cm.exception))

    def test_ts05_reject_duplicate_items(self):
        """TS-05: Reject duplicate item codes in table"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = [
            MockChildRow("AST-001", 3499.00),
            MockChildRow("AST-001", 3499.00) # Duplicate!
        ]
        with self.assertRaises(frappe.ValidationError) as cm:
            loan.validate()
        self.assertIn("Duplicate item AST-001 in loan table", str(cm.exception))

    def test_ts06_block_borrower_with_overdue_loan(self):
        """TS-06: Reject loan if borrower has overdue items"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00105" # Has overdue loan
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = [MockChildRow("AST-001", 3499.00)]
        with self.assertRaises(frappe.PermissionError) as cm:
            loan.validate()
        self.assertIn("has overdue equipment loan", str(cm.exception))

    def test_ts07_submit_updates_asset_status_to_loaned_out(self):
        """TS-07: On submit, asset status flips Available -> Loaned Out"""
        loan = EquipmentLoan()
        loan.name = "LOAN-2026-00042"
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = [MockChildRow("AST-001", 3499.00)]
        loan.submit()
        self.assertEqual(loan.status, "Active")
        self.assertEqual(frappe.db.get_value("Loanable Asset", "AST-001", "status"), "Loaned Out")

    def test_ts08_cancel_reverses_asset_status_to_available(self):
        """TS-08: On cancel, asset status reverses Loaned Out -> Available"""
        loan = EquipmentLoan()
        loan.name = "LOAN-2026-00042"
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = [MockChildRow("AST-001", 3499.00)]
        loan.submit()
        loan.cancel()
        self.assertEqual(loan.status, "Cancelled")
        self.assertEqual(frappe.db.get_value("Loanable Asset", "AST-001", "status"), "Available")

    def test_ts09_empty_items_rejection(self):
        """TS-09: Loan must contain at least one item"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = []
        with self.assertRaises(frappe.ValidationError) as cm:
            loan.validate()
        self.assertIn("At least one hardware item must be added", str(cm.exception))

    def test_ts10_nonexistent_asset_rejection(self):
        """TS-10: Reject non-existent asset ID"""
        loan = EquipmentLoan()
        loan.borrower = "EMP-00104"
        loan.loan_date = "2026-09-21"
        loan.expected_return_date = "2026-09-28"
        loan.items = [MockChildRow("AST-NONEXISTENT", 100.00)]
        with self.assertRaises(frappe.DoesNotExistError) as cm:
            loan.validate()
        self.assertIn("does not exist", str(cm.exception))

if __name__ == "__main__":
    unittest.main(verbosity=2)
