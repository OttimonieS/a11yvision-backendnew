import threading
from typing import Callable

from worker import run_scan


def start_scan(scan_id: str, url: str, set_status: Callable[[str, dict], None]) -> None:
    """Start a background scan and update status via provided setter."""

    def job():
        try:
            set_status(scan_id, {'status': 'running'})
            res = run_scan(url)
            set_status(scan_id, {'status': 'done', 'result': res})
        except Exception as e:  # noqa: BLE001
            set_status(scan_id, {'status': 'error', 'error': str(e)})

    t = threading.Thread(target=job, daemon=True)
    t.start()