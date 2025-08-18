@echo off
REM =============================================================================
REM LeZelote Toolkit - Launcher Script for Windows
REM Version: 1.0.0  
REM Compatible: Windows 10/11, Windows Server 2019+
REM =============================================================================

setlocal enabledelayedexpansion

REM Toolkit information
set TOOLKIT_NAME=LeZelote Toolkit
set VERSION=1.0.0
set AUTHOR=LeZelote Team

REM Paths
set SCRIPT_DIR=%~dp0
set PYTHON_CMD=
set VENV_PATH=%SCRIPT_DIR%venv

REM Colors (Windows CMD doesn't support colors directly, but we'll use echo formatting)
set "RED=[31m"
set "GREEN=[32m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "PURPLE=[35m"
set "CYAN=[36m"
set "WHITE=[37m"
set "NC=[0m"

REM =============================================================================
REM Functions (using labels and goto for Windows batch)
REM =============================================================================

:print_banner
cls
echo.
echo  ╔══════════════════════════════════════════════════════════════════════════════╗
echo  ║                                                                              ║
echo  ║    ██╗     ███████╗███████╗███████╗██╗      ██████╗ ████████╗███████╗       ║
echo  ║    ██║     ██╔════╝╚══███╔╝██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔════╝       ║
echo  ║    ██║     █████╗    ███╔╝ █████╗  ██║     ██║   ██║   ██║   █████╗         ║
echo  ║    ██║     ██╔══╝   ███╔╝  ██╔══╝  ██║     ██║   ██║   ██║   ██╔══╝         ║
echo  ║    ███████╗███████╗███████╗███████╗███████╗╚██████╔╝   ██║   ███████╗       ║
echo  ║    ╚══════╝╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚══════╝       ║
echo  ║                                                                              ║
echo  ║                            PENTEST USB TOOLKIT                              ║
echo  ║                                Version %VERSION%                                ║
echo  ║                                                                              ║
echo  ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
goto :eof

:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

:check_system
call :print_status "Checking system compatibility..."

REM Detect Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
call :print_status "Windows Version: %VERSION%"

REM Check architecture
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set ARCH=x64
) else if "%PROCESSOR_ARCHITECTURE%"=="x86" (
    set ARCH=x86
) else (
    set ARCH=%PROCESSOR_ARCHITECTURE%
)
call :print_status "Architecture: %ARCH%"

REM Check available memory (approximate)
for /f "skip=1" %%p in ('wmic computersystem get TotalPhysicalMemory') do (
    set /a MEMORY_GB=%%p/1024/1024/1024
    call :print_status "Available RAM: !MEMORY_GB!GB"
    if !MEMORY_GB! lss 4 (
        call :print_warning "Low memory detected. Minimum 4GB recommended."
    )
    goto :memory_checked
)
:memory_checked

REM Check disk space
for /f "tokens=3" %%a in ('dir /-c "%SCRIPT_DIR%" ^| findstr /i bytes') do set DISK_SPACE=%%a
call :print_status "Available disk space: %DISK_SPACE% bytes"

goto :eof

:find_python
call :print_status "Looking for Python installation..."

REM Try different Python commands
for %%p in (python3.11 python3.10 python3.9 python3 python py) do (
    %%p --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%v in ('%%p --version 2^>^&1') do (
            set PYTHON_VERSION=%%v
            REM Check if version is 3.9+
            for /f "tokens=1,2 delims=." %%x in ("!PYTHON_VERSION!") do (
                if %%x geq 3 (
                    if %%y geq 9 (
                        set PYTHON_CMD=%%p
                        call :print_success "Found Python: %%p (!PYTHON_VERSION!)"
                        goto :python_found
                    )
                )
            )
        )
    )
)

call :print_error "Python 3.9+ not found. Please install Python 3.9 or higher."
set PYTHON_FOUND=0
goto :eof

:python_found
set PYTHON_FOUND=1
goto :eof

:check_dependencies
call :print_status "Checking Python dependencies..."

if not exist "%SCRIPT_DIR%requirements.txt" (
    call :print_error "requirements.txt not found!"
    set DEPS_OK=0
    goto :eof
)

REM Check if virtual environment exists
if exist "%VENV_PATH%" (
    call :print_status "Virtual environment found"
    call "%VENV_PATH%\Scripts\activate.bat"
    
    REM Check if dependencies are installed
    %PYTHON_CMD% -c "import requests, nmap, yaml" >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "Dependencies are installed"
        set DEPS_OK=1
        goto :eof
    ) else (
        call :print_warning "Some dependencies missing, installing..."
    )
) else (
    call :print_status "Creating virtual environment..."
    %PYTHON_CMD% -m venv "%VENV_PATH%"
    call "%VENV_PATH%\Scripts\activate.bat"
)

REM Install/upgrade dependencies
pip install --upgrade pip >nul 2>&1
pip install -r "%SCRIPT_DIR%requirements.txt" >nul 2>&1
if !errorlevel! equ 0 (
    call :print_success "Dependencies installed successfully"
    set DEPS_OK=1
) else (
    call :print_error "Failed to install dependencies"
    set DEPS_OK=0
)

goto :eof

:check_tools
call :print_status "Checking external tools availability..."

REM List of tools to check
set TOOLS=nmap sqlmap dirb nikto hydra john hashcat

for %%t in (%TOOLS%) do (
    where %%t >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "%%t: Available"
    ) else (
        call :print_warning "%%t: Not found in PATH"
    )
)

REM Check for integrated binaries
set BINARY_PATH=%SCRIPT_DIR%tools\binaries\windows
if exist "%BINARY_PATH%" (
    dir /b "%BINARY_PATH%\*.exe" 2>nul | find /c /v "" > temp_count.txt
    set /p BINARY_COUNT=<temp_count.txt
    del temp_count.txt
    call :print_status "Found !BINARY_COUNT! integrated Windows binaries"
)

