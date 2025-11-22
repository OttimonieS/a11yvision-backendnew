"""
Setup script to install Playwright browsers and verify the installation.
Run this if you're getting errors when scanning websites.
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - TIMEOUT (took more than 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_playwright():
    """Check if Playwright is installed."""
    try:
        import playwright
        print(f"✅ Playwright is installed (version: {playwright.__version__})")
        return True
    except ImportError:
        print("❌ Playwright is not installed")
        return False

def check_opencv():
    """Check if OpenCV is installed."""
    try:
        import cv2
        print(f"✅ OpenCV is installed (version: {cv2.__version__})")
        return True
    except ImportError:
        print("❌ OpenCV (cv2) is not installed")
        return False

def test_scan():
    """Test a simple scan."""
    print(f"\n{'='*60}")
    print("Testing Scan Functionality")
    print(f"{'='*60}")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'app'))
        from worker import run_scan
        
        print("Running test scan on example.com...")
        result = run_scan("https://example.com")
        
        print(f"\n✅ Scan completed successfully!")
        print(f"   - Found {result['summary']['total_issues']} issues")
        print(f"   - Screenshot saved to: {result['screenshotPath']}")
        print(f"   - Report saved to: {result['reportPath']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Scan test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     A11y Vision - Playwright Setup & Verification         ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check if Playwright is installed
    if not check_playwright():
        print("\n⚠️  Installing Playwright...")
        run_command("pip install playwright", "Install Playwright")
        check_playwright()
    
    # Step 2: Check OpenCV
    if not check_opencv():
        print("\n⚠️  Installing OpenCV...")
        run_command("pip install opencv-python", "Install OpenCV")
        check_opencv()
    
    # Step 3: Install Playwright browsers
    success = run_command(
        "playwright install chromium",
        "Install Chromium browser for Playwright"
    )
    
    if not success:
        print("\n⚠️  Trying alternative installation method...")
        run_command(
            "python -m playwright install chromium",
            "Install Chromium (alternative method)"
        )
    
    # Step 4: Install system dependencies (Linux only)
    if sys.platform.startswith('linux'):
        print("\n🐧 Detected Linux - installing system dependencies...")
        run_command(
            "playwright install-deps chromium",
            "Install system dependencies for Chromium"
        )
    
    # Step 5: Verify installation
    print(f"\n{'='*60}")
    print("Verifying Playwright Installation")
    print(f"{'='*60}")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            print("✅ Playwright sync API is working")
            browser = p.chromium.launch(headless=True)
            print("✅ Chromium browser launched successfully")
            browser.close()
            print("✅ Browser closed successfully")
            
        print("\n🎉 Playwright is fully functional!")
        
    except Exception as e:
        print(f"\n❌ Playwright verification failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n📋 Troubleshooting steps:")
        print("   1. Run: playwright install chromium")
        print("   2. Run: playwright install-deps (Linux only)")
        print("   3. Check firewall/antivirus settings")
        print("   4. Try running with administrator privileges")
        return
    
    # Step 6: Test actual scanning
    print("\n" + "="*60)
    test_scan()
    
    print(f"\n{'='*60}")
    print("Setup Complete!")
    print(f"{'='*60}")
    print("\n✅ Your environment is ready for accessibility scanning!")
    print("\nNext steps:")
    print("   1. Start the server: uvicorn main:app --reload")
    print("   2. Visit: http://localhost:8000/docs")
    print("   3. Try scanning a website through the API")

if __name__ == "__main__":
    main()
