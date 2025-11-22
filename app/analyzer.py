import numpy as np
import cv2
from PIL import Image
from typing import List, Dict, Any


def pil_to_cv(img: Image.Image):
	return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def calculate_contrast_ratio(color1, color2):
	"""Calculate WCAG contrast ratio between two colors."""
	def get_luminance(rgb):
		"""Calculate relative luminance."""
		rgb_normalized = [c / 255.0 for c in rgb]
		rgb_linear = []
		for c in rgb_normalized:
			if c <= 0.03928:
				rgb_linear.append(c / 12.92)
			else:
				rgb_linear.append(((c + 0.055) / 1.055) ** 2.4)
		return 0.2126 * rgb_linear[0] + 0.7152 * rgb_linear[1] + 0.0722 * rgb_linear[2]

	l1 = get_luminance(color1)
	l2 = get_luminance(color2)

	lighter = max(l1, l2)
	darker = min(l1, l2)

	return (lighter + 0.05) / (darker + 0.05)


def get_dominant_colors(img_region):
	"""Get the two most dominant colors in a region (background and foreground)."""
	pixels = img_region.reshape(-1, 3)
	# Simple approach: get brightest and darkest average colors
	mean_color = np.mean(pixels, axis=0).astype(int)
	min_color = np.min(pixels, axis=0).astype(int)
	max_color = np.max(pixels, axis=0).astype(int)

	# Return the two most contrasting - convert to Python int for JSON serialization
	return tuple(int(c) for c in max_color), tuple(int(c) for c in min_color)


