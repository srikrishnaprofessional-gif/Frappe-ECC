# Manual QA Test Scenarios: IT Equipment Loan & Return System
**Author:** frappe-manual-qa  
**Suite:** `EQUIPMENT-LOAN-REGRESSION-V1`  

---

## Comprehensive Test Scenario Matrix

| Test ID | Scenario Description | Pre-conditions | Test Steps | Input Data | Expected Result | Priority |
|---|---|---|---|---|---|---|
| **TS-01** | Create Draft Loan (Happy Path) | Employee `EMP-00104` has no overdue loans; assets `AST-001`, `AST-002` Available | 1. Open `/app/equipment-loan/new`<br>2. Select borrower `EMP-00104`<br>3. Set Loan Date today, Return Date +14 days<br>4. Add rows for `AST-001` and `AST-002`<br>5. Click Save | Borrower: `EMP-00104`<br>Loan: 2026-09-21<br>Return: 2026-10-05 | Document saved with autoname `LOAN-.YYYY.-.#####`, status `Draft`, total value $5,098.00 | P0 (Critical) |
| **TS-02** | Reject Invalid Return Date (Past) | New loan form open | 1. Set Loan Date `2026-09-21`<br>2. Set Expected Return Date `2026-09-10`<br>3. Click Save | Return Date < Loan Date | System throws `ValidationError`: Expected Return Date cannot be before Loan Date | P0 (Critical) |
| **TS-03** | Reject Loan Exceeding 30 Days Policy | New loan form open | 1. Set Loan Date `2026-09-21`<br>2. Set Expected Return Date `2026-10-31` (40 days)<br>3. Click Save | Duration = 40 days | System throws `ValidationError`: Loan duration (40 days) exceeds maximum policy limit of 30 days | P1 (High) |
| **TS-04** | Reject Unavailable Asset Lending | Asset `AST-004` marked `Loaned Out` | 1. Add row with asset `AST-004`<br>2. Click Save | Asset: `AST-004` (Loaned Out) | System throws `ValidationError`: Asset AST-004 is currently 'Loaned Out' and unavailable | P0 (Critical) |
| **TS-05** | Reject Duplicate Items in Table | New loan form open | 1. Add row with `AST-001`<br>2. Add second row with `AST-001`<br>3. Click Save | Duplicate `AST-001` | System throws `ValidationError`: Duplicate item AST-001 in loan table | P1 (High) |
| **TS-06** | Block Borrower with Overdue Loan | Employee `EMP-00105` has active overdue loan | 1. Select borrower `EMP-00105`<br>2. Fill valid dates and items<br>3. Click Save | Borrower: `EMP-00105` | System throws `PermissionError`: Borrower has overdue equipment loan. Return overdue items first | P0 (Critical) |
| **TS-07** | Inventory Status Update on Submit | Draft loan saved with available assets | 1. Open draft loan<br>2. Click `Submit`<br>3. Check status of `AST-001` in `Loanable Asset` | docstatus transitions 0 -> 1 | Loan status becomes `Active`. Asset `AST-001` status updates to `Loaned Out` | P0 (Critical) |
| **TS-08** | Inventory Status Reversal on Cancel | Active loan submitted | 1. Open active loan<br>2. Click `Cancel`<br>3. Check status of `AST-001` in `Loanable Asset` | docstatus transitions 1 -> 2 | Loan status becomes `Cancelled`. Asset `AST-001` status reverses back to `Available` | P0 (Critical) |
| **TS-09** | Process Return via REST API | Active loan exists | 1. Send POST request to `/api/method/equipment_loan.api.loan_api.process_return`<br>2. Pass `loan_id` | Loan: `LOAN-2026-00042` | Returns HTTP 200 with `status: success`. Loan status becomes `Returned`, assets released to `Available` | P0 (Critical) |
| **TS-10** | Unauthorized Return Rejection | User lacks `IT Asset Manager` or `System Manager` role | 1. Authenticate as regular Employee<br>2. Attempt to call `process_return` API | User without required role | Returns HTTP 403 Forbidden with `PermissionError` | P1 (High) |
