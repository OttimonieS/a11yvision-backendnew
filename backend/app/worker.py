from io import BytesIO
from pathlib import Path
from typing import Dict, Any

from PIL import Image
from playwright.sync_api import sync_playwright

from analyzer import analyze_image


def run_scan(url: str, out_dir: Path | None = None) -> Dict[str, Any]:
	"""Render the URL in a headless browser, take a screenshot, run analysis heuristics.
	Returns a dict with url, issues, and screenshot path (if saved to disk).
	"""
	out_dir = out_dir or Path.cwd() / "data" / "screenshots"
	out_dir.mkdir(parents=True, exist_ok=True)

	with sync_playwright() as p:
		browser = p.chromium.launch(headless=True)
		context = browser.new_context(viewport={'width': 1280, 'height': 800})
		page = context.new_page()
		page.goto(url, timeout=30000)
		page.wait_for_load_state('networkidle', timeout=10000)
		# full page screenshot
		buffer = page.screenshot(full_page=True)
		img = Image.open(BytesIO(buffer))
		issues = analyze_image(img)
		# save screenshot
		screenshot_path = out_dir / f"screenshot_{abs(hash(url))}.png"
		with open(screenshot_path, 'wb') as f:
			f.write(buffer)
		browser.close()

	return {'url': url, 'issues': issues, 'screenshotPath': str(screenshot_path)}