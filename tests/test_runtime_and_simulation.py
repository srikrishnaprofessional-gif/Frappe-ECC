"""
Automated Verification for Frappe Local Runtime Server, Real-time Autonomous Builder & Data Simulator.
"""

import sys
import os
import time
import json
import urllib.request
import threading

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from frappe_ecc_agents.runtime_server import run_server

# Windows UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def start_server_in_thread(port=8050):
    t = threading.Thread(target=run_server, kwargs={"port": port, "open_browser": False}, daemon=True)
    t.start()
    time.sleep(1.5)  # Wait for socket binding


def http_get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_put(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="PUT")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("\n" + "=" * 80)
    print("🧪 TESTING FRAPPE AUTONOMOUS LOCAL RUNTIME & DATA SIMULATOR")
    print("=" * 80 + "\n")

    port = 8055  # Use port 8055 for clean test isolation
    start_server_in_thread(port)
    base_url = f"http://127.0.0.1:{port}"

    # 1. Test Apps List
    apps = http_get(f"{base_url}/api/apps")
    print(f"[*] 1. Apps Endpoint: Found {len(apps)} initial apps -> {[a['title'] for a in apps]}")
    assert len(apps) >= 2, "Default apps should be registered"

    # 2. Test DocTypes
    dts = http_get(f"{base_url}/api/doctypes?app=loan_management")
    print(f"[*] 2. DocTypes Endpoint: Found {len(dts)} DocTypes for loan_management -> {[d['name'] for d in dts]}")
    assert len(dts) >= 1, "DocTypes should be registered"

    # 3. Test Stimulated Records
    records = http_get(f"{base_url}/api/resource/Equipment%20Loan")
    print(f"[*] 3. Simulated Records Query: Found {len(records)} seeded records in Equipment Loan")
    assert len(records) >= 20, "Should have seeded 20+ realistic simulated records"
    sample = records[0]
    print(f"    Sample Record: [{sample['name']}] '{sample['title']}' | {sample['applicant_name']} | ${sample['requested_amount']:,.2f} | Status: {sample['status']}")

    # 4. Test Data Synthesizer API (Synthesize 15 more simulated records)
    print(f"[*] 4. Testing Live Data Simulator: Generating 15 additional simulated records...")
    synth_res = http_post(f"{base_url}/api/data/synthesize", {"doctype": "Equipment Loan", "count": 15})
    print(f"    Simulator Output: {synth_res}")
    updated_records = http_get(f"{base_url}/api/resource/Equipment%20Loan")
    print(f"    Total Records now in Equipment Loan: {len(updated_records)} (increased by {len(updated_records) - len(records)})")
    assert len(updated_records) == len(records) + 15, "Should have exactly added 15 records"

    # 5. Test Record Workflow State Update (Quick Approve)
    target_rec = updated_records[0]
    print(f"[*] 5. Testing State Machine Action: Transitioning {target_rec['name']} to 'Approved'...")
    put_res = http_put(f"{base_url}/api/resource/Equipment%20Loan/{target_rec['name']}", {"status": "Approved"})
    print(f"    Updated Record Status: {put_res['status']}")
    assert put_res["status"] == "Approved", "Status should be Approved"

    # 6. Test Autonomous App Builder from Prompt in Real Time
    prompt = "Build a Healthcare Clinic and Patient Prescription EHR with appointment scheduling and billing"
    print(f"\n[*] 6. Testing Autonomous AI Agents App Development in Real Time:")
    print(f"    Input Prompt: '{prompt}'")
    build_res = http_post(f"{base_url}/api/autonomous/build", {"prompt": prompt})
    print(f"    [SUCCESS] Real-time Build Result:")
    print(f"      - App Title: {build_res['app_title']}")
    print(f"      - App Slug: {build_res['app_slug']}")
    print(f"      - Deliverables Generated: {build_res['deliverables']}")
    print(f"      - Stimulated Records Seeded: {build_res['simulated_records_seeded']}")
    print(f"      - Autonomous Build Time: {build_res['execution_time_sec']}s")

    # 7. Verify newly synthesized application is live in runtime
    new_apps = http_get(f"{base_url}/api/apps")
    print(f"\n[*] 7. Verifying Hot-Reload: Total Apps in Runtime now: {len(new_apps)}")
    app_titles = [a["title"] for a in new_apps]
    print(f"    Apps List: {app_titles}")
    assert any("Healthcare" in t or "Clinic" in t or "Patient" in t for t in app_titles), "New app must be registered"

    # 8. Verify simulated records exist in the newly synthesized application
    new_dts = http_get(f"{base_url}/api/doctypes?app={build_res['app_slug']}")
    print(f"    DocTypes in new app: {[d['name'] for d in new_dts]}")
    if new_dts:
        target_new_dt = new_dts[0]["name"]
        new_records = http_get(f"{base_url}/api/resource/{urllib.parse.quote(target_new_dt)}")
        print(f"    Stimulated Records seeded in {target_new_dt}: {len(new_records)}")
        assert len(new_records) >= 15, "Should have seeded stimulated records in new app"
        print(f"    Sample new record: {new_records[0]['title']} | {new_records[0].get('applicant_name', 'N/A')} | Status: {new_records[0]['status']}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED: AUTONOMOUS REAL-TIME AGENTS & LOCAL RUNTIME SIMULATOR VERIFIED!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
