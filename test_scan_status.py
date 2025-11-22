"""
Test script to diagnose scan status issues.
This will help identify if the problem is in the backend or frontend.
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"


def test_scan_flow():
    """Test the complete scan flow and monitor status changes."""

    print("\n" + "="*70)
    print("SCAN STATUS TEST - Monitoring scan lifecycle")
    print("="*70 + "\n")

    # Step 1: Create a scan
    print("Step 1: Creating scan...")
    response = requests.post(
        f"{BASE_URL}/api/v1/scans",
        json={"url": "https://example.com", "mode": "static"}
    )

    if response.status_code != 200:
        print(f"❌ Failed to create scan: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    scan_id = data['scanId']
    print(f"✅ Scan created: {scan_id}")
    print(f"   Initial status: {data['status']}\n")

    # Step 2: Monitor status changes
    print("Step 2: Monitoring status (will check every 2 seconds for 30 seconds)...")
    print("-" * 70)

    statuses = []
    for i in range(15):  # 30 seconds total
        time.sleep(2)

        response = requests.get(f"{BASE_URL}/api/v1/scans/{scan_id}")

        if response.status_code != 200:
            print(f"❌ Failed to get status: {response.status_code}")
            continue

        data = response.json()
        status = data.get('status')
        statuses.append({
            'time': i * 2,
            'status': status,
            'hasResult': 'result' in data,
            'hasError': 'error' in data,
            'error': data.get('error', '')[:100] if 'error' in data else None
        })

        print(f"[{i*2:2d}s] Status: {status:10s} | "
              f"Has result: {'Yes' if 'result' in data else 'No ':3s} | "
              f"Has error: {'Yes' if 'error' in data else 'No'}")

        if 'error' in data:
            print(f"      Error: {data['error'][:100]}")

        # Stop if done or error
        if status in ['done', 'error']:
            print("\n" + "-" * 70)
            break

    # Step 3: Get final result
    print("\nStep 3: Final scan state...")
    response = requests.get(f"{BASE_URL}/api/v1/scans/{scan_id}")
    final_data = response.json()

    print(f"\nFinal Status: {final_data.get('status')}")

    if final_data.get('status') == 'done':
        print("✅ SCAN COMPLETED SUCCESSFULLY!")
        result = final_data.get('result', {})
        print(f"   Issues found: {len(result.get('issues', []))}")
        print(f"   Screenshot: {result.get('screenshotPath', 'N/A')}")
    elif final_data.get('status') == 'error':
        print("❌ SCAN FAILED!")
        print(f"   Error: {final_data.get('error')}")
        if 'errorDetails' in final_data:
            print(f"\n   Error Details:")
            print(f"   {final_data['errorDetails']}")
    else:
        print(f"⚠️  SCAN STILL IN PROGRESS (status: {final_data.get('status')})")

    # Step 4: Check debug info
    print("\n" + "="*70)
    print("Step 4: Debug Information")
    print("="*70)

    try:
        response = requests.get(f"{BASE_URL}/api/v1/debug/scans")
        if response.status_code == 200:
            debug_data = response.json()
            print(f"\nTotal scans in memory: {debug_data['totalScans']}")
            print(f"Active scan threads: {len(debug_data['activeThreads'])}")

            if debug_data['activeThreads']:
                print("\nActive threads:")
                for thread in debug_data['activeThreads']:
                    print(f"  - {thread['name']}: alive={thread['alive']}, daemon={thread['daemon']}")
    except Exception as e:
        print(f"Could not get debug info: {e}")

    # Step 5: Status transition analysis
    print("\n" + "="*70)
    print("Step 5: Status Transition Analysis")
    print("="*70)

    print("\nStatus history:")
    for i, s in enumerate(statuses):
        print(f"  {i+1}. [{s['time']:2d}s] {s['status']:10s} "
              f"{'(has result)' if s['hasResult'] else ''} "
              f"{'(has error)' if s['hasError'] else ''}")

    # Check for suspicious patterns
    status_sequence = [s['status'] for s in statuses]

    print("\nDiagnostics:")

    if 'running' in status_sequence and 'error' in status_sequence:
        running_idx = status_sequence.index('running')
        error_idx = status_sequence.index('error')
        print(f"⚠️  Status went from 'running' to 'error' at {statuses[error_idx]['time']}s")
        print(f"   This suggests the scan encountered an error during execution")
        if statuses[error_idx]['error']:
            print(f"   Error message: {statuses[error_idx]['error']}")

    if status_sequence.count('queued') > 3:
        print("⚠️  Scan stayed in 'queued' state for a long time")
        print("   The scan might not be starting properly")

    if 'running' not in status_sequence and final_data.get('status') == 'error':
        print("⚠️  Scan went directly to 'error' without 'running'")
        print("   This suggests the scan failed to start")

    if final_data.get('status') == 'done':
        print("✅ Everything looks good! Scan completed successfully.")

    print("\n" + "="*70)
    print("Test Complete")
    print("="*70 + "\n")


def check_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False


if __name__ == "__main__":
    print("\n🔍 Scan Status Diagnostic Tool\n")

    # Check if server is running
    if not check_server():
        print("❌ Server is not running!")
        print(f"\nPlease start the server first:")
        print(f"   cd app")
        print(f"   uvicorn main:app --reload\n")
        exit(1)

    print(f"✅ Server is running at {BASE_URL}\n")

    # Run the test
    try:
        test_scan_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
