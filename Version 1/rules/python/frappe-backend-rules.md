# Frappe Python Backend Guidelines

## 1. Controller Method Lifecycle
Use appropriate lifecycle methods in DocType controllers:
```python
from frappe.model.document import Document
import frappe
from frappe import _

class AssetTicket(Document):
    def before_insert(self):
        # Set default values, auto-generate sequences
        pass

    def validate(self):
        # Core validation logic: assertions, calculations, date checks
        self.validate_dates()
        self.calculate_totals()

    def before_save(self):
        # Last minute adjustments before DB flush
        pass

    def on_update(self):
        # Document is saved in DB. Update related documents, clear caches.
        pass

    def on_submit(self):
        # Submittable doc logic: create ledger entries, notify external systems
        pass

    def on_cancel(self):
        # Reverse entries, reset linked status
        pass
```

## 2. ORM & Query Efficiency
- **Avoid N+1 Queries**: Never call `frappe.get_doc()` in loops over lists. Use `frappe.get_all()` or `frappe.db.get_values()` with batch filters:
  ```python
  # BAD:
  for row in items:
      doc = frappe.get_doc("Item", row.item_code)
  
  # GOOD:
  item_codes = [row.item_code for row in items]
  items_data = frappe.get_all("Item", filters={"name": ["in", item_codes]}, fields=["name", "standard_rate", "item_group"])
  ```
- **Use `frappe.qb` (QueryBuilder)** for complex joins and aggregations instead of raw SQL:
  ```python
  Asset = frappe.qb.DocType("Asset")
  query = (
      frappe.qb.from_(Asset)
      .select(Asset.name, Asset.asset_name, Asset.status)
      .where(Asset.status == "In Use")
  )
  results = query.run(as_dict=True)
  ```
- **Lightweight DB Fetch**: Use `frappe.db.get_value("DocType", name, "fieldname")` when you only need 1 or 2 fields without loading the full Document object into memory.

## 3. Whitelisted APIs
- Always define clear permissions and input validation in `@frappe.whitelist()` methods:
  ```python
  @frappe.whitelist(methods=["POST"])
  def assign_asset(asset_id: str, employee_id: str):
      frappe.only_for(["IT Manager", "System Manager"])
      if not asset_id or not employee_id:
          frappe.throw(_("Asset ID and Employee ID are required"), frappe.ValidationError)
      # Business logic...
      return {"status": "success", "message": _("Asset assigned successfully")}
  ```
- If `allow_guest=True` is required (public forms), strictly sanitize and rate limit with `@frappe.rate_limit()`.
