# =============================================================================
# LeZelote-Toolkit - Setup Script for Windows PowerShell
# =============================================================================
# Description: Comprehensive installation script for Windows systems
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# Requirements: PowerShell 5.1+ or PowerShell Core 6+
# =============================================================================

#Requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$SkipSystemDeps,
    [switch]$SkipDocker,
    [switch]$Verbose,
    [switch]$Help
)

# Set error action
$ErrorActionPreference = "Stop"

# =============================================================================
# Configuration and Variables
# =============================================================================

$Script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Script:LogFile = Join-Path $ProjectRoot "logs" "installation.log"
$Script:ConfigDir = Join-Path $ProjectRoot "config"

# Colors for console output
$Script:Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    White = "White"
}

# =============================================================================
# Utility Functions
# =============================================================================

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level,
        
        [Parameter(Mandatory = $true)]
        [string]$Message
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Ensure log directory exists
    $logDir = Split-Path $Script:LogFile -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # Write to log file
    Add-Content -Path $Script:LogFile -Value $logEntry -Encoding UTF8
    
    # Write to console with colors
    switch ($Level) {
        "INFO" { Write-Host "[INFO] $Message" -ForegroundColor $Script:Colors.Blue }
        "WARN" { Write-Host "[WARN] $Message" -ForegroundColor $Script:Colors.Yellow }
        "ERROR" { Write-Host "[ERROR] $Message" -ForegroundColor $Script:Colors.Red }
        "SUCCESS" { Write-Host "[SUCCESS] $Message" -ForegroundColor $Script:Colors.Green }
    }
}

function Show-Banner {
    $banner = @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                       LeZelote-Toolkit Setup Script                          ║
║                            Windows Installation                              ║
║                                Version 1.0.0                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"@
    Write-Host $banner -ForegroundColor $Script:Colors.Cyan
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal] $currentUser
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-SystemRequirements {
    Write-Log "INFO" "Checking system requirements..."
    
    # Get system information
    $os = Get-WmiObject -Class Win32_OperatingSystem
    $computer = Get-WmiObject -Class Win32_ComputerSystem
    $processor = Get-WmiObject -Class Win32_Processor | Select-Object -First 1
    
    $totalMemoryGB = [math]::Round($computer.TotalPhysicalMemory / 1GB, 2)
    $freeSpaceGB = [math]::Round((Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 } | Measure-Object -Property FreeSpace -Sum).Sum / 1GB, 2)
    $cpuCores = $processor.NumberOfCores
    
    Write-Log "INFO" "System Information:"
    Write-Log "INFO" "  - OS: $($os.Caption) ($($os.Version))"
    Write-Log "INFO" "  - Architecture: $($os.OSArchitecture)"
    Write-Log "INFO" "  - CPU: $($processor.Name)"
    Write-Log "INFO" "  - CPU Cores: $cpuCores"
    Write-Log "INFO" "  - Total Memory: ${totalMemoryGB}GB"
    Write-Log "INFO" "  - Free Disk Space: ${freeSpaceGB}GB"
    
    # Check requirements
    $errors = 0
    
    # Check Windows version (Windows 10 or later)
    $minVersion = [Version]"10.0.0.0"
    $currentVersion = [Version]$os.Version
    if ($currentVersion -lt $minVersion) {
        Write-Log "ERROR" "Windows 10 or later is required (found: $($os.Caption))"
        $errors++
    }
    
    # Check CPU cores
    if ($cpuCores -lt 2) {
        Write-Log "WARN" "Minimum 2 CPU cores recommended (found: $cpuCores)"
    }
    
    # Check memory
    if ($totalMemoryGB -lt 8) {
        Write-Log "ERROR" "Minimum 8GB RAM required (found: ${totalMemoryGB}GB)"
        $errors++
    }
    
    # Check disk space
    if ($freeSpaceGB -lt 32) {
        Write-Log "ERROR" "Minimum 32GB free disk space required (found: ${freeSpaceGB}GB)"
        $errors++
    }
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        Write-Log "ERROR" "PowerShell 5.1 or later is required (found: $($psVersion.ToString()))"
        $errors++
    }
    
    if ($errors -gt 0) {
        Write-Log "ERROR" "System requirements not met. Please upgrade your system."
        throw "System requirements check failed"
    }
    
    Write-Log "SUCCESS" "System requirements check passed"
}

