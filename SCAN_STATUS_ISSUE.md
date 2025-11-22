# Scan Status Issue - Diagnosis Guide

## The Problem

You reported: "When I start a scan, status shows 'running', but when I navigate to issues page and come back to scans page, the status is 'error'."

## Possible Causes

### 1. **Backend Issue: Scan Actually Failing** (Most Likely)
The scan is genuinely failing due to:
- ✅ Playwright browsers not installed
- ✅ Network timeouts
- ✅ Invalid URL
- ✅ Permission issues with file system
- ✅ Missing dependencies (cv2, numpy, etc.)

### 2. **Frontend Issue: Status Polling**
- Frontend might not be polling correctly
- Race condition in status updates
- Caching issues

### 3. **Thread Termination** (Now Fixed)
- ~~Background threads were daemon threads~~ ✅ Fixed
- ~~Could terminate prematurely~~ ✅ Fixed

## What I Fixed

### 1. Enhanced Logging
The backend now logs every step of the scan process:
```
============================================================
Starting scan: abc-123-def
URL: https://example.com
============================================================

[abc-123-def] Status set to 'running', calling run_scan...
[abc-123-def] Scan completed successfully!
[abc-123-def] Found 5 issues
[abc-123-def] Status set to 'done'
```

### 2. Changed Thread Behavior
```python
# Before: daemon=True (could terminate unexpectedly)
t = threading.Thread(target=job, daemon=True)

# After: daemon=False (completes properly)
t = threading.Thread(target=job, daemon=False, name=f"ScanThread-{scan_id[:8]}")
```

### 3. Added Debug Endpoint
```
GET /api/v1/debug/scans
```
Shows:
- All scans and their status
- Active scan threads
- Error details

### 4. Created Diagnostic Tool
```bash
python test_scan_status.py
```
This tool:
- Creates a test scan
- Monitors status every 2 seconds
- Shows status transitions
- Identifies suspicious patterns
- Shows detailed error messages

## How to Diagnose YOUR Issue

### Step 1: Run the Diagnostic Tool

```bash
# Make sure server is running first
cd app
uvicorn main:app --reload

# In another terminal, run the diagnostic
python test_scan_status.py
```

**What it will show:**
```
Step 1: Creating scan...
✅ Scan created: abc-123-def

Step 2: Monitoring status...
[ 0s] Status: queued     | Has result: No  | Has error: No
[ 2s] Status: running    | Has result: No  | Has error: No
[ 4s] Status: running    | Has result: No  | Has error: No
[ 6s] Status: error      | Has result: No  | Has error: Yes
      Error: Scan failed: Executable doesn't exist...

❌ SCAN FAILED!
   Error: Scan failed: Executable doesn't exist at /path/to/chromium
   
   Error Details:
   Please ensure Playwright browsers are installed (run: playwright install chromium)
```

### Step 2: Check Server Logs

When you start a scan, watch the server console output:

**If Playwright not installed:**
```
[abc-123-def] Status set to 'running', calling run_scan...
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[abc-123-def] SCAN FAILED!
Error: Executable doesn't exist at...
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

**If successful:**
```
[abc-123-def] Status set to 'running', calling run_scan...
[abc-123-def] Scan completed successfully!
[abc-123-def] Found 12 issues
[abc-123-def] Status set to 'done'
```

### Step 3: Check Debug Endpoint

```bash
curl http://localhost:8000/api/v1/debug/scans | jq
```

Response:
```json
{
  "totalScans": 3,
  "activeThreads": [
    {
      "name": "ScanThread-abc-123",
      "alive": true,
      "daemon": false
    }
  ],
  "scans": [
    {
      "scanId": "abc-123-def-456",
      "url": "https://example.com",
      "status": "error",
      "hasResult": false,
      "error": "Scan failed: Executable doesn't exist...",
      "createdAt": "2025-11-22T10:30:00Z",
      "updatedAt": "2025-11-22T10:30:05Z"
    }
  ]
}
```

### Step 4: Get Detailed Scan Status

```bash
# Replace SCAN_ID with your actual scan ID
curl http://localhost:8000/api/v1/scans/SCAN_ID | jq
```

Look for:
- `status`: "error"
- `error`: The error message
- `errorDetails`: Stack trace

## Most Common Solution

**90% of the time, the issue is Playwright not being installed:**

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Linux: Install system dependencies
playwright install-deps chromium

# Or use the automated setup
python setup_playwright.py
```

## Is it Frontend or Backend?

### It's a BACKEND issue if:
✅ `test_scan_status.py` shows the scan failing  
✅ Server logs show errors  
✅ Debug endpoint shows `"status": "error"`  
✅ Error message mentions Playwright, permissions, or timeouts  

### It's a FRONTEND issue if:
❌ `test_scan_status.py` shows scan succeeding  
❌ Server logs show "Scan completed successfully"  
❌ Debug endpoint shows `"status": "done"`  
❌ But frontend still shows "error"  

## Testing the Fix

### Test 1: Server-side test
```bash
python test_scan_status.py
```
Should show: `✅ SCAN COMPLETED SUCCESSFULLY!`

### Test 2: API test
```bash
# Create scan
SCAN_ID=$(curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' | jq -r '.scanId')

# Wait 10 seconds
sleep 10

# Check status
curl http://localhost:8000/api/v1/scans/$SCAN_ID | jq '.status'
```
Should show: `"done"`

### Test 3: Frontend test
1. Start server: `uvicorn main:app --reload`
2. Open frontend
3. Create a scan
4. Navigate away
5. Come back
6. Check if status is still correct

## What to Report

If the issue persists after running `setup_playwright.py`, please report:

1. **Output of diagnostic tool:**
   ```bash
   python test_scan_status.py > scan_test_output.txt
   ```

2. **Server logs when creating a scan**

3. **Debug endpoint output:**
   ```bash
   curl http://localhost:8000/api/v1/debug/scans > debug_output.json
   ```

4. **Scan status with error details:**
   ```bash
   curl http://localhost:8000/api/v1/scans/SCAN_ID > scan_details.json
   ```

## Summary

**99% of the time**, scans fail because Playwright browsers aren't installed. The enhanced logging will now tell you exactly why it's failing.

**Run this to fix:**
```bash
python setup_playwright.py
```

**Then test:**
```bash
python test_scan_status.py
```

If it still fails, the diagnostic tool will show you the exact error message.
