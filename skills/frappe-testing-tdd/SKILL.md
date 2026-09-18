---
name: frappe-testing-tdd
description: Complete framework for Test-Driven Development (TDD), FrappeTestCase, test records, fixtures, and CI automation.
---

# Frappe Testing & TDD Workflow

## 1. Test Case Structure
Tests in Frappe inherit from `frappe.tests.utils.FrappeTestCase`. Frappe isolates each test with database savepoints and automatically rolls back changes.

Example: `your_app/your_module/doctype/asset_item/test_asset_item.py`
```python
import frappe
from frappe.tests.utils import FrappeTestCase

class TestAssetItem(FrappeTestCase):
    def setUp(self):
        # Create prerequisite fixtures if not present
        if not frappe.db.exists("Asset Category", "IT Hardware"):
            frappe.get_doc({
                "doctype": "Asset Category",
                "category_name": "IT Hardware"
            }).insert(ignore_permissions=True)

    def test_asset_creation_and_autoname(self):
        doc = frappe.get_doc({
            "doctype": "Asset Item",
            "asset_name": "MacBook Pro M3",
            "asset_category": "IT Hardware",
            "serial_no": "MBP-M3-99901"
        }).insert()

        self.assertTrue(doc.name.startswith("AST-"))
        self.assertEqual(doc.status, "Draft")

    def test_duplicate_serial_no_rejection(self):
        doc1 = frappe.get_doc({
            "doctype": "Asset Item",
            "asset_name": "ThinkPad X1",
            "asset_category": "IT Hardware",
            "serial_no": "TP-X1-DUPE"
        }).insert()

        doc2 = frappe.get_doc({
            "doctype": "Asset Item",
            "asset_name": "ThinkPad X1 Duplicate",
            "asset_category": "IT Hardware",
            "serial_no": "TP-X1-DUPE"
        })

        self.assertRaises(frappe.DuplicateEntryError, doc2.insert)

    def test_warranty_validation(self):
        doc = frappe.get_doc({
            "doctype": "Asset Item",
            "asset_name": "Monitor 27in",
            "asset_category": "IT Hardware",
            "serial_no": "MN-27-01",
            "purchase_date": "2026-05-10",
            "warranty_expiry_date": "2025-05-10" # Invalid: expiry before purchase
        })

        self.assertRaises(frappe.ValidationError, doc.insert)
```

## 2. Running Tests
Run tests via Bench:
```bash
# Run tests for entire app
bench --site itam.localhost run-tests --app your_app

# Run tests for specific DocType
bench --site itam.localhost run-tests --app your_app --doctype "Asset Item"

# Run tests with failfast
bench --site itam.localhost run-tests --app your_app --failfast
```
