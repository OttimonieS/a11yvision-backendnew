from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List
import json

from PIL import Image
from playwright.sync_api import sync_playwright

from analyzer import analyze_image
from visualizer import draw_issue_overlay, generate_issue_report_html


def extract_page_elements(page) -> List[Dict]:
	"""Extract interactive elements from the page DOM for enhanced analysis."""
	try:
		elements = page.evaluate("""
			() => {
				const interactiveSelectors = 'a, button, input, select, textarea, [role="button"], [role="link"], [onclick]';
				const elements = Array.from(document.querySelectorAll(interactiveSelectors));

				return elements.map((el, index) => {
					const rect = el.getBoundingClientRect();
					const styles = window.getComputedStyle(el);

					// Get element path
					const getPath = (element) => {
						if (element.id) return '#' + element.id;
						if (element.className && typeof element.className === 'string') {
							const classes = element.className.trim().split(/\\s+/).slice(0, 2).join('.');
							if (classes) return element.tagName.toLowerCase() + '.' + classes;
						}
						return element.tagName.toLowerCase();
					};

					return {
						index: index,
						selector: getPath(el),
						tag: el.tagName.toLowerCase(),
						text: el.textContent?.trim().substring(0, 100) || '',
						role: el.getAttribute('role') || el.tagName.toLowerCase(),
						ariaLabel: el.getAttribute('aria-label') || '',
						bbox: {
							x: Math.round(rect.x),
							y: Math.round(rect.y),
							width: Math.round(rect.width),
							height: Math.round(rect.height)
						},
						styles: {
							color: styles.color,
							backgroundColor: styles.backgroundColor,
							fontSize: styles.fontSize,
							fontWeight: styles.fontWeight
						},
						href: el.href || '',
						type: el.type || ''
					};
				}).filter(el => el.bbox.width > 0 && el.bbox.height > 0);
			}
		""")
		return elements
	except Exception as e:
		print(f"Error extracting page elements: {e}")
		return []


def enrich_issues_with_elements(issues: List[Dict], page_elements: List[Dict]) -> List[Dict]:
	"""Match detected issues with actual DOM elements for more detailed reporting."""
	for issue in issues:
		bbox = issue.get('bbox', {})
		issue_x = bbox.get('x', 0)
		issue_y = bbox.get('y', 0)
		issue_w = bbox.get('w', 0)
		issue_h = bbox.get('h', 0)

		# Find overlapping elements
		matching_elements = []
		for element in page_elements:
			el_bbox = element.get('bbox', {})
			el_x = el_bbox.get('x', 0)
			el_y = el_bbox.get('y', 0)
			el_w = el_bbox.get('width', 0)
			el_h = el_bbox.get('height', 0)

			# Check if bounding boxes overlap
			if (issue_x < el_x + el_w and issue_x + issue_w > el_x and
				issue_y < el_y + el_h and issue_y + issue_h > el_y):
				matching_elements.append(element)

		# Add element information to issue
		if matching_elements:
			# Take the first matching element (most likely candidate)
			element = matching_elements[0]

			# Enhance the message with element details
			element_desc = f"{element.get('tag', 'element')}"
			if element.get('selector'):
				element_desc += f" ({element.get('selector')})"
			if element.get('text'):
				element_desc += f" containing \"{element.get('text')[:50]}\""

			# Add to existing message
			if 'message' in issue:
				issue['message'] = f"Element: {element_desc}. " + issue['message']

			# Add element details
			if 'details' not in issue:
				issue['details'] = {}

			issue['details']['element'] = {
				'selector': element.get('selector', ''),
				'tag': element.get('tag', ''),
				'text': element.get('text', ''),
				'role': element.get('role', ''),
				'ariaLabel': element.get('ariaLabel', ''),
				'href': element.get('href', ''),
				'type': element.get('type', ''),
				'computed_styles': element.get('styles', {})
			}

	return issues


