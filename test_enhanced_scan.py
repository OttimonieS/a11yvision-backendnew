"""
Test script to demonstrate enhanced accessibility scanning
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from worker import run_scan
import json


def test_scan(url: str):
    """Run a scan and display detailed results."""
    print(f"\n{'='*80}")
    print(f"Scanning: {url}")
    print(f"{'='*80}\n")
    
    try:
        result = run_scan(url)
        
        # Display summary
        print("SCAN SUMMARY")
        print("-" * 80)
        print(f"Page Title: {result['pageInfo']['title']}")
        print(f"Page URL: {result['pageInfo']['url']}")
        print(f"Total Issues: {result['summary']['total_issues']}")
        print(f"  - Critical: {result['summary']['critical']}")
        print(f"  - Serious: {result['summary']['serious']}")
        print(f"  - Minor: {result['summary']['minor']}")
        print(f"Elements Analyzed: {result['summary']['elements_analyzed']}")
        print(f"\nFiles Generated:")
        print(f"  - Screenshot: {result['screenshotPath']}")
        print(f"  - Annotated Screenshot: {result.get('annotatedScreenshotPath', 'N/A')}")
        print(f"  - JSON Report: {result['reportPath']}")
        print(f"  - HTML Report: {result.get('htmlReportPath', 'N/A')}")
        
        # Display detailed issues
        print(f"\n{'='*80}")
        print("DETAILED ISSUES")
        print(f"{'='*80}\n")
        
        for idx, issue in enumerate(result['issues'][:10], 1):  # Show first 10 issues
            print(f"\nIssue #{idx}: {issue['rule'].upper()}")
            print("-" * 80)
            print(f"Severity: {issue['severity'].upper()}")
            print(f"WCAG: {', '.join(issue['wcag'])}")
            print(f"Confidence: {issue['confidence']*100}%")
            print(f"\nMessage:")
            print(f"  {issue['message'][:200]}...")
            
            details = issue.get('details', {})
            
            # Show position
            if 'position' in details:
                pos = details['position']
                print(f"\nPosition:")
                print(f"  Location: {pos['x_percent']}% from left, {pos['y_percent']}% from top")
                print(f"  Coordinates: ({pos['x_px']}, {pos['y_px']})px")
                print(f"  Size: {pos['width']} × {pos['height']}px")
            
            # Show contrast details
            if 'contrast_ratio' in details:
                print(f"\nContrast Details:")
                print(f"  Ratio: {details['contrast_ratio']}:1")
                print(f"  Foreground: RGB{details['foreground_color']}")
                print(f"  Background: RGB{details['background_color']}")
                print(f"  WCAG AA: {'PASS' if details['wcag_aa_pass'] else 'FAIL'}")
                print(f"  WCAG AAA: {'PASS' if details['wcag_aaa_pass'] else 'FAIL'}")
            
            # Show target size details
            if 'current_size' in details:
                print(f"\nTarget Size Details:")
                print(f"  Current: {details['current_size']['width']}×{details['current_size']['height']}px")
                print(f"  Required: {details['required_size']['width']}×{details['required_size']['height']}px")
                print(f"  Recommended: {details['recommended_size']['width']}×{details['recommended_size']['height']}px")
                print(f"  Shortage: {details['shortage']['width']}px wide, {details['shortage']['height']}px tall")
            
            # Show element details
            if 'element' in details:
                elem = details['element']
                print(f"\nElement Details:")
                print(f"  Selector: {elem.get('selector', 'N/A')}")
                print(f"  Tag: {elem.get('tag', 'N/A')}")
                if elem.get('text'):
                    print(f"  Text: \"{elem['text'][:50]}...\"")
                if elem.get('role'):
                    print(f"  Role: {elem['role']}")
            
            # Show how to fix
            if 'how_to_fix' in details:
                print(f"\nHow to Fix:")
                for i, fix in enumerate(details['how_to_fix'][:3], 1):
                    print(f"  {i}. {fix}")
        
        if len(result['issues']) > 10:
            print(f"\n... and {len(result['issues']) - 10} more issues")
        
        print(f"\n{'='*80}")
        print(f"View the full HTML report at: {result.get('htmlReportPath', 'N/A')}")
        print(f"{'='*80}\n")
        
        return result
        
    except Exception as e:
        print(f"Error during scan: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test with a sample URL
    test_url = input("Enter URL to scan (or press Enter for example.com): ").strip()
    if not test_url:
        test_url = "https://example.com"
    
    result = test_scan(test_url)
    
    if result:
        print("\n✅ Scan completed successfully!")
        print("\nNext steps:")
        print(f"1. Open the HTML report: {result.get('htmlReportPath', 'N/A')}")
        print(f"2. View the annotated screenshot: {result.get('annotatedScreenshotPath', 'N/A')}")
        print(f"3. Check the JSON data: {result['reportPath']}")
