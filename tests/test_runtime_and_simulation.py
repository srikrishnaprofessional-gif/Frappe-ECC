"""
Automated Verification for Frappe Pure Prompt Studio & Autonomous Build from Scratch.
"""

import sys
import os
import time
import json
import urllib.request
import urllib.parse
import threading

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from frappe_ecc_agents.runtime_server import run_server

# Windows UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def start_server_in_thread(port=8055):
    t = threading.Thread(target=run_server, kwargs={"port": port, "open_browser": False}, daemon=True)
    t.start()
    time.sleep(1.5)


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
    print("🧪 TESTING PURE PROMPT STUDIO & AUTONOMOUS BUILD FROM SCRATCH")
    print("=" * 80 + "\n")

    port = 8055
    start_server_in_thread(port)
    base_url = f"http://127.0.0.1:{port}"

    # 1. Verify ZERO Example Apps upon startup
    apps = http_get(f"{base_url}/api/apps")
    print(f"[*] 1. Checking Initial State: Found {len(apps)} apps.")
    assert len(apps) == 0, f"Expected 0 example apps, but found {len(apps)}"
    print("    [CONFIRMED] Zero example apps exist. System starts in clean Prompt Studio mode!")

    # 2. Provide user prompt to build application from scratch
    prompt = "Build an autonomous Healthcare Clinic and Patient Prescription EHR with appointment scheduling, physician notes, and consultation billing"
    print(f"\n[*] 2. Submitting User Prompt to Autonomous AI Agents:")
    print(f"    Prompt: '{prompt}'")
    build_res = http_post(f"{base_url}/api/autonomous/build", {"prompt": prompt, "simulated_count": 25})
    print(f"    [SUCCESS] Application Built from Scratch:")
    print(f"      - App Title: {build_res['app_title']}")
    print(f"      - App Slug: {build_res['app_slug']}")
    print(f"      - Primary DocType: {build_res['primary_doctype']}")
    print(f"      - Deliverables Generated: {build_res['deliverables']}")
    print(f"      - Stimulated Records Seeded: {build_res['simulated_records_seeded']}")
    print(f"      - Execution Time: {build_res['execution_time_sec']}s")

    # 3. Verify application now exists in runtime
    apps_after = http_get(f"{base_url}/api/apps")
    print(f"\n[*] 3. Checking Runtime Apps: Found {len(apps_after)} app -> {apps_after[0]['title']}")
    assert len(apps_after) == 1, "Expected exactly 1 newly built application"

    # 4. Verify stimulated records in the newly created application
    dt_name = build_res['primary_doctype']
    records = http_get(f"{base_url}/api/resource/{urllib.parse.quote(dt_name)}")
    print(f"[*] 4. Querying Stimulated Records in '{dt_name}': Found {len(records)} records")
    assert len(records) == 25, f"Expected 25 stimulated records, found {len(records)}"
    sample = records[0]
    print(f"    Sample Record: [{sample['name']}] '{sample.get('title')}' | Patient: {sample.get('patient_name')} | Doctor: {sample.get('doctor_assigned')} | Diagnosis: {sample.get('diagnosis')} | Status: {sample.get('status')}")

    # 5. Verify State Machine Action on a record
    target_rec = records[0]
    print(f"\n[*] 5. Testing State Machine Action on record {target_rec['name']}...")
    update_res = http_put(f"{base_url}/api/resource/{urllib.parse.quote(dt_name)}/{target_rec['name']}", {"status": "Approved"})
    print(f"    Record Status Updated: {update_res['status']}")
    assert update_res["status"] == "Approved", "Status should be updated to Approved"

    # 6. Verify Working SOP was generated
    sop_data = http_get(f"{base_url}/api/app/sop?name={build_res['app_slug']}")
    print(f"\n[*] 6. Checking Working SOP Documentation:")
    assert len(sop_data.get("sop", "")) > 100, "Working SOP should be generated"
    print("    [CONFIRMED] Working SOP successfully generated for the application!")

    # 7. Stimulate 15 more records on demand
    print(f"\n[*] 7. Testing On-Demand Data Stimulation (+15 records)...")
    synth_res = http_post(f"{base_url}/api/data/synthesize", {"doctype": dt_name, "count": 15})
    total_records = http_get(f"{base_url}/api/resource/{urllib.parse.quote(dt_name)}")
    print(f"    Total records now: {len(total_records)}")
    assert len(total_records) == 40, f"Expected 40 records, found {len(total_records)}"

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED: PURE PROMPT STUDIO & REAL-TIME BUILD VERIFIED!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
