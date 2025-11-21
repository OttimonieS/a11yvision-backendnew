Param(
    [switch]$Global
)

Write-Host "[setup] Checking for Python..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Install with: winget install Python.Python.3.11" -ForegroundColor Yellow
    exit 1
}

Write-Host "[setup] Upgrading pip..."
python -m pip install --upgrade pip

Write-Host "[setup] Installing dev formatters (black, isort)..."
if ($Global) {
    python -m pip install black isort
}
else {
    python -m pip install --user black isort
}

Write-Host "[setup] Formatter installation complete. Restart VS Code if Alt+Shift+F does not trigger Black." -ForegroundColor Green