def run_scan(url: str, out_dir: Path | None = None) -> Dict[str, Any]:
	"""Render the URL in a headless browser, take a screenshot, run analysis heuristics.
	Returns a dict with url, issues, and screenshot path (if saved to disk).
	"""
	import traceback

	try:
		out_dir = out_dir or Path.cwd() / "data" / "screenshots"
		out_dir.mkdir(parents=True, exist_ok=True)
	except Exception as e:
		print(f"Error creating output directory: {e}")
		raise Exception(f"Failed to create output directory: {str(e)}")

	try:
		with sync_playwright() as p:
	try:
		with sync_playwright() as p:
			browser = p.chromium.launch(headless=True)
			context = browser.new_context(viewport={'width': 1280, 'height': 800})
			page = context.new_page()

			# Navigate to URL
			try:
				page.goto(url, timeout=30000)
				page.wait_for_load_state('networkidle', timeout=10000)
			except Exception as e:
				print(f"Error loading page {url}: {e}")
				# Continue with what we have
				pass

			# Extract page elements for detailed analysis
			page_elements = extract_page_elements(page)

			# Get page metadata
			try:
				page_info = page.evaluate("""
					() => ({
						title: document.title,
						url: window.location.href,
						lang: document.documentElement.lang || 'not specified',
						viewport: {
							width: window.innerWidth,
							height: window.innerHeight,
							scrollHeight: document.documentElement.scrollHeight
						}
					})
				""")
			except Exception as e:
				print(f"Error extracting page info: {e}")
				page_info = {
					'title': 'Unknown',
					'url': url,
					'lang': 'not specified',
					'viewport': {'width': 1280, 'height': 800, 'scrollHeight': 800}
				}

			# full page screenshot
			buffer = page.screenshot(full_page=True)
			img = Image.open(BytesIO(buffer))

			# Run analysis
			issues = analyze_image(img, page_elements)

			# Enrich issues with element information
			issues = enrich_issues_with_elements(issues, page_elements)

			# save screenshot
			screenshot_path = out_dir / f"screenshot_{abs(hash(url))}.png"
			with open(screenshot_path, 'wb') as f:
				f.write(buffer)

			# Save detailed report
			report_path = out_dir / f"report_{abs(hash(url))}.json"
			with open(report_path, 'w', encoding='utf-8') as f:
				json.dump({
					'url': url,
					'page_info': page_info,
					'issues': issues,
					'elements_analyzed': len(page_elements),
					'screenshot_path': str(screenshot_path)
				}, f, indent=2, ensure_ascii=False)

			# Generate annotated screenshot with issue markers
			annotated_path = None
			html_report_path = None
			try:
				annotated_path = draw_issue_overlay(str(screenshot_path), issues)

				# Generate HTML report
				html_report = generate_issue_report_html(issues, str(screenshot_path), page_info)
				html_report_path = out_dir / f"report_{abs(hash(url))}.html"
				with open(html_report_path, 'w', encoding='utf-8') as f:
					f.write(html_report)
			except Exception as e:
				print(f"Error generating visualizations: {e}")
				import traceback
				traceback.print_exc()

			browser.close()

		return {
			'url': url,
			'issues': issues,
			'screenshotPath': str(screenshot_path),
			'annotatedScreenshotPath': annotated_path,
			'reportPath': str(report_path),
			'htmlReportPath': str(html_report_path) if html_report_path else None,
			'pageInfo': page_info,
			'summary': {
				'total_issues': len(issues),
				'critical': sum(1 for i in issues if i.get('severity') == 'critical'),
				'serious': sum(1 for i in issues if i.get('severity') == 'serious'),
				'minor': sum(1 for i in issues if i.get('severity') == 'minor'),
				'elements_analyzed': len(page_elements)
			}
		}

	except Exception as e:
		print(f"Critical error in run_scan: {e}")
		import traceback
		traceback.print_exc()
		raise Exception(f"Scan failed: {str(e)}. Please ensure Playwright browsers are installed (run: playwright install chromium)")