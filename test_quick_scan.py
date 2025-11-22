import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from worker import run_scan

print("Testing scan functionality...")
try:
    result = run_scan('https://example.com')
    print(f"\n✅ SUCCESS! Scan completed.")
    print(f"   Found {len(result['issues'])} issues")
    print(f"   Screenshot: {result['screenshotPath']}")
    print(f"   Summary: {result['summary']}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
