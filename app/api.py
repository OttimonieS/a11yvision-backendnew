import threading
from typing import Callable
import traceback

from worker import run_scan


def start_scan(scan_id: str, url: str, set_status: Callable[[str, dict], None]) -> None:
    """Start a background scan and update status via provided setter."""

    def job():
        print(f"\n{'='*60}")
        print(f"Starting scan: {scan_id}")
        print(f"URL: {url}")
        print(f"{'='*60}\n")

        try:
            set_status(scan_id, {'status': 'running'})
            print(f"[{scan_id}] Status set to 'running', calling run_scan...")

            res = run_scan(url)

            print(f"[{scan_id}] Scan completed successfully!")
            print(f"[{scan_id}] Found {len(res.get('issues', []))} issues")

            set_status(scan_id, {'status': 'done', 'result': res})
            print(f"[{scan_id}] Status set to 'done'")

        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()

            print(f"\n{'!'*60}")
            print(f"[{scan_id}] SCAN FAILED!")
            print(f"Error: {error_msg}")
            print(f"{'!'*60}")
            print(error_trace)
            print(f"{'!'*60}\n")

            set_status(scan_id, {
                'status': 'error',
                'error': error_msg,
                'errorDetails': error_trace[:500]  # Truncate for storage
            })

    # Use daemon=False to prevent premature termination
    t = threading.Thread(target=job, daemon=False, name=f"ScanThread-{scan_id[:8]}")
    t.start()
    print(f"[{scan_id}] Background thread started: {t.name}")