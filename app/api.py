import threading
from typing import Callable
import traceback

from worker import run_scan


def start_scan(scan_id: str, url: str, set_status: Callable[[str, dict], None]) -> None:
    """Start a background scan and update status via provided setter."""

    def job():
        try:
            set_status(scan_id, {'status': 'running'})
            res = run_scan(url)
            set_status(scan_id, {'status': 'done', 'result': res})
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            print(f"Scan error for {scan_id}: {error_msg}")
            print(error_trace)
            set_status(scan_id, {
                'status': 'error', 
                'error': error_msg,
                'errorDetails': error_trace[:500]  # Truncate for storage
            })

    t = threading.Thread(target=job, daemon=True)
    t.start()