def analyze_image(pil_img: Image.Image, page_elements: List[Dict] = None):
	"""
	Enhanced accessibility analyzer with detailed issue reporting.
	Detects low contrast regions and small interactive elements with comprehensive details.

	Args:
		pil_img: PIL Image to analyze
		page_elements: Optional list of DOM elements from page analysis with structure:
			[{'selector': str, 'bbox': dict, 'text': str, 'tag': str, 'role': str}]
	"""
	img = pil_to_cv(pil_img)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	height, width = gray.shape

	# compute local contrast: difference between local max and min in a window
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
	local_max = cv2.dilate(gray, kernel)
	local_min = cv2.erode(gray, kernel)
	local_contrast = (local_max.astype(int) - local_min.astype(int)).astype(np.uint8)

	# threshold low contrast (small difference)
	_, low_contrast_mask = cv2.threshold(local_contrast, 18, 255, cv2.THRESH_BINARY_INV)

	# find contours of low contrast areas
	contours, _ = cv2.findContours(low_contrast_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	issues = []

	# Analyze low contrast issues
	for i, cnt in enumerate(contours):
		x, y, cw, ch = cv2.boundingRect(cnt)
		area = cw * ch
		if area < 500:  # skip small noise
			continue

		# Extract the region to analyze colors
		region = img[y:y+ch, x:x+cw]
		if region.size == 0:
			continue

		# Get dominant colors and calculate contrast ratio
		fg_color, bg_color = get_dominant_colors(region)
		contrast_ratio = calculate_contrast_ratio(fg_color, bg_color)

		# Determine WCAG compliance
		wcag_aa_pass = contrast_ratio >= 4.5
		wcag_aaa_pass = contrast_ratio >= 7.0

		# Calculate position percentages
		x_percent = round((x / width) * 100, 1)
		y_percent = round((y / height) * 100, 1)

		# Build detailed message
		message = f"Low contrast detected (ratio: {contrast_ratio:.2f}:1). "
		if not wcag_aa_pass:
			message += f"Fails WCAG AA (requires 4.5:1 minimum). "
		if not wcag_aaa_pass:
			message += f"Fails WCAG AAA (requires 7:1). "
		message += f"Foreground: RGB{fg_color}, Background: RGB{bg_color}. "
		message += f"Location: {x_percent}% from left, {y_percent}% from top. "
		message += f"Recommendation: Increase contrast between text and background to at least 4.5:1 for normal text or 3:1 for large text (18pt+)."

		issues.append({
			'id': f'A11Y-LOWCON-{i}',
			'rule': 'low-contrast',
			'wcag': ['1.4.3', '1.4.6'],
			'severity': 'critical' if contrast_ratio < 3.0 else 'serious',
			'confidence': 0.75,
			'message': message,
			'bbox': {'x': int(x), 'y': int(y), 'w': int(cw), 'h': int(ch)},
			'details': {
				'contrast_ratio': round(contrast_ratio, 2),
				'foreground_color': fg_color,
				'background_color': bg_color,
				'wcag_aa_pass': wcag_aa_pass,
				'wcag_aaa_pass': wcag_aaa_pass,
				'position': {
					'x_percent': x_percent,
					'y_percent': y_percent,
					'x_px': int(x),
					'y_px': int(y),
					'width': int(cw),
					'height': int(ch)
				},
				'recommendation': 'Increase color contrast to meet WCAG 2.1 Level AA requirements (4.5:1 for normal text, 3:1 for large text)',
				'how_to_fix': [
					'Use a color contrast checker tool to find compliant color combinations',
					'Darken the text color or lighten the background color',
					'Consider using bold text to improve readability',
					'Test with different color blindness simulations'
				]
			}
		})

	# Detect small interactive elements (target-size issues)
	# Look for button-like or link-like elements
	edges = cv2.Canny(gray, 50, 150)
	contours2, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Also detect bright/dark clickable-looking regions
	_, bw_bright = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
	_, bw_dark = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
	combined = cv2.bitwise_or(bw_bright, bw_dark)
	contours3, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	all_potential_targets = list(contours2) + list(contours3)

	for j, cnt in enumerate(all_potential_targets):
		x, y, cw, ch = cv2.boundingRect(cnt)

		# WCAG 2.5.8: Target size should be at least 24x24 CSS pixels
		# We'll flag anything smaller than 44x44px (mobile-friendly guideline)
		min_dimension = min(cw, ch)

		if 8 < cw < 44 or 8 < ch < 44:
			# Calculate how much it falls short
			target_size = 44
			width_shortage = max(0, target_size - cw)
			height_shortage = max(0, target_size - ch)

			# Position information
			x_percent = round((x / width) * 100, 1)
			y_percent = round((y / height) * 100, 1)

			# Determine severity based on size
			if min_dimension < 24:
				severity = 'serious'
				wcag_level = 'AA (Level 2.5.8)'
			else:
				severity = 'minor'
				wcag_level = 'AAA (Enhanced)'

			message = f"Small interactive target detected ({cw}x{ch}px). "
			message += f"WCAG 2.5.8 requires minimum 24x24px, recommended 44x44px for touch targets. "
			message += f"Current target is {width_shortage}px too narrow and {height_shortage}px too short. "
			message += f"Location: {x_percent}% from left, {y_percent}% from top. "
			message += f"Recommendation: Increase tap/click target size to at least 44x44 pixels with adequate spacing."

			issues.append({
				'id': f'A11Y-SMALLTARGET-{j}',
				'rule': 'target-size',
				'wcag': ['2.5.8'],
				'severity': severity,
				'confidence': 0.65,
				'message': message,
				'bbox': {'x': int(x), 'y': int(y), 'w': int(cw), 'h': int(ch)},
				'details': {
					'current_size': {'width': int(cw), 'height': int(ch)},
					'required_size': {'width': 24, 'height': 24},
					'recommended_size': {'width': 44, 'height': 44},
					'shortage': {'width': int(width_shortage), 'height': int(height_shortage)},
					'position': {
						'x_percent': x_percent,
						'y_percent': y_percent,
						'x_px': int(x),
						'y_px': int(y),
						'width': int(cw),
						'height': int(ch)
					},
					'wcag_level': wcag_level,
					'recommendation': 'Increase clickable/tappable area to minimum 44x44 pixels',
					'how_to_fix': [
						'Add CSS padding to increase the clickable area',
						'Use min-width and min-height CSS properties',
						'Ensure adequate spacing (at least 8px) between adjacent targets',
						'Consider making the entire parent container clickable',
						'Test on mobile devices with actual finger taps'
					]
				}
			})

	return issues