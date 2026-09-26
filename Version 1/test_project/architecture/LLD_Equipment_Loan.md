# Low-Level Design (LLD): IT Equipment Loan & Return System
**Author:** frappe-lld-designer  
**System:** `equipment_loan`  
**Status:** Approved for Implementation  

---

## 1. Entity-Relationship (ER) Model

```mermaid
erDiagram
    EQUIPMENT_LOAN ||--o{ EQUIPMENT_LOAN_ITEM : contains
    LOANABLE_ASSET ||--o{ EQUIPMENT_LOAN_ITEM : allocated_in
    EMPLOYEE ||--o{ EQUIPMENT_LOAN : borrows

    LOANABLE_ASSET {
        varchar(140) name PK "Autoname AST-#####"
        varchar(140) asset_name "Indexed"
        varchar(140) serial_no UK "Unique Index"
        varchar(50) category "Laptop | Monitor | Mobile | Peripheral"
        varchar(50) status "Available | Loaned Out | Maintenance"
        decimal replacement_value
    }

    EQUIPMENT_LOAN {
        varchar(140) name PK "Autoname LOAN-.YYYY.-.#####"
        varchar(140) borrower FK "References EMPLOYEE"
        varchar(140) department
        date loan_date
        date expected_return_date
        date actual_return_date
        varchar(50) status "Draft | Active | Returned | Overdue"
        decimal total_loan_value
        text return_notes
        int docstatus "0=Draft, 1=Submitted/Active, 2=Cancelled"
    }

    EQUIPMENT_LOAN_ITEM {
        varchar(140) name PK
        varchar(140) parent FK "References EQUIPMENT_LOAN"
        varchar(140) asset FK "References LOANABLE_ASSET"
        varchar(140) serial_no
        varchar(50) condition_on_loan "Good | New | Fair"
        varchar(50) condition_on_return "Good | Damaged | Lost"
        decimal item_value
        int idx "Row Sequence"
    }
```

---

## 2. State Transition Machine

```
[Draft: docstatus=0]
        │
        ▼ (Submit action: Validate dates, check availability, borrower check)
[Active / Loaned: docstatus=1]
        │
        ├─────────────────────────────┬─────────────────────────────┐
        │                             │                             │
        ▼ (Process Return API)        ▼ (Daily Cron Check)          ▼ (Cancel action)
[Returned: docstatus=1]       [Overdue: docstatus=1]        [Cancelled: docstatus=2]
(Assets marked Available)      (Alert sent to manager)       (Assets marked Available)
```

---

## 3. Whitelisted REST API Specifications

### Endpoint: `process_return`
- **Route**: `POST /api/method/equipment_loan.api.loan_api.process_return`
- **Headers**: `Authorization: token <key>:<secret>`
- **Request Body**:
  ```json
  {
    "loan_id": "LOAN-2026-00012",
    "return_notes": "All items returned in pristine condition.",
    "item_conditions": {
      "AST-0001": "Good",
      "AST-0002": "Good"
    }
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "loan_id": "LOAN-2026-00012",
    "returned_on": "2026-09-21",
    "items_processed": 2
  }
  ```