function Install-Chocolatey {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Log "INFO" "Chocolatey is already installed"
        return
    }
    
    Write-Log "INFO" "Installing Chocolatey package manager..."
    
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Log "SUCCESS" "Chocolatey installed successfully"
    }
    catch {
        Write-Log "ERROR" "Failed to install Chocolatey: $($_.Exception.Message)"
        throw
    }
    
    # Refresh environment variables
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

function Install-SystemDependencies {
    Write-Log "INFO" "Installing system dependencies..."
    
    # Install Chocolatey first
    Install-Chocolatey
    
    # List of packages to install
    $packages = @(
        "python3",
        "git",
        "curl",
        "wget",
        "7zip",
        "nmap",
        "docker-desktop",
        "wireshark",
        "putty",
        "vscode"  # Optional but useful
    )
    
    foreach ($package in $packages) {
        try {
            Write-Log "INFO" "Installing $package..."
            & choco install $package -y --no-progress
            Write-Log "SUCCESS" "$package installed successfully"
        }
        catch {
            Write-Log "WARN" "Failed to install $package`: $($_.Exception.Message)"
        }
    }
    
    # Install additional security tools via Chocolatey
    $securityTools = @(
        "hashcat",
        "john-the-ripper",
        "sqlmap"
    )
    
    foreach ($tool in $securityTools) {
        try {
            Write-Log "INFO" "Installing security tool: $tool..."
            & choco install $tool -y --no-progress --ignore-checksums
            Write-Log "SUCCESS" "$tool installed successfully"
        }
        catch {
            Write-Log "WARN" "Failed to install $tool`: $($_.Exception.Message)"
        }
    }
    
    Write-Log "SUCCESS" "System dependencies installation completed"
    
    # Refresh environment variables
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

function Setup-PythonEnvironment {
    Write-Log "INFO" "Setting up Python environment..."
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "INFO" "Found Python: $pythonVersion"
    }
    catch {
        Write-Log "ERROR" "Python not found. Please install Python 3.8+ first."
        throw "Python installation required"
    }
    
    # Create virtual environment
    $venvPath = Join-Path $Script:ProjectRoot ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Log "INFO" "Creating Python virtual environment..."
        python -m venv $venvPath
        Write-Log "INFO" "Python virtual environment created"
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $venvPath "Scripts" "Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        Write-Log "INFO" "Virtual environment activated"
    }
    else {
        Write-Log "ERROR" "Failed to find virtual environment activation script"
        throw "Virtual environment setup failed"
    }
    
    # Upgrade pip
    Write-Log "INFO" "Upgrading pip..."
    python -m pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    $requirementsFile = Join-Path $Script:ProjectRoot "requirements.txt"
    if (Test-Path $requirementsFile) {
        Write-Log "INFO" "Installing Python dependencies..."
        pip install -r $requirementsFile
        Write-Log "SUCCESS" "Python dependencies installed successfully"
    }
    else {
        Write-Log "ERROR" "requirements.txt not found"
        throw "Requirements file missing"
    }
}

function Setup-DockerEnvironment {
    Write-Log "INFO" "Setting up Docker environment..."
    
    # Check if Docker is installed
    try {
        $dockerVersion = docker --version 2>&1
        Write-Log "INFO" "Found Docker: $dockerVersion"
    }
    catch {
        Write-Log "WARN" "Docker not found. Please install Docker Desktop manually."
        Write-Log "INFO" "Download from: https://www.docker.com/products/docker-desktop"
        return
    }
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Log "SUCCESS" "Docker is running"
    }
    catch {
        Write-Log "WARN" "Docker is not running. Please start Docker Desktop."
        Write-Log "INFO" "Starting Docker Desktop..."
        
        # Try to start Docker Desktop
        $dockerDesktopPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerDesktopPath) {
            Start-Process $dockerDesktopPath
            Write-Log "INFO" "Docker Desktop started. Waiting for Docker daemon..."
            
            # Wait for Docker to start (up to 60 seconds)
            $timeout = 60
            $elapsed = 0
            while ($elapsed -lt $timeout) {
                try {
                    docker info | Out-Null
                    Write-Log "SUCCESS" "Docker daemon is now running"
                    break
                }
                catch {
                    Start-Sleep -Seconds 2
                    $elapsed += 2
                }
            }
            
            if ($elapsed -ge $timeout) {
                Write-Log "ERROR" "Docker failed to start within $timeout seconds"
                throw "Docker startup timeout"
            }
        }
        else {
            Write-Log "ERROR" "Docker Desktop not found at expected location"
            throw "Docker Desktop not installed"
        }
    }
    
    # Test Docker with hello-world
    try {
        docker run --rm hello-world | Out-Null
        Write-Log "SUCCESS" "Docker setup completed successfully"
    }
    catch {
        Write-Log "ERROR" "Docker test failed: $($_.Exception.Message)"
        throw "Docker test failed"
    }
}

