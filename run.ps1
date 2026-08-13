$ErrorActionPreference = "Stop"

Write-Host "Checking for Python virtual environment..."
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

Write-Host "Installing/Updating requirements..."
.\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "Running bot.py..."
.\venv\Scripts\python.exe bot.py
