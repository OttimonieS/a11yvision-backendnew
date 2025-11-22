# Troubleshooting Scan Errors

## Problem: Scans Always Return "Error" Status

If your scans are consistently failing with error status, follow these steps to diagnose and fix the issue.

### Step 1: Run the Setup Script

```bash
python setup_playwright.py
```

This script will:

- ✅ Check if Playwright is installed
- ✅ Check if OpenCV is installed
- ✅ Install Chromium browser for Playwright
- ✅ Install system dependencies (Linux)
- ✅ Verify the installation works
- ✅ Run a test scan

### Step 2: Manual Playwright Installation

If the setup script doesn't work, try installing manually:

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Linux only: Install system dependencies
playwright install-deps chromium
```

### Step 3: Verify Installation

Test if Playwright works:

```bash
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(); print('✅ Works!'); b.close(); p.stop()"
```

### Step 4: Check Server Logs

When running the server, watch for error messages:

```bash
cd app
uvicorn main:app --reload
```

Look for errors like:

- `Executable doesn't exist` - Playwright browsers not installed
- `ImportError: cv2` - OpenCV not installed
- `Permission denied` - File/directory permission issues

### Common Errors and Solutions

#### Error: "Executable doesn't exist at ..."

**Cause:** Playwright browsers not installed

**Solution:**

```bash
playwright install chromium
```

#### Error: "Import cv2 could not be resolved"

**Cause:** OpenCV not installed

**Solution:**

```bash
pip install opencv-python
```

#### Error: "Permission denied" or directory creation fails

**Cause:** Insufficient permissions for data directory

**Solution:**

```bash
# Create the directory manually
mkdir -p data/screenshots

# Or run with appropriate permissions
# On Linux/Mac:
sudo chown -R $USER data/
```

#### Error: "Timeout" when loading pages

**Cause:** Network issues or firewall blocking

**Solution:**

- Check internet connection
- Check firewall settings
- Try with a different URL
- Increase timeout in `worker.py` (currently 30 seconds)

### Step 5: Test Individual Components

#### Test the analyzer only:

```python
from app.analyzer import analyze_image
from PIL import Image

# Create a test image
img = Image.new('RGB', (800, 600), color='white')
issues = analyze_image(img)
print(f"Found {len(issues)} issues")
```

#### Test the worker with verbose output:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'app'))

from worker import run_scan

try:
    result = run_scan("https://example.com")
    print("✅ Success!")
    print(f"Issues: {len(result['issues'])}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
```

### Step 6: Check Dependencies

Ensure all required packages are installed:

```bash
pip install -r requirements.txt
```

Required packages:

- `fastapi`
- `uvicorn`
- `playwright`
- `opencv-python`
- `numpy`
- `pillow`
- `pydantic`

### Step 7: Check File Paths

Make sure the data directory exists and is writable:

```bash
# Create necessary directories
mkdir -p data/screenshots
mkdir -p data/uploads

# Check permissions
ls -la data/
```

### Step 8: Environment-Specific Issues

#### Windows

- Run PowerShell as Administrator
- Check Windows Defender isn't blocking Playwright

#### Linux

- Install system dependencies: `playwright install-deps chromium`
- Check SELinux/AppArmor isn't blocking execution

#### Docker/Railway

- Ensure the Dockerfile includes Playwright installation
- Add to Dockerfile:
  ```dockerfile
  RUN playwright install --with-deps chromium
  ```

### Step 9: Check API Response

When creating a scan, check the detailed error:

```bash
# Create a scan
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Get scan status (replace SCAN_ID)
curl http://localhost:8000/api/v1/scans/SCAN_ID
```

Look at the `error` and `errorDetails` fields in the response.

### Step 10: Enable Debug Logging

Modify `worker.py` to add more logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Still Having Issues?

1. **Check the error message** - The enhanced error handling now provides detailed error messages
2. **Run setup_playwright.py** - Automated diagnostics and fixes
3. **Check server logs** - Look for stack traces and error details
4. **Test step by step** - Use the individual component tests above
5. **Check Railway logs** - If deployed, check the deployment logs

### Success Indicators

When everything works correctly:

```
✅ Playwright is installed
✅ Chromium browser is installed
✅ OpenCV is installed
✅ Test scan completed successfully
✅ Screenshot generated
✅ JSON report created
✅ HTML report created
```

### Quick Fix Checklist

- [ ] `pip install playwright`
- [ ] `playwright install chromium`
- [ ] `pip install opencv-python`
- [ ] Create `data/screenshots` directory
- [ ] Test with `python setup_playwright.py`
- [ ] Check server logs for specific errors
- [ ] Verify with simple test scan

---

**If problems persist after all these steps, check the error message in the scan result - it will now provide specific details about what went wrong.**
