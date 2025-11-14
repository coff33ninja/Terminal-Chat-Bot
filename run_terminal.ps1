# Terminal Chat Bot Launcher for PowerShell
# Usage: .\run_terminal.ps1 [user_id]

param(
    [string]$UserId = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Terminal Chat Bot Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "✗ ERROR: main.py not found" -ForegroundColor Red
    Write-Host "Please run this script from the ai/ directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if uv is installed
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✓ uv found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Yellow
    Write-Host ""
    
    # Try to install uv using pip if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
        
        python -m pip install uv
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ ERROR: Failed to install uv" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✓ uv installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python first, or install uv manually from: https://docs.astral.sh/uv/" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
}

# Check if .venv exists, if not create it with Python 3.13
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Setting up..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Installing Python 3.13 and creating virtual environment with uv..." -ForegroundColor Yellow
    uv venv .venv --python 3.13
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ ERROR: Failed to create virtual environment" -ForegroundColor Red
        Write-Host "uv will automatically download Python 3.13 if needed" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "✓ Virtual environment created successfully with Python 3.13!" -ForegroundColor Green
    Write-Host ""
}

# Install/update requirements if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host "Checking dependencies..." -ForegroundColor Cyan
    uv pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ WARNING: Some dependencies may not have installed correctly" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Dependencies installed" -ForegroundColor Green
    }
    Write-Host ""
}

# Show interface selection menu
Write-Host ""
Write-Host "Select Interface:" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Terminal Mode (Simple, Fast)" -ForegroundColor White
Write-Host "2. TUI Mode (Modern, Beautiful)" -ForegroundColor White
Write-Host "3. Exit" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Terminal Chat Bot (Terminal Mode)..." -ForegroundColor Green
        Write-Host ""
        
        if ($UserId -eq "") {
            & .venv\Scripts\python.exe main.py chat
        } else {
            & .venv\Scripts\python.exe main.py chat --user $UserId
        }
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Terminal Chat Bot (TUI Mode)..." -ForegroundColor Green
        Write-Host ""
        
        if ($UserId -eq "") {
            & .venv\Scripts\python.exe main.py chat --tui
        } else {
            & .venv\Scripts\python.exe main.py chat --user $UserId --tui
        }
    }
    "3" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Invalid choice. Defaulting to Terminal Mode..." -ForegroundColor Yellow
        Write-Host ""
        
        if ($UserId -eq "") {
            & .venv\Scripts\python.exe main.py chat
        } else {
            & .venv\Scripts\python.exe main.py chat --user $UserId
        }
    }
}

Write-Host ""
Write-Host "Bot has exited." -ForegroundColor Cyan
Read-Host "Press Enter to exit"