goto :eof

:run_system_check
call :print_status "Running comprehensive system check..."

if exist "%SCRIPT_DIR%scripts\maintenance\system_check.py" (
    %PYTHON_CMD% "%SCRIPT_DIR%scripts\maintenance\system_check.py" --component resources
) else (
    call :print_warning "System check script not found, skipping detailed analysis"
)

goto :eof

:launch_toolkit
call :print_status "Launching LeZelote Toolkit..."

REM Ensure we're in the toolkit directory
cd /d "%SCRIPT_DIR%"

REM Activate virtual environment if it exists
if exist "%VENV_PATH%" (
    call "%VENV_PATH%\Scripts\activate.bat"
)

REM Check if CLI script exists
if exist "%SCRIPT_DIR%run_cli.py" (
    call :print_success "Starting CLI interface..."
    echo.
    %PYTHON_CMD% "%SCRIPT_DIR%run_cli.py"
) else (
    call :print_error "CLI script (run_cli.py) not found!"
    pause
    exit /b 1
)

goto :eof

:launch_web_interface
call :print_status "Launching web interface..."

cd /d "%SCRIPT_DIR%"

if exist "%VENV_PATH%" (
    call "%VENV_PATH%\Scripts\activate.bat"
)

if exist "%SCRIPT_DIR%interfaces\web\app.py" (
    call :print_success "Starting web interface on http://localhost:8080"
    %PYTHON_CMD% "%SCRIPT_DIR%interfaces\web\app.py"
) else (
    call :print_error "Web interface not found!"
    pause
    exit /b 1
)

goto :eof

:show_help
echo LeZelote Toolkit Launcher
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   -h, --help              Show this help message
echo   -v, --version           Show version information
echo   -c, --check-only        Run system checks only (don't launch)
echo   -s, --skip-checks       Skip system checks and launch directly
echo   -w, --web               Launch web interface instead of CLI
echo   --install-deps          Install/update dependencies only
echo   --reset-venv            Reset virtual environment
echo.
echo Examples:
echo   %~nx0                   Launch toolkit with system checks
echo   %~nx0 -s                Launch toolkit without checks
echo   %~nx0 -w                Launch web interface
echo   %~nx0 --install-deps    Install dependencies only
echo.
goto :eof

:show_version
echo %TOOLKIT_NAME%
echo Version: %VERSION%
echo Author: %AUTHOR%  
echo Platform: Windows (%ARCH%)
echo.
goto :eof

:install_dependencies_only
call :print_status "Installing dependencies only..."

call :find_python
if !PYTHON_FOUND! neq 1 (
    pause
    exit /b 1
)

call :check_dependencies
if !DEPS_OK! equ 1 (
    call :print_success "Dependencies installation completed"
) else (
    call :print_error "Failed to install dependencies"
    pause
    exit /b 1
)
goto :eof

:reset_venv
call :print_status "Resetting virtual environment..."

if exist "%VENV_PATH%" (
    rmdir /s /q "%VENV_PATH%"
    call :print_success "Virtual environment removed"
)

call :find_python
if !PYTHON_FOUND! neq 1 (
    pause
    exit /b 1
)

call :check_dependencies
if !DEPS_OK! equ 1 (
    call :print_success "Virtual environment recreated"
) else (
    call :print_error "Failed to recreate virtual environment"
    pause
    exit /b 1
)
goto :eof

REM =============================================================================
REM Main execution
REM =============================================================================

REM Parse command line arguments
set SKIP_CHECKS=false
set CHECK_ONLY=false
set WEB_MODE=false

:parse_args
if "%~1"=="" goto args_parsed
if "%~1"=="-h" goto show_help_exit
if "%~1"=="--help" goto show_help_exit
if "%~1"=="-v" goto show_version_exit
if "%~1"=="--version" goto show_version_exit
if "%~1"=="-c" set CHECK_ONLY=true& shift& goto parse_args
if "%~1"=="--check-only" set CHECK_ONLY=true& shift& goto parse_args
if "%~1"=="-s" set SKIP_CHECKS=true& shift& goto parse_args
if "%~1"=="--skip-checks" set SKIP_CHECKS=true& shift& goto parse_args
if "%~1"=="-w" set WEB_MODE=true& shift& goto parse_args
if "%~1"=="--web" set WEB_MODE=true& shift& goto parse_args
if "%~1"=="--install-deps" goto install_deps_exit
if "%~1"=="--reset-venv" goto reset_venv_exit

call :print_error "Unknown option: %~1"
echo Use -h or --help for usage information
pause
exit /b 1

:show_help_exit
call :show_help
pause
exit /b 0

:show_version_exit
call :show_version
pause
exit /b 0

:install_deps_exit
call :print_banner
call :install_dependencies_only
pause
exit /b 0

:reset_venv_exit
call :print_banner
call :reset_venv
pause
exit /b 0

:args_parsed

REM Main workflow
call :print_banner

if "%SKIP_CHECKS%"=="false" (
    call :check_system
    
    call :find_python
    if !PYTHON_FOUND! neq 1 (
        pause
        exit /b 1
    )
    
    call :check_dependencies
    if !DEPS_OK! neq 1 (
        pause
        exit /b 1
    )
    
    call :check_tools
    call :run_system_check
    
    call :print_success "System checks completed successfully!"
    echo.
)

if "%CHECK_ONLY%"=="true" (
    call :print_success "System check completed. Exiting."
    pause
    exit /b 0
)

REM Launch appropriate interface
if "%WEB_MODE%"=="true" (
    call :launch_web_interface
) else (
    call :launch_toolkit
)

pause