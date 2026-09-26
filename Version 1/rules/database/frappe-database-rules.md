# Frappe Database & MariaDB / PostgreSQL Optimization Rules

## 1. Indexing Strategy
- When defining DocType fields in `.json`:
  - Set `"search_index": 1` for fields frequently used in WHERE filters, lookups, or barcode scans (e.g. `serial_no`, `asset_tag`, `mac_address`).
  - Set `"in_standard_filter": 1` or `"in_list_view": 1` for fields used in standard Desk search bars.
  - Link fields automatically create database indexes; do not add redundant manual indexes.

## 2. Child Table Query Performance
- In MariaDB, child tables are stored in separate physical tables (e.g. `tabAsset Maintenance Item`).
- Every child table row has `parent`, `parenttype`, `parentfield`, and `idx`.
- When filtering parent documents by child table attributes, avoid correlated subqueries. Use `frappe.qb` inner joins or query the child table first to collect distinct parent names:
  ```python
  Item = frappe.qb.DocType("Asset Maintenance Item")
  parents = (
      frappe.qb.from_(Item)
      .select(Item.parent)
      .distinct()
      .where(Item.item_code == target_item)
  ).run(pluck=True)
  ```

## 3. Large Dataset Processing
- Never load entire tables into Python memory with `frappe.get_all()` without limits.
- Process large batch jobs in chunks using pagination:
  ```python
  limit = 500
  start = 0
  while True:
      batch = frappe.get_all("Asset", fields=["name", "status"], start=start, page_length=limit)
      if not batch:
          break
      for row in batch:
          process_row(row)
      start += limit
  ```
