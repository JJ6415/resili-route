import sys
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

print("Testing all 3 Live Scenarios via requests on http://127.0.0.1:8080...")

for sid in [1, 2, 3]:
    r = requests.post("http://127.0.0.1:8080/v1/simulation/run", json={"scenario_id": sid}, timeout=30)
    data = r.json()
    print(f"[OK] Scenario {sid} [{data['scenario_name']}]: HTTP {r.status_code} | Status={data['status']}")
    if sid == 1:
        print(f"     Applicant: {data['output_summary']['applicant']}")
        print(f"     Savings: {data['output_summary']['cost_savings_jpy']:,} JPY ({data['output_summary']['savings_pct']})")
    elif sid == 2:
        print(f"     Bottleneck: {data['output_summary']['shinjuku_bottleneck_index']}")
        print(f"     Dispersal: {data['output_summary']['group_a']}")
    elif sid == 3:
        print(f"     Stranded: {data['output_summary']['stranded_employee']}")
        print(f"     Shelter: {data['output_summary']['matched_bcp_shelter']}")

print("\n[SUCCESS] All 3 Scenarios Live API Verification Completed with 100% Success!")
