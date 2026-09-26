---
name: frappe-qa-testing-automation
description: End-to-end testing automation recipes with Playwright for Frappe Desk, manual test matrix generation, and API regression testing.
---

# Frappe QA Testing & Browser Automation

## 1. Manual QA Test Matrix Structure
When creating manual test suites, organize cases into a structured verification matrix:

| Test ID | Feature Scenario | Pre-conditions | Test Steps | Input Data | Expected Result | Status |
|---|---|---|---|---|---|---|
| `TC-AST-01` | Create Asset with Autonaming | User has `Asset Manager` role | 1. Navigate to `/app/asset-item/new`<br>2. Fill Name & Category<br>3. Click Save | Name: "Dell XPS 15"<br>Category: "IT Hardware" | Doc created with prefix `AST-2026-` and status `Draft` | Passed |
| `TC-AST-02` | Reject Duplicate Serial Number | Existing asset with SN `SN-DUPE-01` | 1. Create new asset<br>2. Input existing serial number<br>3. Click Save | Serial: `SN-DUPE-01` | System throws `DuplicateEntryError` modal toast | Passed |
| `TC-AST-03` | Restrict Non-Manager Deletion | User has `Asset Custodian` role (Read only) | 1. Open submitted asset<br>2. Check Menu dropdown | N/A | `Delete` option hidden from Menu; direct API returns HTTP 403 | Passed |

---

## 2. Playwright Automated E2E Browser Testing for Frappe Desk
Playwright drives headless Chromium to test complete Desk workflows:

```python
# tests/e2e/test_asset_workflow.py
import pytest
from playwright.sync_api import Page, expect

FRAPPE_URL = "http://itam.localhost:8000"

def test_asset_creation_and_submission(page: Page):
    # 1. Login to Frappe Desk
    page.goto(f"{FRAPPE_URL}/login")
    page.fill('input[id="login_email"]', "Administrator")
    page.fill('input[id="login_password"]', "admin123")
    page.click('button:has-text("Sign in")')
    
    # 2. Verify Desk is loaded
    expect(page.locator('.navbar-home')).to_be_visible()

    # 3. Navigate to Asset Form
    page.goto(f"{FRAPPE_URL}/app/asset-item/new")
    
    # 4. Fill form inputs using Desk selectors
    page.fill('input[data-fieldname="asset_name"]', "Test Automated Asset")
    page.fill('input[data-fieldname="serial_no"]', "AUTO-SN-99881")
    
    # 5. Save Document
    page.click('button[data-label="Save"]')
    
    # 6. Assert Indicator and Toast
    expect(page.locator('.indicator-pill')).to_contain_text("Draft")
    expect(page.locator('.desk-alert')).to_be_visible()
```
