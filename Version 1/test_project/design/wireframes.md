# Visual Wireframes: IT Equipment Loan & Return System
**Author:** frappe-wireframe-builder  

---

## 1. Desk Form View (Active Loan)

```
+-----------------------------------------------------------------------------------------------+
| < Equipment Loans  /  LOAN-2026-00042   [ Active (Green) ]            [ Process Return ] [Menu]|
+-----------------------------------------------------------------------------------------------+
| SECTION 1: BORROWER & SCHEDULE                                                                |
|  Borrower:     [ EMP-00104 - Alex Mercer v ]     Department:          [ Engineering          ]|
|  Loan Date:    [ 2026-09-21              ]     Expected Return Date:[ 2026-10-05            ]|
|  Duration:     14 days                         Actual Return Date:  [                      ]|
+-----------------------------------------------------------------------------------------------+
| SECTION 2: BORROWED EQUIPMENT (Child Table Grid)                                              |
|  +---+---------------------+----------------+------------------+--------------+-------------+ |
|  | # | Asset Code          | Serial Number  | Condition        | Value (USD)  | Action      | |
|  +---+---------------------+----------------+------------------+--------------+-------------+ |
|  | 1 | AST-001 (MacBook)   | MBP-M3-9901    | Good             | $   2,499.00 | [Remove]    | |
|  | 2 | AST-004 (Monitor)   | MN-4K-2210     | New              | $     650.00 | [Remove]    | |
|  +---+---------------------+----------------+------------------+--------------+-------------+ |
|  [ + Add Hardware Item ]                               Total Loan Value: $   3,149.00         |
+-----------------------------------------------------------------------------------------------+
| SECTION 3: RETURN AUDIT & NOTES                                                               |
|  Return Notes: [ Returned via IT Helpdesk Desk #4                                           ] |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. Modal Return Dialog Wireframe (`frappe.ui.Dialog`)

```
+--------------------------------------------------------------------+
| Process Equipment Return - LOAN-2026-00042                     [X] |
+--------------------------------------------------------------------+
| Return Date:       [ 2026-10-04 (Today)                          ] |
| Return Condition:  [ All items intact & operational              v]|
| Inspection Notes:  [ Tested display and power adapter. All OK.   ] |
|                                                                    |
| Hardware Checklist:                                                |
|  [x] AST-001 - MacBook Pro 16" (Charger received)                  |
|  [x] AST-004 - Studio Display 27" (Thunderbolt cable received)     |
+--------------------------------------------------------------------+
|                                      [ Cancel ]  [ Confirm Return ]|
+--------------------------------------------------------------------+
```
