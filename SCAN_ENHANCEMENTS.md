# Enhanced Accessibility Scanning Features

## Overview
The accessibility scanner has been significantly enhanced to provide detailed, actionable insights about accessibility issues on websites.

## What's New

### 1. Detailed Issue Information
Each issue now includes:
- **Precise location**: Pixel coordinates and percentage positions
- **Element identification**: CSS selectors, tags, and text content
- **Severity levels**: Critical, Serious, Minor
- **Confidence scores**: How certain the detection is
- **WCAG criteria**: Which specific WCAG guidelines are violated

### 2. Low Contrast Detection
For contrast issues, you now get:
- **Actual contrast ratio** (e.g., 2.3:1)
- **Foreground and background colors** (RGB values)
- **WCAG compliance status** (AA and AAA levels)
- **Exact position** on the page
- **How to fix** with specific recommendations

**Example Output:**
```json
{
  "id": "A11Y-LOWCON-0",
  "rule": "low-contrast",
  "severity": "critical",
  "message": "Element: button (.submit-btn) containing \"Submit\". Low contrast detected (ratio: 2.31:1). Fails WCAG AA (requires 4.5:1 minimum). Foreground: RGB(150, 150, 150), Background: RGB(200, 200, 200). Location: 45.2% from left, 60.3% from top.",
  "details": {
    "contrast_ratio": 2.31,
    "foreground_color": [150, 150, 150],
    "background_color": [200, 200, 200],
    "wcag_aa_pass": false,
    "wcag_aaa_pass": false,
    "position": {
      "x_percent": 45.2,
      "y_percent": 60.3,
      "x_px": 579,
      "y_px": 482
    },
    "element": {
      "selector": "button.submit-btn",
      "tag": "button",
      "text": "Submit",
      "role": "button"
    },
    "how_to_fix": [
      "Use a color contrast checker tool to find compliant color combinations",
      "Darken the text color or lighten the background color",
      "Consider using bold text to improve readability",
      "Test with different color blindness simulations"
    ]
  }
}
```

### 3. Target Size Detection
For small interactive elements, you get:
- **Current dimensions** (width × height in pixels)
- **Required vs recommended sizes** (24×24px minimum, 44×44px recommended)
- **Shortage calculation** (how many pixels too small)
- **Element details** (selector, role, text)
- **Touch target improvements** needed

**Example Output:**
```json
{
  "id": "A11Y-SMALLTARGET-5",
  "rule": "target-size",
  "severity": "serious",
  "message": "Element: a (#nav-link) containing \"Home\". Small interactive target detected (28×32px). WCAG 2.5.8 requires minimum 24×24px, recommended 44×44px for touch targets. Current target is 16px too narrow and 12px too short.",
  "details": {
    "current_size": {"width": 28, "height": 32},
    "required_size": {"width": 24, "height": 24},
    "recommended_size": {"width": 44, "height": 44},
    "shortage": {"width": 16, "height": 12},
    "element": {
      "selector": "a#nav-link",
      "tag": "a",
      "text": "Home",
      "href": "/home"
    },
    "how_to_fix": [
      "Add CSS padding to increase the clickable area",
      "Use min-width and min-height CSS properties",
      "Ensure adequate spacing (at least 8px) between adjacent targets",
      "Consider making the entire parent container clickable",
      "Test on mobile devices with actual finger taps"
    ]
  }
}
```

### 4. Visual Reports

#### Annotated Screenshots
- Bounding boxes drawn around each issue
- Color-coded by severity (red = critical, orange = serious, yellow = minor)
- Issue numbers and types labeled
- Legend showing issue counts by severity

#### HTML Reports
- Professional, readable format
- Summary dashboard with counts
- Detailed issue cards with all information
- How-to-fix sections for each issue
- Mobile-responsive design

### 5. Enhanced Scan Results

The scan now returns:
```json
{
  "url": "https://example.com",
  "issues": [...],
  "screenshotPath": "/path/to/screenshot.png",
  "annotatedScreenshotPath": "/path/to/screenshot_annotated.png",
  "reportPath": "/path/to/report.json",
  "htmlReportPath": "/path/to/report.html",
  "pageInfo": {
    "title": "Example Site",
    "url": "https://example.com",
    "lang": "en",
    "viewport": {
      "width": 1280,
      "height": 800
    }
  },
  "summary": {
    "total_issues": 45,
    "critical": 3,
    "serious": 12,
    "minor": 30,
    "elements_analyzed": 127
  }
}
```

## How Issues Are Now Categorized

### Severity Levels
- **Critical**: Contrast ratio < 3:1, completely inaccessible
- **Serious**: Contrast ratio 3-4.5:1, target size < 24px
- **Minor**: Contrast ratio 4.5-7:1 (fails AAA), target size 24-44px

### Confidence Scores
- **0.75**: High confidence (contrast calculations)
- **0.65**: Moderate confidence (target size detection)
- **0.50**: Lower confidence (heuristic-based detection)

## Where Issues Are Located

Each issue includes multiple location indicators:
1. **Absolute pixel coordinates**: `(x, y)` from top-left
2. **Percentage position**: `45% from left, 60% from top`
3. **Element selector**: CSS selector for direct targeting
4. **Text content**: What text is in the element
5. **Bounding box**: Full dimensions `(x, y, width, height)`

## Files Generated Per Scan

1. **screenshot_{hash}.png** - Original full-page screenshot
2. **screenshot_{hash}_annotated.png** - Screenshot with issue markers
3. **report_{hash}.json** - Complete data in JSON format
4. **report_{hash}.html** - Human-readable HTML report

## API Changes

The Issue model now stores:
- `details` (JSON): All enhanced information
- `wcag` (JSON array): Multiple WCAG criteria
- `message` (Text): Full descriptive message

## Using the Reports

### For Developers
1. Open the JSON report for programmatic access
2. Use the CSS selectors to locate exact elements
3. Follow the "how_to_fix" recommendations
4. Check contrast ratios with the provided RGB values

### For Designers
1. Open the HTML report in a browser
2. View the annotated screenshot
3. Read the detailed explanations
4. Use the color values to adjust designs

### For QA/Testing
1. Compare issue counts over time
2. Verify fixes by rescanning
3. Export reports for documentation
4. Track WCAG compliance levels

## Example Workflow

```python
from worker import run_scan

# Run a scan
result = run_scan("https://example.com")

# Access detailed information
print(f"Found {result['summary']['total_issues']} issues")
print(f"Critical: {result['summary']['critical']}")
print(f"View report at: {result['htmlReportPath']}")

# Each issue has full details
for issue in result['issues']:
    print(f"\nIssue: {issue['rule']}")
    print(f"Location: {issue['details']['position']}")
    print(f"Message: {issue['message']}")
    print(f"How to fix: {issue['details']['how_to_fix']}")
```

## Future Enhancements

Planned improvements:
- [ ] Keyboard navigation testing
- [ ] Screen reader compatibility checks
- [ ] Form label validation
- [ ] Alt text analysis for images
- [ ] Heading hierarchy validation
- [ ] Focus indicator checks
- [ ] Animation and motion detection
- [ ] Language attribute validation
