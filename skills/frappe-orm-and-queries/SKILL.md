---
name: frappe-orm-and-queries
description: Comprehensive guidelines, patterns, and performance recipes for Frappe ORM, Document operations, and QueryBuilder (frappe.qb).
---

# Frappe ORM & QueryBuilder Mastery

## 1. Document Lifecycle Operations
```python
import frappe

# 1. Loading & Modifying
doc = frappe.get_doc("Asset Item", "AST-2026-00001")
doc.status = "In Use"
doc.append("items", {
    "component_name": "SSD 1TB",
    "serial_no": "SN-99882"
})
doc.save() # Triggers validate(), before_save(), on_update()

# 2. Inserting
new_doc = frappe.get_doc({
    "doctype": "Asset Item",
    "asset_name": "Dell Precision 5570",
    "asset_category": "Laptops",
    "serial_no": "DL-5570-X1"
})
new_doc.insert()

# 3. Submitting & Cancelling (Submittable DocTypes only)
doc.submit() # docstatus becomes 1
doc.cancel() # docstatus becomes 2
```

## 2. Fast Database Lookups
When full controller validation isn't needed:
```python
# Single field
serial = frappe.db.get_value("Asset Item", "AST-2026-00001", "serial_no")

# Multiple fields as dict
asset_info = frappe.db.get_value(
    "Asset Item",
    {"serial_no": "DL-5570-X1"},
    ["name", "status", "asset_category"],
    as_dict=True
)

# Updating without triggering controller save
frappe.db.set_value("Asset Item", "AST-2026-00001", "status", "Under Maintenance")

# Check existence
if frappe.db.exists("Asset Item", {"serial_no": "DL-5570-X1"}):
    pass
```

## 3. QueryBuilder (`frappe.qb`)
Frappe's modern, type-safe query builder prevents SQL injection completely:
```python
Asset = frappe.qb.DocType("Asset Item")
Category = frappe.qb.DocType("Asset Category")

query = (
    frappe.qb.from_(Asset)
    .inner_join(Category)
    .on(Asset.asset_category == Category.name)
    .select(
        Asset.name,
        Asset.asset_name,
        Asset.status,
        Category.category_name
    )
    .where(Asset.status == "In Use")
    .orderby(Asset.creation, order=frappe.qb.desc)
    .limit(50)
)

data = query.run(as_dict=True)
```