function New-DirectoryStructure {
    Write-Log "INFO" "Creating directory structure..."
    
    $directories = @(
        (Join-Path $Script:ProjectRoot "logs"),
        (Join-Path $Script:ProjectRoot "outputs" "scans"),
        (Join-Path $Script:ProjectRoot "outputs" "reports"),
        (Join-Path $Script:ProjectRoot "outputs" "temporary"),
        (Join-Path $Script:ProjectRoot "data" "loot"),
        (Join-Path $Script:ProjectRoot "tools" "binaries"),
        (Join-Path $env:USERPROFILE ".lezelote")
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "INFO" "Created directory: $dir"
        }
    }
    
    Write-Log "SUCCESS" "Directory structure created successfully"
}

function Set-FilePermissions {
    Write-Log "INFO" "Configuring file permissions..."
    
    # Make scripts executable (PowerShell scripts are executable by default)
    $scriptFiles = Get-ChildItem -Path (Join-Path $Script:ProjectRoot "scripts") -Recurse -Include "*.ps1", "*.py", "*.bat"
    
    foreach ($file in $scriptFiles) {
        try {
            # Remove read-only attribute if present
            $file.Attributes = $file.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly)
            Write-Log "INFO" "Updated permissions for: $($file.Name)"
        }
        catch {
            Write-Log "WARN" "Failed to update permissions for: $($file.Name)"
        }
    }
    
    Write-Log "SUCCESS" "File permissions configured successfully"
}

function Setup-Configuration {
    Write-Log "INFO" "Setting up configuration files..."
    
    $userConfigDir = Join-Path $env:USERPROFILE ".lezelote"
    $userConfigFile = Join-Path $userConfigDir "config.yaml"
    
    if (-not (Test-Path $userConfigFile)) {
        $configContent = @"
# LeZelote-Toolkit User Configuration
user:
  name: ""
  email: ""
  organization: ""

paths:
  project_root: "$($Script:ProjectRoot -replace '\\', '\\')"
  output_directory: ""
  tools_directory: ""

preferences:
  default_scan_profile: "default"
  auto_update: true
  stealth_mode: false
  verbose_logging: false

interface:
  theme: "dark"
  show_banner: true
  confirmation_prompts: true
"@
        
        Set-Content -Path $userConfigFile -Value $configContent -Encoding UTF8
        Write-Log "INFO" "User configuration file created: $userConfigFile"
    }
    
    Write-Log "SUCCESS" "Configuration setup completed"
}

function Register-PowerShellAlias {
    Write-Log "INFO" "Registering PowerShell aliases..."
    
    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileDir = Split-Path $profilePath -Parent
    
    # Create profile directory if it doesn't exist
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    
    # Create profile file if it doesn't exist
    if (-not (Test-Path $profilePath)) {
        New-Item -ItemType File -Path $profilePath -Force | Out-Null
    }
    
    $aliasContent = @"

# LeZelote-Toolkit aliases
function Start-LeZelote {
    Set-Location '$Script:ProjectRoot'
    & '.\launch.bat'
}
Set-Alias -Name lezelote -Value Start-LeZelote
`$env:LEZELOTE_HOME = '$Script:ProjectRoot'
"@
    
    $currentContent = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
    if (-not ($currentContent -like "*LeZelote-Toolkit aliases*")) {
        Add-Content -Path $profilePath -Value $aliasContent -Encoding UTF8
        Write-Log "INFO" "Aliases added to PowerShell profile: $profilePath"
        Write-Log "INFO" "Restart PowerShell or run '. `$PROFILE' to use 'lezelote' command"
    }
    
    Write-Log "SUCCESS" "PowerShell aliases registered successfully"
}

