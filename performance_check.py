"""
Performance Monitoring Script for a11yvision Backend
Similar to Chrome DevTools Performance tab
"""
import time
import psutil
import requests
from datetime import datetime

API_BASE = "https://api.a11yvision.labnexus.my.id"

def check_backend_performance():
    """Check actual backend performance metrics"""

    print("🔍 BACKEND PERFORMANCE CHECK")
    print("=" * 60)

    # 1. API Response Time
    print("\n📊 API Response Times:")
    endpoints = [
        "/health",
        "/api/v1/stats",
        "/api/v1/scans",
    ]

    for endpoint in endpoints:
        try:
            start = time.time()
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            duration = (time.time() - start) * 1000  # ms

            status = "✅" if duration < 500 else "⚠️" if duration < 1000 else "❌"
            print(f"{status} {endpoint}: {duration:.2f}ms (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {str(e)}")

    # 2. System Resources (if running locally)
    print("\n💻 System Resources:")
    print(f"   CPU Usage: {psutil.cpu_percent()}%")
    print(f"   Memory Usage: {psutil.virtual_memory().percent}%")
    print(f"   Disk Usage: {psutil.disk_usage('/').percent}%")

    # 3. Scan Performance Test
    print("\n⚡ Scan Performance Test:")
    test_url = "https://example.com"

    try:
        # Create scan
        start = time.time()
        response = requests.post(
            f"{API_BASE}/api/v1/scans",
            json={"url": test_url, "mode": "static"},
            timeout=30
        )
        create_time = (time.time() - start) * 1000
        print(f"   Scan Creation: {create_time:.2f}ms")

        if response.status_code == 200:
            scan_id = response.json().get('scanId')
            print(f"   Scan ID: {scan_id}")

            # Monitor scan progress
            max_wait = 60  # seconds
            start_wait = time.time()

            while (time.time() - start_wait) < max_wait:
                time.sleep(2)
                status_response = requests.get(f"{API_BASE}/api/v1/scans/{scan_id}")
                status = status_response.json().get('status')
                print(f"   Status: {status}")

                if status in ['done', 'error', 'failed']:
                    total_time = time.time() - start_wait
                    print(f"   ✅ Total Scan Time: {total_time:.2f}s")
                    break

    except Exception as e:
        print(f"   ❌ Scan test failed: {str(e)}")

    print("\n" + "=" * 60)
    print("✅ Performance check complete!")
    print("\n📝 SUMMARY:")
    print("   - If response times > 1000ms: Backend is slow")
    print("   - If CPU/Memory > 80%: Resource bottleneck")
    print("   - If scans take > 30s: Scanning pipeline needs optimization")

if __name__ == "__main__":
    check_backend_performance()
