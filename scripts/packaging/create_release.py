#!/usr/bin/env python3
"""
LeZelote Toolkit - Release Creation Script
Creates distribution packages for Windows, Linux, and macOS
"""

import os
import sys
import shutil
import tarfile
import zipfile
import hashlib
import json
from pathlib import Path
from datetime import datetime
import argparse
import subprocess

# Add the project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.utils.logging_handler import get_logger
except ImportError:
    # Fallback logging if core modules not available
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

class ReleaseCreator:
    """Creates release packages for LeZelote Toolkit."""
    
    def __init__(self, version="1.0.0", output_dir="releases"):
        self.version = version
        self.project_root = project_root
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Files to exclude from packages
        self.exclude_patterns = [
            "*.pyc", "__pycache__", "*.log", ".git", ".pytest_cache",
            "venv", "env", ".env", "node_modules", ".DS_Store",
            "Thumbs.db", "*.tmp", "*.swp", ".vscode", ".idea",
            "releases", "*.zip", "*.tar.gz", "*.exe", "*.msi"
        ]
        
        # Core files that must be included
        self.core_files = [
            "run_cli.py", "launch.sh", "launch.bat", "requirements.txt",
            "README.md", "LICENSE", "DISCLAIMER.md"
        ]
        
        # Directories to include
        self.core_dirs = [
            "core", "modules", "interfaces", "tools", "data", "config",
            "scripts", "runtime", "docs", "tests"
        ]
        
    def should_exclude(self, path):
        """Check if path should be excluded from package."""
        path_str = str(path)
        
        for pattern in self.exclude_patterns:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
                
        return False
        
    def copy_files(self, source_dir, dest_dir):
        """Copy files while respecting exclude patterns."""
        files_copied = 0
        
        for item in source_dir.rglob("*"):
            if self.should_exclude(item):
                continue
                
            relative_path = item.relative_to(source_dir)
            dest_path = dest_dir / relative_path
            
            if item.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)
                files_copied += 1
            elif item.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
                
        return files_copied
        
    def create_portable_package(self, platform="universal"):
        """Create a portable ZIP package."""
        logger.info(f"Creating portable package for {platform}...")
        
        package_name = f"lezelote-toolkit-{self.version}-{platform}-portable"
        temp_dir = self.output_dir / "temp" / package_name
        
        # Clean and create temp directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        
        # Copy core files and directories
        files_copied = 0
        
        # Copy main files
        for file_name in self.core_files:
            source_file = self.project_root / file_name
            if source_file.exists():
                shutil.copy2(source_file, temp_dir / file_name)
                files_copied += 1
                
        # Copy directories
        for dir_name in self.core_dirs:
            source_dir = self.project_root / dir_name
            if source_dir.exists():
                dest_dir = temp_dir / dir_name
                files_copied += self.copy_files(source_dir, dest_dir)
                
        logger.info(f"Copied {files_copied} files to package")
        
        # Create version info file
        version_info = {
            "name": "LeZelote Toolkit",
            "version": self.version,
            "platform": platform,
            "package_type": "portable",
            "created_at": datetime.utcnow().isoformat(),
            "python_version_required": "3.9+",
            "files_count": files_copied
        }
        
        with open(temp_dir / "version_info.json", "w") as f:
            json.dump(version_info, f, indent=2)
            
        # Create ZIP archive
        zip_path = self.output_dir / f"{package_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    arc_path = file_path.relative_to(temp_dir.parent)
                    zipf.write(file_path, arc_path)
                    
        # Calculate checksums
        zip_size = zip_path.stat().st_size
        zip_hash = self.calculate_checksum(zip_path)
        
        # Clean up temp directory
        shutil.rmtree(temp_dir.parent)
        
        logger.info(f"Created portable package: {zip_path}")
        logger.info(f"Package size: {zip_size / 1024 / 1024:.1f} MB")
        logger.info(f"SHA256: {zip_hash}")
        
        return {
            "path": str(zip_path),
            "size": zip_size,
            "checksum": zip_hash,
            "type": "portable_zip"
        }
        
    def create_source_package(self):
        """Create source code package."""
        logger.info("Creating source code package...")
        
        package_name = f"lezelote-toolkit-{self.version}-source"
        tar_path = self.output_dir / f"{package_name}.tar.gz"
        
        with tarfile.open(tar_path, "w:gz") as tar:
            for item in self.project_root.rglob("*"):
                if self.should_exclude(item) or item.is_dir():
                    continue
                    
                # Skip if in output directory to avoid recursion
                if self.output_dir in item.parents:
                    continue
                    
                arc_path = package_name / item.relative_to(self.project_root)
                tar.add(item, arcname=arc_path)
                
        tar_size = tar_path.stat().st_size
        tar_hash = self.calculate_checksum(tar_path)
        
        logger.info(f"Created source package: {tar_path}")
        logger.info(f"Package size: {tar_size / 1024 / 1024:.1f} MB")
        logger.info(f"SHA256: {tar_hash}")
        
        return {
            "path": str(tar_path),
            "size": tar_size, 
            "checksum": tar_hash,
            "type": "source_tarball"
        }
        
    def calculate_checksum(self, file_path, algorithm="sha256"):
        """Calculate file checksum."""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
        
    def create_checksums_file(self, packages):
        """Create checksums file for all packages."""
        checksums_path = self.output_dir / "checksums.txt"
        
        with open(checksums_path, "w") as f:
            f.write(f"# LeZelote Toolkit v{self.version} - Package Checksums\n")
            f.write(f"# Generated: {datetime.utcnow().isoformat()}\n")
            f.write("# Algorithm: SHA256\n\n")
            
            for package in packages:
                filename = Path(package["path"]).name
                f.write(f"{package['checksum']}  {filename}\n")
                
        logger.info(f"Created checksums file: {checksums_path}")
        return str(checksums_path)
        
    def create_release_info(self, packages):
        """Create release information file."""
        release_info = {
            "name": "LeZelote Toolkit",
            "version": self.version,
            "release_date": datetime.utcnow().isoformat(),
            "description": "Comprehensive penetration testing toolkit",
            "homepage": "https://github.com/LeZelote01/LeZelote-Toolkit",
            "license": "MIT",
            "python_requirements": ">=3.9",
            "packages": packages,
            "total_size": sum(p["size"] for p in packages),
            "package_count": len(packages)
        }
        
        release_path = self.output_dir / "release_info.json"
        
        with open(release_path, "w") as f:
            json.dump(release_info, f, indent=2)
            
        logger.info(f"Created release info: {release_path}")
        return str(release_path)
        
    def create_installer_script(self, platform="linux"):
        """Create platform-specific installer script."""
        if platform == "linux":
            installer_content = self._get_linux_installer()
            installer_path = self.output_dir / "install.sh"
        elif platform == "windows":
            installer_content = self._get_windows_installer()
            installer_path = self.output_dir / "install.bat"
        else:
            logger.warning(f"No installer template for platform: {platform}")
            return None
            
        with open(installer_path, "w", newline='\n' if platform == "linux" else '\r\n') as f:
            f.write(installer_content)
            
        if platform == "linux":
            os.chmod(installer_path, 0o755)
            
        logger.info(f"Created installer script: {installer_path}")
        return str(installer_path)
        
    def _get_linux_installer(self):
        """Get Linux installer script content."""
        return f'''#!/bin/bash
# LeZelote Toolkit v{self.version} - Linux Installer
set -e

TOOLKIT_VERSION="{self.version}"
PACKAGE_NAME="lezelote-toolkit-${{TOOLKIT_VERSION}}-universal-portable.zip"
INSTALL_DIR="/opt/lezelote-toolkit"
BIN_DIR="/usr/local/bin"

echo "LeZelote Toolkit v$TOOLKIT_VERSION - Linux Installer"
echo "=================================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This installer must be run as root (use sudo)"
   exit 1
fi

# Check dependencies
echo "Checking dependencies..."
for cmd in python3 unzip wget; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "Missing dependency: $cmd"
        echo "Please install it and run this installer again"
        exit 1
    fi
done

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{{sys.version_info.major}}.{{sys.version_info.minor}}')")
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "Python 3.9+ required (found: $PYTHON_VERSION)"
    exit 1
fi

# Download package if not present
if [ ! -f "$PACKAGE_NAME" ]; then
    echo "Downloading $PACKAGE_NAME..."
    wget "https://github.com/LeZelote01/LeZelote-Toolkit/releases/download/v$TOOLKIT_VERSION/$PACKAGE_NAME"
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Extract package
echo "Extracting package..."
unzip -q "$PACKAGE_NAME" -d "$INSTALL_DIR"
mv "$INSTALL_DIR"/lezelote-toolkit-*/* "$INSTALL_DIR/"
rmdir "$INSTALL_DIR"/lezelote-toolkit-*

# Install dependencies
echo "Installing Python dependencies..."
cd "$INSTALL_DIR"
python3 -m pip install -r requirements.txt

# Create symlink
echo "Creating system-wide command..."
ln -sf "$INSTALL_DIR/launch.sh" "$BIN_DIR/lezelote"

# Set permissions
chmod +x "$INSTALL_DIR/launch.sh"
chmod +x "$INSTALL_DIR/scripts/install/setup.sh"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "Usage:"
echo "  lezelote                    # Launch toolkit"
echo "  lezelote --help            # Show help"
echo "  lezelote --web             # Launch web interface"
echo ""
echo "Configuration files: $INSTALL_DIR/config/"
echo "Documentation: $INSTALL_DIR/docs/"
echo ""
'''

    def _get_windows_installer(self):
        """Get Windows installer script content."""
        return f'''@echo off
REM LeZelote Toolkit v{self.version} - Windows Installer

set TOOLKIT_VERSION={self.version}
set PACKAGE_NAME=lezelote-toolkit-%TOOLKIT_VERSION%-universal-portable.zip
set INSTALL_DIR=C:\\Program Files\\LeZelote-Toolkit

echo LeZelote Toolkit v%TOOLKIT_VERSION% - Windows Installer
echo ==================================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

REM Check if package exists
if not exist "%PACKAGE_NAME%" (
    echo Package %PACKAGE_NAME% not found in current directory
    echo Please download it from the releases page
    pause
    exit /b 1
)

REM Create installation directory
echo Creating installation directory: %INSTALL_DIR%
mkdir "%INSTALL_DIR%" 2>nul

REM Extract package (requires PowerShell)
echo Extracting package...
powershell -Command "Expand-Archive -Path '%PACKAGE_NAME%' -DestinationPath '%INSTALL_DIR%' -Force"

REM Move files from subdirectory
for /d %%d in ("%INSTALL_DIR%\\lezelote-toolkit-*") do (
    move "%%d\\*" "%INSTALL_DIR%\\" >nul
    rmdir "%%d"
)

REM Install dependencies
echo Installing Python dependencies...
cd /d "%INSTALL_DIR%"
python -m pip install -r requirements.txt

REM Add to PATH (requires admin privileges)
echo Adding to system PATH...
setx /M PATH "%PATH%;%INSTALL_DIR%" >nul

echo.
echo ✅ Installation completed successfully!
echo.
echo Usage:
echo   launch.bat                  # Launch toolkit
echo   launch.bat --help          # Show help  
echo   launch.bat --web           # Launch web interface
echo.
echo Configuration files: %INSTALL_DIR%\\config\\
echo Documentation: %INSTALL_DIR%\\docs\\
echo.
echo Please restart your command prompt to use the 'lezelote' command
pause
'''

    def validate_project_structure(self):
        """Validate that all required files exist."""
        logger.info("Validating project structure...")
        
        missing_files = []
        
        # Check core files
        for file_name in self.core_files:
            if not (self.project_root / file_name).exists():
                missing_files.append(file_name)
                
        # Check core directories
        for dir_name in self.core_dirs:
            if not (self.project_root / dir_name).exists():
                missing_files.append(f"{dir_name}/ (directory)")
                
        if missing_files:
            logger.error("Missing required files/directories:")
            for item in missing_files:
                logger.error(f"  - {item}")
            return False
            
        logger.info("Project structure validation passed")
        return True
        
    def create_full_release(self):
        """Create complete release with all packages."""
        logger.info(f"Creating full release for version {self.version}")
        
        # Validate project structure
        if not self.validate_project_structure():
            logger.error("Project validation failed. Cannot create release.")
            return False
            
        packages = []
        
        try:
            # Create portable packages
            for platform in ["universal", "linux", "windows", "macos"]:
                package_info = self.create_portable_package(platform)
                packages.append(package_info)
                
            # Create source package
            source_package = self.create_source_package()
            packages.append(source_package)
            
            # Create additional files
            self.create_checksums_file(packages)
            self.create_release_info(packages)
            
            # Create installer scripts
            self.create_installer_script("linux")
            self.create_installer_script("windows")
            
            # Summary
            total_size = sum(p["size"] for p in packages) / 1024 / 1024
            logger.info(f"✅ Release creation completed!")
            logger.info(f"📦 Created {len(packages)} packages")
            logger.info(f"💾 Total size: {total_size:.1f} MB")
            logger.info(f"📁 Output directory: {self.output_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"Release creation failed: {str(e)}")
            return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create LeZelote Toolkit release packages")
    parser.add_argument("--version", default="1.0.0", help="Version number for release")
    parser.add_argument("--output-dir", default="releases", help="Output directory for packages")
    parser.add_argument("--platform", choices=["universal", "linux", "windows", "macos", "all"], 
                       default="all", help="Platform to create package for")
    parser.add_argument("--package-type", choices=["portable", "source", "all"], 
                       default="all", help="Type of package to create")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only validate project structure")
    
    args = parser.parse_args()
    
    # Initialize release creator
    creator = ReleaseCreator(args.version, args.output_dir)
    
    if args.validate_only:
        success = creator.validate_project_structure()
        sys.exit(0 if success else 1)
        
    # Create releases based on arguments
    if args.platform == "all" and args.package_type == "all":
        success = creator.create_full_release()
    else:
        # Individual package creation
        packages = []
        
        if args.package_type in ["portable", "all"]:
            if args.platform == "all":
                platforms = ["universal", "linux", "windows", "macos"]
            else:
                platforms = [args.platform]
                
            for platform in platforms:
                package_info = creator.create_portable_package(platform)
                packages.append(package_info)
                
        if args.package_type in ["source", "all"]:
            source_package = creator.create_source_package()
            packages.append(source_package)
            
        if packages:
            creator.create_checksums_file(packages)
            creator.create_release_info(packages)
            success = True
        else:
            success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()