function Invoke-Verification {
    Write-Log "INFO" "Running installation verification..."
    
    $verificationScript = Join-Path $PSScriptRoot "verify_installation.py"
    if (Test-Path $verificationScript) {
        try {
            python $verificationScript
        }
        catch {
            Write-Log "WARN" "Verification script failed: $($_.Exception.Message)"
        }
    }
    else {
        Write-Log "WARN" "Verification script not found. Skipping verification."
    }
}

# =============================================================================
# Main Installation Function
# =============================================================================

function Start-Installation {
    Show-Banner
    
    Write-Log "INFO" "Starting LeZelote-Toolkit installation..."
    Write-Log "INFO" "Installation directory: $Script:ProjectRoot"
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Log "WARN" "Not running as Administrator. Some features may not work properly."
        $response = Read-Host "Continue anyway? (y/N)"
        if ($response -notmatch '^[Yy]$') {
            Write-Log "INFO" "Installation aborted by user"
            return
        }
    }
    
    # Test system requirements
    Test-SystemRequirements
    
    # Create directory structure
    New-DirectoryStructure
    
    # Install system dependencies
    if (-not $SkipSystemDeps) {
        Install-SystemDependencies
    }
    else {
        Write-Log "WARN" "Skipping system dependencies installation"
    }
    
    # Setup Python environment
    Setup-PythonEnvironment
    
    # Setup Docker
    if (-not $SkipDocker) {
        try {
            Setup-DockerEnvironment
        }
        catch {
            Write-Log "WARN" "Docker setup failed: $($_.Exception.Message)"
            Write-Log "WARN" "Continuing installation without Docker"
        }
    }
    else {
        Write-Log "WARN" "Skipping Docker setup"
    }
    
    # Configure permissions
    Set-FilePermissions
    
    # Setup configuration
    Setup-Configuration
    
    # Register PowerShell aliases
    Register-PowerShellAlias
    
    # Run verification
    Invoke-Verification
    
    Write-Log "SUCCESS" "LeZelote-Toolkit installation completed successfully!"
    
    # Show completion message
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                          Installation Complete!                             ║" -ForegroundColor Green
    Write-Host "╠══════════════════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║ To start using LeZelote-Toolkit:                                            ║" -ForegroundColor Green
    Write-Host "║                                                                              ║" -ForegroundColor Green
    Write-Host "║ 1. Restart PowerShell or run: . `$PROFILE                                    ║" -ForegroundColor Green
    Write-Host "║ 2. Use command: lezelote                                                    ║" -ForegroundColor Green
    Write-Host "║ 3. Or navigate to: $Script:ProjectRoot" -ForegroundColor Green
    Write-Host "║    and run: .\launch.bat                                                    ║" -ForegroundColor Green
    Write-Host "║                                                                              ║" -ForegroundColor Green
    Write-Host "║ Configuration file: $env:USERPROFILE\.lezelote\config.yaml                 ║" -ForegroundColor Green
    Write-Host "║ Log file: $Script:LogFile" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
}

# =============================================================================
# Script Entry Point
# =============================================================================

if ($Help) {
    Write-Host "LeZelote-Toolkit Setup Script for Windows"
    Write-Host "Usage: .\setup.ps1 [parameters]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -SkipSystemDeps     Skip system dependencies installation"
    Write-Host "  -SkipDocker         Skip Docker setup"
    Write-Host "  -Verbose            Enable verbose output"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\setup.ps1 -SkipDocker -Verbose"
    exit 0
}

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Main execution
try {
    Start-Installation
}
catch {
    Write-Log "ERROR" "Installation failed: $($_.Exception.Message)"
    Write-Host "Installation failed. Check the log file for details: $Script:LogFile" -ForegroundColor Red
    exit 1
}