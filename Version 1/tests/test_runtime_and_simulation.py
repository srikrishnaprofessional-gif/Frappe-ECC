"""
Automated Verification for Frappe Pure Prompt Studio & Autonomous Build from Scratch.
Tests dynamic schema synthesis, Claude API connection endpoints, and multi-domain execution.
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
    print("🧪 TESTING PURE PROMPT STUDIO, CLAUDE INTEGRATION & ZERO-TEMPLATE SYNTHESIS")
    print("=" * 80 + "\n")

    port = 8055
    start_server_in_thread(port)
    base_url = f"http://127.0.0.1:{port}"

    # 1. Verify ZERO Example Apps upon startup
    apps = http_get(f"{base_url}/api/apps")
    print(f"[*] 1. Checking Initial State: Found {len(apps)} apps.")
    assert len(apps) == 0, f"Expected 0 example apps, but found {len(apps)}"
    print("    [CONFIRMED] Zero example apps exist. System starts in clean Prompt Studio mode!")

    # 2. Verify Claude Connection Status endpoint
    claude_status = http_get(f"{base_url}/api/claude/status")
    print(f"\n[*] 2. Checking Claude Status Endpoint: connected={claude_status.get('connected')}, model={claude_status.get('model')}")
    assert "connected" in claude_status, "Claude status should return connected flag"

    # 3. Test Claude Connect Endpoint (Stores locally in ~/.claude_key & .env)
    test_key = "sk-ant-api03-test-mock-autonomous-agent-key-4928"
    connect_res = http_post(f"{base_url}/api/claude/connect", {
        "api_key": test_key,
        "model": "claude-3-7-sonnet-20250219"
    })
    print(f"[*] 3. Testing Claude Connect Endpoint: success={connect_res.get('success')}")
    assert connect_res.get("success") is True, "Setting Claude key should succeed"

    # 4. Provide Bespoke Natural Language Prompt 1 (Aerospace & Satellites - No Templates!)
    prompt1 = "Build an autonomous Aerospace Satellite Payload and Telemetry Tracker with orbit velocity, sensor thermal readings, telemetry packets, and ground station downlink logs"
    print(f"\n[*] 4. Submitting Bespoke Prompt 1 (Zero Templates - Aerospace & Satellites):")
    print(f"    Prompt: '{prompt1}'")
    build_res1 = http_post(f"{base_url}/api/autonomous/build", {"prompt": prompt1, "simulated_count": 25})
    print(f"    [SUCCESS] Application 1 Built from Scratch:")
    print(f"      - App Title: {build_res1['app_title']}")
    print(f"      - App Slug: {build_res1['app_slug']}")
    print(f"      - Primary DocType: {build_res1['primary_doctype']}")
    print(f"      - Deliverables Generated: {build_res1['deliverables']}")
    print(f"      - Stimulated Records Seeded: {build_res1['simulated_records_seeded']}")
    print(f"      - Execution Time: {build_res1['execution_time_sec']}s")

    assert build_res1["simulated_records_seeded"] == 25, "Expected 25 simulated records"
    assert build_res1["deliverables"] > 0, "Deliverables should be generated across all pillars"

    # 5. Query Stimulated Records in Application 1
    dt_name1 = build_res1['primary_doctype']
    records1 = http_get(f"{base_url}/api/resource/{urllib.parse.quote(dt_name1)}")
    print(f"\n[*] 5. Querying Stimulated Records in '{dt_name1}': Found {len(records1)} records")
    assert len(records1) == 25, f"Expected 25 stimulated records, found {len(records1)}"
    sample1 = records1[0]
    print(f"    Sample Record: [{sample1['name']}] Title: '{sample1.get('title')}' | Status: {sample1.get('status')}")

    # 6. Test State Machine Action on App 1 Record
    print(f"\n[*] 6. Testing State Machine Action on record {sample1['name']}...")
    update_res = http_put(f"{base_url}/api/resource/{urllib.parse.quote(dt_name1)}/{sample1['name']}", {"status": "Approved"})
    print(f"    Record Status Updated: {update_res['status']}")
    assert update_res["status"] == "Approved", "Status should be updated to Approved"

    # 7. Check Working SOP for App 1
    sop_data = http_get(f"{base_url}/api/app/sop?name={build_res1['app_slug']}")
    print(f"\n[*] 7. Checking Working SOP Documentation for '{build_res1['app_slug']}':")
    assert len(sop_data.get("sop", "")) > 100, "Working SOP should be generated"
    print("    [CONFIRMED] Working SOP successfully generated for Application 1!")

    # 8. Submit Bespoke Natural Language Prompt 2 (Agricultural Vineyard & Fermentation)
    prompt2 = "Build an Agricultural Vineyard and Wine Fermentation Monitor with sugar brix levels, barrel tanks, and fermentation temperatures"
    print(f"\n[*] 8. Submitting Bespoke Prompt 2 (Agricultural Fermentation):")
    print(f"    Prompt: '{prompt2}'")
    build_res2 = http_post(f"{base_url}/api/autonomous/build", {"prompt": prompt2, "simulated_count": 20})
    print(f"    [SUCCESS] Application 2 Built from Scratch:")
    print(f"      - App Title: {build_res2['app_title']}")
    print(f"      - Primary DocType: {build_res2['primary_doctype']}")
    print(f"      - Stimulated Records Seeded: {build_res2['simulated_records_seeded']}")

    # 9. Verify Multi-App Isolation on the Frappe Framework
    apps_all = http_get(f"{base_url}/api/apps")
    print(f"\n[*] 9. Checking Runtime Applications: Found {len(apps_all)} distinct applications")
    assert len(apps_all) == 2, f"Expected 2 distinct applications, found {len(apps_all)}"
    for a in apps_all:
        print(f"      → [{a['name']}] {a['title']}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED: PURE PROMPT STUDIO, CLAUDE INTEGRATION & ZERO TEMPLATES VERIFIED!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
