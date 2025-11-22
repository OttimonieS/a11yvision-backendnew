"""
Visualizer for accessibility issues - annotates screenshots with issue markers
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Dict, Any


def draw_issue_overlay(screenshot_path: str, issues: List[Dict[str, Any]], output_path: str = None) -> str:
    """
    Draw bounding boxes and labels on screenshot for all detected issues.

    Args:
        screenshot_path: Path to original screenshot
        issues: List of issue dictionaries with bbox and details
        output_path: Optional output path, defaults to screenshot_path with '_annotated' suffix

    Returns:
        Path to annotated image
    """
    # Load image
    img = cv2.imread(screenshot_path)
    if img is None:
        raise ValueError(f"Could not load screenshot: {screenshot_path}")

    # Convert to RGB for PIL
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img, 'RGBA')

    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 11)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Color coding by severity
    severity_colors = {
        'critical': (220, 38, 38, 180),    # Red
        'serious': (251, 146, 60, 180),    # Orange
        'minor': (250, 204, 21, 180),      # Yellow
        'moderate': (59, 130, 246, 180)    # Blue
    }

    # Draw each issue
    for idx, issue in enumerate(issues):
        bbox = issue.get('bbox', {})
        x = bbox.get('x', 0)
        y = bbox.get('y', 0)
        w = bbox.get('w', 0)
        h = bbox.get('h', 0)

        severity = issue.get('severity', 'minor')
        color = severity_colors.get(severity, (128, 128, 128, 180))

        # Draw semi-transparent rectangle
        draw.rectangle([x, y, x + w, y + h], outline=color[:3], width=3)
        draw.rectangle([x, y, x + w, y + h], fill=color)

        # Draw label with issue number and type
        rule = issue.get('rule', 'unknown')
        label = f"#{idx+1}: {rule}"

        # Draw label background
        label_bbox = draw.textbbox((x, y - 20), label, font=font)
        label_bg = (label_bbox[0] - 2, label_bbox[1] - 2, label_bbox[2] + 2, label_bbox[3] + 2)
        draw.rectangle(label_bg, fill=color[:3])
        draw.text((x, y - 20), label, fill=(255, 255, 255), font=font)

        # Add details if available
        details = issue.get('details', {})
        if 'contrast_ratio' in details:
            ratio_text = f"{details['contrast_ratio']:.2f}:1"
            draw.text((x + 5, y + 5), ratio_text, fill=(255, 255, 255), font=font_small)
        elif 'current_size' in details:
            size = details['current_size']
            size_text = f"{size['width']}x{size['height']}px"
            draw.text((x + 5, y + 5), size_text, fill=(255, 255, 255), font=font_small)

    # Add legend
    legend_y = 10
    legend_x = 10
    draw.rectangle([legend_x, legend_y, legend_x + 250, legend_y + 120],
                   fill=(255, 255, 255, 230), outline=(0, 0, 0))

    draw.text((legend_x + 10, legend_y + 5), "Accessibility Issues Legend:",
              fill=(0, 0, 0), font=font)

    y_offset = legend_y + 25
    for severity, color in severity_colors.items():
        draw.rectangle([legend_x + 10, y_offset, legend_x + 30, y_offset + 15],
                      fill=color[:3], outline=(0, 0, 0))
        count = sum(1 for i in issues if i.get('severity') == severity)
        draw.text((legend_x + 35, y_offset), f"{severity.capitalize()}: {count}",
                 fill=(0, 0, 0), font=font_small)
        y_offset += 20

    # Save annotated image
    if output_path is None:
        path = Path(screenshot_path)
        output_path = str(path.parent / f"{path.stem}_annotated{path.suffix}")

    # Convert back to BGR for OpenCV
    annotated_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, annotated_img)

    return output_path


def generate_issue_report_html(issues: List[Dict[str, Any]], screenshot_path: str,
                               page_info: Dict[str, Any] = None) -> str:
    """
    Generate an HTML report for the accessibility issues.

    Args:
        issues: List of detected issues
        screenshot_path: Path to screenshot
        page_info: Optional page metadata

    Returns:
        HTML string
    """
    page_title = page_info.get('title', 'Unknown') if page_info else 'Unknown'
    page_url = page_info.get('url', 'Unknown') if page_info else 'Unknown'

    # Count issues by severity
    critical = sum(1 for i in issues if i.get('severity') == 'critical')
    serious = sum(1 for i in issues if i.get('severity') == 'serious')
    minor = sum(1 for i in issues if i.get('severity') == 'minor')

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Accessibility Report - {page_title}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                margin: 0 0 10px 0;
                color: #1a1a1a;
            }}
            .summary {{
                display: flex;
                gap: 15px;
                margin-top: 15px;
            }}
            .summary-card {{
                flex: 1;
                padding: 15px;
                border-radius: 6px;
                color: white;
                text-align: center;
            }}
            .critical {{ background: #dc2626; }}
            .serious {{ background: #fb923c; }}
            .minor {{ background: #facc15; color: #1a1a1a; }}
            .issue {{
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 4px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .issue.critical {{ border-left-color: #dc2626; }}
            .issue.serious {{ border-left-color: #fb923c; }}
            .issue.minor {{ border-left-color: #facc15; }}
            .issue-header {{
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 10px;
            }}
            .issue-title {{
                font-weight: 600;
                font-size: 1.1em;
                color: #1a1a1a;
            }}
            .badge {{
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: 500;
            }}
            .badge.critical {{ background: #fee2e2; color: #dc2626; }}
            .badge.serious {{ background: #ffedd5; color: #fb923c; }}
            .badge.minor {{ background: #fef9c3; color: #ca8a04; }}
            .issue-message {{
                color: #4b5563;
                line-height: 1.6;
                margin: 10px 0;
            }}
            .details {{
                background: #f9fafb;
                padding: 15px;
                border-radius: 6px;
                margin-top: 15px;
            }}
            .detail-row {{
                margin: 8px 0;
                display: flex;
                gap: 10px;
            }}
            .detail-label {{
                font-weight: 600;
                min-width: 150px;
                color: #374151;
            }}
            .detail-value {{
                color: #6b7280;
            }}
            .how-to-fix {{
                margin-top: 15px;
                padding: 15px;
                background: #eff6ff;
                border-left: 3px solid #3b82f6;
                border-radius: 4px;
            }}
            .how-to-fix h4 {{
                margin: 0 0 10px 0;
                color: #1e40af;
            }}
            .how-to-fix ul {{
                margin: 0;
                padding-left: 20px;
            }}
            .how-to-fix li {{
                margin: 5px 0;
                color: #1e3a8a;
            }}
            code {{
                background: #e5e7eb;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Accessibility Scan Report</h1>
            <p><strong>Page:</strong> {page_title}</p>
            <p><strong>URL:</strong> {page_url}</p>
            <div class="summary">
                <div class="summary-card critical">
                    <div style="font-size: 2em; font-weight: bold;">{critical}</div>
                    <div>Critical Issues</div>
                </div>
                <div class="summary-card serious">
                    <div style="font-size: 2em; font-weight: bold;">{serious}</div>
                    <div>Serious Issues</div>
                </div>
                <div class="summary-card minor">
                    <div style="font-size: 2em; font-weight: bold;">{minor}</div>
                    <div>Minor Issues</div>
                </div>
            </div>
        </div>
    """

    for idx, issue in enumerate(issues, 1):
        severity = issue.get('severity', 'minor')
        rule = issue.get('rule', 'unknown')
        message = issue.get('message', '')
        wcag = issue.get('wcag', [])
        details = issue.get('details', {})

        html += f"""
        <div class="issue {severity}">
            <div class="issue-header">
                <div class="issue-title">#{idx}: {rule.replace('-', ' ').title()}</div>
                <span class="badge {severity}">{severity.upper()}</span>
            </div>
            <div class="issue-message">{message}</div>
            <div class="details">
                <div class="detail-row">
                    <span class="detail-label">WCAG Criteria:</span>
                    <span class="detail-value">{', '.join(wcag)}</span>
                </div>
        """

        # Add specific details based on issue type
        if 'position' in details:
            pos = details['position']
            html += f"""
                <div class="detail-row">
                    <span class="detail-label">Position:</span>
                    <span class="detail-value">{pos.get('x_percent', 0)}% from left, {pos.get('y_percent', 0)}% from top ({pos.get('x_px', 0)}, {pos.get('y_px', 0)}px)</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Size:</span>
                    <span class="detail-value">{pos.get('width', 0)} × {pos.get('height', 0)} pixels</span>
                </div>
            """

        if 'contrast_ratio' in details:
            html += f"""
                <div class="detail-row">
                    <span class="detail-label">Contrast Ratio:</span>
                    <span class="detail-value">{details['contrast_ratio']}:1</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Foreground Color:</span>
                    <span class="detail-value">RGB{details.get('foreground_color', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Background Color:</span>
                    <span class="detail-value">RGB{details.get('background_color', 'N/A')}</span>
                </div>
            """

        if 'element' in details:
            elem = details['element']
            html += f"""
                <div class="detail-row">
                    <span class="detail-label">Element:</span>
                    <span class="detail-value"><code>{elem.get('selector', 'N/A')}</code></span>
                </div>
            """
            if elem.get('text'):
                html += f"""
                <div class="detail-row">
                    <span class="detail-label">Text Content:</span>
                    <span class="detail-value">"{elem['text'][:100]}"</span>
                </div>
                """

        html += "</div>"

        # Add how to fix section
        if 'how_to_fix' in details:
            html += """
                <div class="how-to-fix">
                    <h4>How to Fix:</h4>
                    <ul>
            """
            for fix in details['how_to_fix']:
                html += f"<li>{fix}</li>"
            html += """
                    </ul>
                </div>
            """

        html += "</div>"

    html += """
    </body>
    </html>
    """

    return html
