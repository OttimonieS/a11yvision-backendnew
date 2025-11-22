# Accessibility Scanning - Quick Reference

## Running a Scan

### Basic Usage

```python
from app.worker import run_scan

result = run_scan("https://example.com")
```

### What You Get Back

```python
{
  "url": "https://example.com",
  "issues": [...],  # Detailed issue list
  "screenshotPath": "path/to/screenshot.png",
  "annotatedScreenshotPath": "path/to/screenshot_annotated.png",
  "reportPath": "path/to/report.json",
  "htmlReportPath": "path/to/report.html",
  "summary": {
    "total_issues": 45,
    "critical": 3,
    "serious": 12,
    "minor": 30
  }
}
```

## Issue Structure

### Every Issue Contains

| Field        | Description            | Example                              |
| ------------ | ---------------------- | ------------------------------------ |
| `id`         | Unique identifier      | `"A11Y-LOWCON-0"`                    |
| `rule`       | Type of issue          | `"low-contrast"` or `"target-size"`  |
| `severity`   | Impact level           | `"critical"`, `"serious"`, `"minor"` |
| `wcag`       | WCAG criteria violated | `["1.4.3", "1.4.6"]`                 |
| `confidence` | Detection confidence   | `0.75` (75%)                         |
| `message`    | Full description       | See examples below                   |
| `bbox`       | Bounding box           | `{x: 100, y: 200, w: 300, h: 50}`    |
| `details`    | Extended information   | See below                            |

### Low Contrast Issue Details

```json
{
  "contrast_ratio": 2.31,
  "foreground_color": [150, 150, 150],
  "background_color": [200, 200, 200],
  "wcag_aa_pass": false,
  "wcag_aaa_pass": false,
  "position": {
    "x_percent": 45.2,
    "y_percent": 60.3,
    "x_px": 579,
    "y_px": 482,
    "width": 300,
    "height": 50
  },
  "element": {
    "selector": "button.submit-btn",
    "tag": "button",
    "text": "Submit",
    "role": "button"
  },
  "recommendation": "Increase color contrast...",
  "how_to_fix": [
    "Use a color contrast checker tool...",
    "Darken the text color or lighten the background...",
    "..."
  ]
}
```

### Target Size Issue Details

```json
{
  "current_size": {"width": 28, "height": 32},
  "required_size": {"width": 24, "height": 24},
  "recommended_size": {"width": 44, "height": 44},
  "shortage": {"width": 16, "height": 12},
  "position": {...},
  "element": {...},
  "how_to_fix": [
    "Add CSS padding to increase the clickable area",
    "Use min-width and min-height CSS properties",
    "..."
  ]
}
```

## Understanding Severity Levels

### Critical

- **Contrast ratio < 3:1** - Extremely hard to read
- **Immediate action required**
- Affects users with low vision and color blindness

### Serious

- **Contrast ratio 3:1 - 4.5:1** - Fails WCAG AA
- **Target size < 24px** - Too small for touch/click
- Affects mobile users and users with motor disabilities

### Minor

- **Contrast ratio 4.5:1 - 7:1** - Passes AA, fails AAA
- **Target size 24-44px** - Meets minimum, but not ideal
- Minor improvements recommended

## Location Information

Every issue tells you WHERE it is:

```python
position = issue['details']['position']

# Multiple ways to locate:
position['x_percent']  # 45.2 (45.2% from left edge)
position['y_percent']  # 60.3 (60.3% from top)
position['x_px']       # 579 (exact pixel from left)
position['y_px']       # 482 (exact pixel from top)
position['width']      # 300 (element width)
position['height']     # 50 (element height)

# Plus the CSS selector:
element = issue['details']['element']
element['selector']    # "button.submit-btn"
```

## WCAG Compliance Levels

### Contrast Requirements

| Text Size            | WCAG AA | WCAG AAA |
| -------------------- | ------- | -------- |
| Normal text (< 18pt) | 4.5:1   | 7:1      |
| Large text (≥ 18pt)  | 3:1     | 4.5:1    |
| UI components        | 3:1     | -        |

### Target Size Requirements

| Standard             | Minimum Size          | Notes                   |
| -------------------- | --------------------- | ----------------------- |
| WCAG 2.5.8 (AA)      | 24×24px               | Level AA requirement    |
| Mobile Best Practice | 44×44px               | Apple/Google guidelines |
| Recommended          | 44×44px + 8px spacing | Optimal for all users   |

## Working with Reports

### JSON Report

```python
import json

with open(result['reportPath'], 'r') as f:
    data = json.load(f)

# Access all data
for issue in data['issues']:
    print(f"{issue['rule']}: {issue['message']}")
```

### HTML Report

- Open in any browser
- Professional layout
- All details included
- Print-ready
- Shareable

### Annotated Screenshot

- Visual representation
- Color-coded by severity:
  - 🔴 Red = Critical
  - 🟠 Orange = Serious
  - 🟡 Yellow = Minor
- Numbered issues match report

## Common Queries

### How many critical issues?

```python
critical_count = result['summary']['critical']
```

### What issues are at a specific location?

```python
issues_at_top = [
    i for i in result['issues']
    if i['details']['position']['y_percent'] < 25
]
```

### Which elements have contrast issues?

```python
contrast_issues = [
    i for i in result['issues']
    if i['rule'] == 'low-contrast'
]

for issue in contrast_issues:
    elem = issue['details']['element']
    print(f"{elem['selector']}: {issue['details']['contrast_ratio']}:1")
```

### Get all selectors with issues?

```python
selectors = [
    i['details']['element']['selector']
    for i in result['issues']
    if 'element' in i['details']
]
```

## Fixing Issues

### For Contrast Issues

1. Check the RGB values provided
2. Use contrast ratio calculator
3. Adjust colors to meet 4.5:1 minimum
4. Rescan to verify

### For Target Size Issues

1. Note current size and shortage
2. Add CSS padding or min-width/height
3. Ensure 8px spacing between targets
4. Test on mobile devices
5. Rescan to verify

## Example: Complete Workflow

```python
# 1. Run scan
result = run_scan("https://mysite.com")

# 2. Check summary
print(f"Found {result['summary']['total_issues']} issues")

# 3. Review critical issues first
critical = [i for i in result['issues'] if i['severity'] == 'critical']

for issue in critical:
    print(f"\nFIX THIS: {issue['message']}")
    print(f"Element: {issue['details']['element']['selector']}")
    print("\nHow to fix:")
    for fix in issue['details']['how_to_fix']:
        print(f"  - {fix}")

# 4. Open HTML report for full details
import webbrowser
webbrowser.open(result['htmlReportPath'])

# 5. After fixes, rescan
result2 = run_scan("https://mysite.com")
improvement = result['summary']['total_issues'] - result2['summary']['total_issues']
print(f"Fixed {improvement} issues!")
```

## Tips

1. **Always fix critical issues first** - Biggest impact
2. **Use the HTML report** - Easier to read and share
3. **Check the annotated screenshot** - See visual context
4. **Follow the how_to_fix guides** - Specific to each issue
5. **Rescan after fixes** - Verify improvements
6. **Export JSON for tracking** - Monitor progress over time
