import numpy as np
import cv2
from PIL import Image


def pil_to_cv(img: Image.Image):
	return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def analyze_image(pil_img: Image.Image):
	"""
	Very small heuristic based analyzer.
	Detects low contrast regions using local contrast estimation and returns bounding boxes.
	This is a demo fallback until vision models are integrated.
	"""
	img = pil_to_cv(pil_img)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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
	for i, cnt in enumerate(contours):
		x, y, cw, ch = cv2.boundingRect(cnt)
		area = cw * ch
		if area < 500:  # skip small noise
			continue
		issues.append(
			{
				'id': f'A11Y-LOWCON-{i}',
				'rule': 'low-contrast',
				'wcag': ['1.4.3'],
				'severity': 'major',
				'confidence': 0.6,
				'bbox': {'x': x, 'y': y, 'w': cw, 'h': ch},
			}
		)

	# Example: detect small bright squares -> small hit target
	_, bw = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
	contours2, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	for j, cnt in enumerate(contours2):
		x, y, cw, ch = cv2.boundingRect(cnt)
		if 20 < cw < 44 and 12 < ch < 44:
			issues.append(
				{
					'id': f'A11Y-SMALLBTN-{j}',
					'rule': 'target-size',
					'wcag': ['2.5.8'],
					'severity': 'minor',
					'confidence': 0.5,
					'bbox': {'x': x, 'y': y, 'w': cw, 'h': ch},
				}
			)

	return issues