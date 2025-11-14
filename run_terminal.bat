@echo off
REM Terminal Chat Bot Launcher for Windows
REM Usage: run_terminal.bat [user_id]

echo ========================================
echo   Terminal Chat Bot Launcher
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please run this script from the ai/ directory
    pause
    exit /b 1
)

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv not found. Installing uv...
    echo.
    
    REM Try to install uv using pip if Python is available
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python first, or install uv manually from: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
    
    python -m pip install uv
    if errorlevel 1 (
        echo ERROR: Failed to install uv
        pause
        exit /b 1
    )
    echo uv installed successfully!
    echo.
)

REM Check if .venv exists, if not create it with Python 3.13
if not exist ".venv" (
    echo Virtual environment not found. Setting up...
    echo.
    
    echo Installing Python 3.13 and creating virtual environment with uv...
    uv venv .venv --python 3.13
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo uv will automatically download Python 3.13 if needed
        pause
        exit /b 1
    )
    
    echo Virtual environment created successfully with Python 3.13!
    echo.
)

REM Install/update requirements if requirements.txt exists
if exist "requirements.txt" (
    echo Checking dependencies...
    uv pip install -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Some dependencies may not have installed correctly
    )
    echo.
)

REM Show interface selection menu
echo Select Interface:
echo ========================================
echo 1. Terminal Mode (Simple, Fast)
echo 2. TUI Mode (Modern, Beautiful)
echo 3. Exit
echo ========================================
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto terminal_mode
if "%choice%"=="2" goto tui_mode
if "%choice%"=="3" goto end
echo Invalid choice. Defaulting to Terminal Mode...
goto terminal_mode

:terminal_mode
echo.
echo Starting Terminal Chat Bot (Terminal Mode)...
echo.
if "%1"=="" (
    .venv\Scripts\python.exe main.py chat
) else (
    .venv\Scripts\python.exe main.py chat --user %1
)
goto end

:tui_mode
echo.
echo Starting Terminal Chat Bot (TUI Mode)...
echo.
if "%1"=="" (
    .venv\Scripts\python.exe main.py chat --tui
) else (
    .venv\Scripts\python.exe main.py chat --user %1 --tui
)
goto end

:end
echo.
echo Bot has exited.
pause
