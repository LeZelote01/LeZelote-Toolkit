@echo off
setlocal EnableDelayedExpansion

REM Pentest-USB Toolkit - Windows Launcher
REM Version: 1.0.0

echo ====================================
echo    Pentest-USB Toolkit Launcher
echo ====================================
echo.

REM Get current directory
set "TOOLKIT_ROOT=%~dp0"
set "PYTHON_PATH=%TOOLKIT_ROOT%runtime\python\windows"
set "TOOLS_PATH=%TOOLKIT_ROOT%tools\binaries\windows"

REM Check if portable Python exists
if not exist "%PYTHON_PATH%\python.exe" (
    echo [ERROR] Portable Python not found!
    echo Please run setup.ps1 first to initialize the toolkit.
    pause
    exit /b 1
)

REM Add tools to PATH
set "PATH=%TOOLS_PATH%;%PATH%"

REM Set Python path
set "PYTHONPATH=%TOOLKIT_ROOT%"

REM Change to toolkit directory
cd /d "%TOOLKIT_ROOT%"

REM Launch the main CLI interface
echo [INFO] Starting Pentest-USB Toolkit...
"%PYTHON_PATH%\python.exe" interfaces\cli\main_cli.py

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start toolkit!
    pause
)