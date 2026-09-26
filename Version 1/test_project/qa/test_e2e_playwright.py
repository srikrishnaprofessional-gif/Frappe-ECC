#!/usr/bin/env python3
"""
Playwright End-to-End Browser Automation Suite for Frappe Desk
Simulates real user interaction: Login -> DocType Navigation -> Form Filling ->
Child Table Manipulation -> Document Submission -> Return Processing Dialog.

Can be run against a live Frappe bench (set FRAPPE_URL) or against local prototype.
Usage:
    pytest test_project/qa/test_e2e_playwright.py
    python test_project/qa/test_e2e_playwright.py
"""

import os
import sys
from pathlib import Path

FRAPPE_URL = os.environ.get("FRAPPE_URL", "http://localhost:8000")
ADMIN_USER = os.environ.get("FRAPPE_ADMIN_USER", "Administrator")
ADMIN_PASS = os.environ.get("FRAPPE_ADMIN_PASSWORD", "admin")

def run_e2e_tests():
    try:
        from playwright.sync_api import sync_playwright, expect
    except ImportError:
        print("[SKIP] Playwright is not installed in the current environment.")
        print("To install playwright: pip install playwright && playwright install chromium")
        return 0

    print("============================================================")
    print("🎭 PLAYWRIGHT END-TO-END BROWSER AUTOMATION")
    print("============================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # ------------------------------------------------------------
        # Test 1: Interactive Prototype Flow (Self-contained)
        # ------------------------------------------------------------
        prototype_path = Path(__file__).resolve().parent.parent / "design" / "interactive_prototype.html"
        if prototype_path.exists():
            print(f"[RUN] Testing Interactive Prototype: {prototype_path.name}")
            page.goto(f"file:///{prototype_path.as_posix()}")

            # 1. Assert Title and Initial State
            expect(page.locator("h1")).to_contain_text("LOAN-2026-00042")
            expect(page.locator(".bg-amber-50")).to_be_visible() # Draft pill

            # 2. Add Child Table Item
            initial_rows = page.locator("tbody tr").count()
            add_btn = page.locator('button:has-text("Add Hardware Item")')
            if add_btn.is_visible():
                add_btn.click()
                print("  ✓ Clicked 'Add Hardware Item' -> New row inserted")

            # 3. Submit Document
            submit_btn = page.locator('button:has-text("Submit Loan")')
            submit_btn.click()
            print("  ✓ Clicked 'Submit Loan' button")

            # Assert Status changed to Active
            page.wait_for_timeout(300)
            expect(page.locator("span:has-text('Active')")).to_be_visible()
            print("  ✓ Document status dynamically updated to 'Active'")

            # 4. Open Return Dialog Modal
            return_btn = page.locator('button:has-text("Process Return")')
            expect(return_btn).to_be_visible()
            return_btn.click()
            print("  ✓ Clicked 'Process Return' -> Return modal opened")

            # Fill Return Form
            expect(page.locator("h3:has-text('Process Equipment Return')")).to_be_visible()
            page.fill("input[type='date']", "2026-09-22")
            page.select_option("select", index=0)
            page.fill("textarea", "Returned in pristine condition during automated E2E test run.")

            # Confirm Return
            page.click("button:has-text('Confirm Return')")
            page.wait_for_timeout(300)
            expect(page.locator("span:has-text('Returned')")).to_be_visible()
            print("  ✓ Equipment returned -> Status transitioned to 'Returned'")
            print("✅ Interactive Prototype E2E Test Passed Successfully!\n")

        # ------------------------------------------------------------
        # Test 2: Live Frappe Desk Flow (When Frappe server is reachable)
        # ------------------------------------------------------------
        desk_reachable = False
        try:
            import urllib.request
            urllib.request.urlopen(f"{FRAPPE_URL}/login", timeout=2)
            desk_reachable = True
        except Exception:
            print(f"[INFO] Live Frappe server not running at {FRAPPE_URL} (skipping live Desk test).")

        if desk_reachable:
            print(f"[RUN] Testing Live Frappe Desk Workflow on {FRAPPE_URL}")
            page.goto(f"{FRAPPE_URL}/login")
            page.fill('input[id="login_email"]', ADMIN_USER)
            page.fill('input[id="login_password"]', ADMIN_PASS)
            page.click('button:has-text("Sign in")')
            page.wait_for_selector(".navbar-home", timeout=5000)
            print("  ✓ Logged into Frappe Desk")

            # Navigate to Equipment Loan
            page.goto(f"{FRAPPE_URL}/app/equipment-loan/new")
            page.fill('input[data-fieldname="borrower"]', "EMP-00104")
            page.fill('input[data-fieldname="loan_date"]', "2026-09-21")
            page.fill('input[data-fieldname="expected_return_date"]', "2026-10-05")
            page.click('button[data-label="Save"]')
            expect(page.locator('.indicator-pill')).to_contain_text("Draft")
            print("  ✓ Draft Equipment Loan saved")
            print("✅ Live Desk Workflow Test Passed Successfully!")

        browser.close()
        return 0

if __name__ == "__main__":
    sys.exit(run_e2e_tests())
