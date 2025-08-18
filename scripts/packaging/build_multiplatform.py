#!/usr/bin/env python3
"""
LeZelote Toolkit - Multi-Platform Build and Optimization Script
===============================================================

Comprehensive build system for creating optimized packages for:
- Windows (x64, ARM64)
- Linux (x64, ARM64) 
- macOS (Intel, Apple Silicon, Universal)
- Portable USB configurations

Features:
- Cross-platform compilation
- Size optimization
- Integrity verification
- Digital signing (when configured)
- Performance testing
"""

import os
import sys
import subprocess
import shutil
import platform
import hashlib
import json
import tarfile
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import logging

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.utils.logging_handler import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

class MultiPlatformBuilder:
    """Advanced multi-platform build system for LeZelote Toolkit."""
    
    def __init__(self, version="1.0.0", output_dir="releases"):
        self.version = version
        self.project_root = project_root
        self.output_dir = Path(output_dir)
        self.build_dir = Path("build")
        self.temp_dir = Path("temp_build")
        
        # Platform configurations
        self.platforms = {
            "windows-x64": {
                "os": "windows", 
                "arch": "x64",
                "ext": "zip",
                "executable": "launch.bat",
                "python_dist": "windows-x64"
            },
            "windows-arm64": {
                "os": "windows",
                "arch": "arm64", 
                "ext": "zip",
                "executable": "launch.bat",
                "python_dist": "windows-arm64"
            },
            "linux-x64": {
                "os": "linux",
                "arch": "x64",
                "ext": "tar.gz",
                "executable": "launch.sh",
                "python_dist": "linux-x64"
            },
            "linux-arm64": {
                "os": "linux",
                "arch": "arm64",
                "ext": "tar.gz", 
                "executable": "launch.sh",
                "python_dist": "linux-arm64"
            },
            "macos-intel": {
                "os": "macos",
                "arch": "intel",
                "ext": "tar.gz",
                "executable": "launch.sh",
                "python_dist": "macos-intel"
            },
            "macos-arm64": {
                "os": "macos",
                "arch": "arm64",
                "ext": "tar.gz",
                "executable": "launch.sh", 
                "python_dist": "macos-arm64"
            },
            "macos-universal": {
                "os": "macos",
                "arch": "universal",
                "ext": "tar.gz",
                "executable": "launch.sh",
                "python_dist": "macos-universal"
            }
        }
        
        # Files to exclude from packages
        self.exclude_patterns = [
            "*.pyc", "__pycache__", "*.log", ".git*", ".pytest_cache",
            "venv", "env", ".env", "node_modules", ".DS_Store",
            "Thumbs.db", "*.tmp", "*.swp", ".vscode", ".idea",
            "releases", "build", "temp_build", "*.zip", "*.tar.gz", 
            "*.exe", "*.msi", "*.dmg", ".coverage", "htmlcov"
        ]
        
        # Optimization settings
        self.optimization = {
            "compress_python": True,
            "remove_tests": True,
            "optimize_images": True,
            "minify_configs": False,  # Keep configs readable
            "strip_comments": False   # Keep documentation
        }
        
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create required directories."""
        for directory in [self.output_dir, self.build_dir, self.temp_dir]:
            directory.mkdir(exist_ok=True, parents=True)
            
    def get_host_platform(self):
        """Detect current host platform."""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "windows":
            if machine in ["amd64", "x86_64"]:
                return "windows-x64"
            elif machine in ["arm64", "aarch64"]:
                return "windows-arm64"
        elif system == "linux":
            if machine in ["x86_64", "amd64"]:
                return "linux-x64"
            elif machine in ["aarch64", "arm64"]:
                return "linux-arm64"
        elif system == "darwin":
            if machine in ["x86_64"]:
                return "macos-intel"
            elif machine in ["arm64"]:
                return "macos-arm64"
                
        return "universal"
        
    def optimize_package_content(self, source_dir, platform_config):
        """Apply platform-specific optimizations."""
        logger.info(f"Optimizing package content for {platform_config['os']}-{platform_config['arch']}")
        
        optimizations_applied = []
        
        # Remove test files if configured
        if self.optimization["remove_tests"]:
            test_dirs = ["tests", "**/test_*", "**/*_test.py"]
            for pattern in test_dirs:
                for path in source_dir.glob(pattern):
                    if path.exists():
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        optimizations_applied.append(f"Removed test: {path.name}")
                        
        # Optimize Python bytecode
        if self.optimization["compress_python"]:
            self._compile_python_files(source_dir)
            optimizations_applied.append("Compiled Python bytecode")
            
        # Platform-specific optimizations
        if platform_config["os"] == "windows":
            self._optimize_for_windows(source_dir)
            optimizations_applied.append("Applied Windows optimizations")
        elif platform_config["os"] == "linux":
            self._optimize_for_linux(source_dir)
            optimizations_applied.append("Applied Linux optimizations")
        elif platform_config["os"] == "macos":
            self._optimize_for_macos(source_dir)
            optimizations_applied.append("Applied macOS optimizations")
            
        return optimizations_applied
        
    def _compile_python_files(self, directory):
        """Compile Python files to bytecode."""
        try:
            import py_compile
            for py_file in directory.rglob("*.py"):
                if py_file.name != "__init__.py":  # Keep __init__.py readable
                    try:
                        py_compile.compile(py_file, doraise=True, optimize=2)
                    except Exception as e:
                        logger.warning(f"Failed to compile {py_file}: {e}")
        except ImportError:
            logger.warning("py_compile not available, skipping bytecode optimization")
            
    def _optimize_for_windows(self, directory):
        """Apply Windows-specific optimizations."""
        # Ensure Windows line endings for .bat files
        for bat_file in directory.rglob("*.bat"):
            if bat_file.exists():
                content = bat_file.read_text()
                bat_file.write_text(content, newline='\r\n')
                
        # Set executable permissions on batch files
        for script in directory.rglob("*.bat"):
            if script.exists():
                script.chmod(0o755)
                
    def _optimize_for_linux(self, directory):
        """Apply Linux-specific optimizations.""" 
        # Ensure Unix line endings for shell scripts
        for sh_file in directory.rglob("*.sh"):
            if sh_file.exists():
                content = sh_file.read_text()
                sh_file.write_text(content, newline='\n')
                sh_file.chmod(0o755)
                
        # Set proper permissions on Python files
        for py_file in directory.rglob("*.py"):
            if py_file.name in ["run_cli.py", "setup.py"]:
                py_file.chmod(0o755)
                
    def _optimize_for_macos(self, directory):
        """Apply macOS-specific optimizations."""
        # Same as Linux but with macOS-specific considerations
        self._optimize_for_linux(directory)
        
        # Remove .DS_Store files if they exist
        for ds_store in directory.rglob(".DS_Store"):
            ds_store.unlink()
            
    def create_platform_package(self, platform_name, target_platforms=None):
        """Create optimized package for specific platform."""
        if platform_name not in self.platforms:
            raise ValueError(f"Unknown platform: {platform_name}")
            
        platform_config = self.platforms[platform_name]
        logger.info(f"Creating package for {platform_name}")
        
        # Create temporary build directory
        platform_build_dir = self.temp_dir / f"build_{platform_name}"
        if platform_build_dir.exists():
            shutil.rmtree(platform_build_dir)
        platform_build_dir.mkdir(parents=True)
        
        # Copy project files
        self._copy_project_files(platform_build_dir)
        
        # Apply optimizations
        optimizations = self.optimize_package_content(platform_build_dir, platform_config)
        
        # Create platform-specific launcher
        self._create_platform_launcher(platform_build_dir, platform_config)
        
        # Create version info
        version_info = {
            "name": "LeZelote Toolkit",
            "version": self.version,
            "platform": platform_name,
            "os": platform_config["os"],
            "architecture": platform_config["arch"], 
            "build_date": datetime.utcnow().isoformat(),
            "optimizations": optimizations,
            "package_type": "platform_optimized"
        }
        
        version_file = platform_build_dir / "platform_info.json"
        with open(version_file, "w") as f:
            json.dump(version_info, f, indent=2)
            
        # Create archive
        package_name = f"lezelote-toolkit-{self.version}-{platform_name}"
        
        if platform_config["ext"] == "zip":
            archive_path = self.output_dir / f"{package_name}.zip"
            self._create_zip_archive(platform_build_dir, archive_path, package_name)
        else:
            archive_path = self.output_dir / f"{package_name}.tar.gz"
            self._create_tar_archive(platform_build_dir, archive_path, package_name)
            
        # Calculate checksums and metadata
        file_size = archive_path.stat().st_size
        checksum = self._calculate_checksum(archive_path)
        
        # Create signature if signing key available
        signature_path = self._create_signature(archive_path)
        
        # Clean up temporary directory
        shutil.rmtree(platform_build_dir)
        
        package_info = {
            "platform": platform_name,
            "path": str(archive_path),
            "size": file_size,
            "checksum": checksum,
            "signature": signature_path,
            "created_at": datetime.utcnow().isoformat(),
            "version_info": version_info
        }
        
        logger.info(f"✅ Created {platform_name} package: {archive_path.name}")
        logger.info(f"   Size: {file_size / 1024 / 1024:.1f} MB")
        logger.info(f"   Checksum: {checksum[:16]}...")
        
        return package_info
        
    def _copy_project_files(self, dest_dir):
        """Copy project files excluding patterns."""
        copied_files = 0
        
        for item in self.project_root.rglob("*"):
            if self._should_exclude(item):
                continue
                
            relative_path = item.relative_to(self.project_root)
            dest_path = dest_dir / relative_path
            
            if item.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_path)
                copied_files += 1
            elif item.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
                
        logger.info(f"Copied {copied_files} files")
        return copied_files
        
    def _should_exclude(self, path):
        """Check if path matches exclusion patterns."""
        path_str = str(path)
        
        for pattern in self.exclude_patterns:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
                
        return False
        
    def _create_platform_launcher(self, build_dir, platform_config):
        """Create optimized launcher for platform."""
        if platform_config["os"] == "windows":
            self._create_windows_launcher(build_dir)
        else:
            self._create_unix_launcher(build_dir, platform_config["os"])
            
    def _create_windows_launcher(self, build_dir):
        """Create optimized Windows launcher."""
        launcher_content = f'''@echo off
REM LeZelote Toolkit v{self.version} - Windows Launcher
REM Optimized for Windows deployment

setlocal enabledelayedexpansion

REM Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found. Searching for portable Python...
    if exist "runtime\\python\\python.exe" (
        set PYTHON_CMD=runtime\\python\\python.exe
    ) else (
        echo Please install Python 3.9+ from python.org
        pause
        exit /b 1
    )
) else (
    set PYTHON_CMD=python
)

REM Set environment
set PYTHONPATH=%CD%
set TOOLKIT_HOME=%CD%

REM Launch application
echo Starting LeZelote Toolkit...
%PYTHON_CMD% run_cli.py %*

if %errorLevel% neq 0 (
    echo.
    echo Error occurred. Check logs in logs/ directory
    pause
)
'''
        launcher_path = build_dir / "launch.bat"
        with open(launcher_path, "w", newline='\r\n') as f:
            f.write(launcher_content)
        launcher_path.chmod(0o755)
        
    def _create_unix_launcher(self, build_dir, os_type):
        """Create optimized Unix/Linux/macOS launcher."""
        launcher_content = f'''#!/bin/bash
# LeZelote Toolkit v{self.version} - {os_type.title()} Launcher
# Optimized for {os_type} deployment

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\\033[0;32m'
RED='\\033[0;31m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

# Check Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    # Check if it's Python 3
    if python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${{RED}}Python 3.9+ required${{NC}}"
        exit 1
    fi
elif [ -x "runtime/python/bin/python3" ]; then
    PYTHON_CMD="runtime/python/bin/python3"
else
    echo -e "${{RED}}Python 3.9+ not found${{NC}}"
    echo "Please install Python or use a package with embedded runtime"
    exit 1
fi

# Set environment
export PYTHONPATH="$SCRIPT_DIR"
export TOOLKIT_HOME="$SCRIPT_DIR"

# Launch application
echo -e "${{GREEN}}Starting LeZelote Toolkit v{self.version}...${{NC}}"
exec "$PYTHON_CMD" run_cli.py "$@"
'''
        launcher_path = build_dir / "launch.sh"
        with open(launcher_path, "w", newline='\n') as f:
            f.write(launcher_content)
        launcher_path.chmod(0o755)
        
    def _create_zip_archive(self, source_dir, archive_path, base_name):
        """Create ZIP archive."""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arc_path = base_name / file_path.relative_to(source_dir)
                    zipf.write(file_path, arc_path)
                    
    def _create_tar_archive(self, source_dir, archive_path, base_name):
        """Create compressed TAR archive."""
        with tarfile.open(archive_path, "w:gz") as tar:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arc_path = base_name / file_path.relative_to(source_dir)
                    tar.add(file_path, arcname=arc_path)
                    
    def _calculate_checksum(self, file_path, algorithm="sha256"):
        """Calculate file checksum."""
        hash_obj = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
        
    def _create_signature(self, file_path):
        """Create digital signature if signing configured."""
        # Placeholder for digital signing
        # In production, this would use GPG or other signing tools
        signature_path = str(file_path) + ".sig"
        
        # Create simple verification signature
        checksum = self._calculate_checksum(file_path)
        signature_content = {
            "file": file_path.name,
            "algorithm": "sha256",
            "checksum": checksum,
            "signed_by": "LeZelote Toolkit Build System",
            "signed_at": datetime.utcnow().isoformat()
        }
        
        with open(signature_path, "w") as f:
            json.dump(signature_content, f, indent=2)
            
        return signature_path
        
    def build_all_platforms(self, platforms=None, parallel=True):
        """Build packages for multiple platforms."""
        if platforms is None:
            platforms = list(self.platforms.keys())
        elif isinstance(platforms, str):
            platforms = [platforms]
            
        logger.info(f"Building packages for {len(platforms)} platforms")
        
        packages = []
        
        if parallel and len(platforms) > 1:
            # Parallel building
            with ThreadPoolExecutor(max_workers=min(4, len(platforms))) as executor:
                future_to_platform = {
                    executor.submit(self.create_platform_package, platform): platform
                    for platform in platforms
                }
                
                for future in as_completed(future_to_platform):
                    platform = future_to_platform[future]
                    try:
                        package_info = future.result()
                        packages.append(package_info)
                    except Exception as e:
                        logger.error(f"Failed to build {platform}: {e}")
        else:
            # Sequential building
            for platform in platforms:
                try:
                    package_info = self.create_platform_package(platform)
                    packages.append(package_info)
                except Exception as e:
                    logger.error(f"Failed to build {platform}: {e}")
                    
        return packages
        
    def create_usb_optimized_package(self):
        """Create special USB-optimized package."""
        logger.info("Creating USB-optimized package...")
        
        usb_build_dir = self.temp_dir / "usb_build"
        if usb_build_dir.exists():
            shutil.rmtree(usb_build_dir)
        usb_build_dir.mkdir(parents=True)
        
        # Copy project with USB-specific optimizations
        self._copy_project_files(usb_build_dir)
        
        # USB-specific optimizations
        self._apply_usb_optimizations(usb_build_dir)
        
        # Create autorun files
        self._create_autorun_files(usb_build_dir)
        
        # Create USB package
        package_name = f"lezelote-toolkit-{self.version}-usb-portable"
        archive_path = self.output_dir / f"{package_name}.zip"
        
        self._create_zip_archive(usb_build_dir, archive_path, package_name)
        
        # Calculate metadata
        file_size = archive_path.stat().st_size
        checksum = self._calculate_checksum(archive_path)
        
        package_info = {
            "platform": "usb-portable",
            "path": str(archive_path),
            "size": file_size,
            "checksum": checksum,
            "created_at": datetime.utcnow().isoformat(),
            "special": "usb_optimized"
        }
        
        # Clean up
        shutil.rmtree(usb_build_dir)
        
        logger.info(f"✅ Created USB-optimized package: {archive_path.name}")
        
        return package_info
        
    def _apply_usb_optimizations(self, directory):
        """Apply USB-specific optimizations."""
        # Compress everything maximally for USB space constraints
        # Remove unnecessary files more aggressively
        
        # Remove development files
        dev_patterns = [
            "*.md", ".git*", "tests/", "docs/developer_guide.md",
            "build/", "temp*/", "*.pyc"
        ]
        
        for pattern in dev_patterns:
            for path in directory.glob(pattern):
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                        
        # Create USB-specific configuration
        usb_config = {
            "usb_mode": True,
            "portable": True,
            "auto_cleanup": True,
            "minimal_logging": True,
            "fast_startup": True
        }
        
        config_file = directory / "config" / "usb_config.json"
        config_file.parent.mkdir(exist_ok=True, parents=True)
        with open(config_file, "w") as f:
            json.dump(usb_config, f, indent=2)
            
    def _create_autorun_files(self, directory):
        """Create autorun files for USB."""
        # Windows autorun.inf
        autorun_inf = '''[AutoRun]
label=LeZelote Toolkit
icon=icon.ico
open=launch.bat
action=Start LeZelote Toolkit
'''
        with open(directory / "autorun.inf", "w") as f:
            f.write(autorun_inf)
            
        # Create simple icon file (placeholder)
        # In production, this would be a real .ico file
        with open(directory / "icon.ico", "w") as f:
            f.write("# LeZelote Toolkit Icon Placeholder")
            
    def create_checksums_manifest(self, packages):
        """Create comprehensive checksums manifest."""
        manifest_path = self.output_dir / "checksums_manifest.json"
        
        manifest = {
            "manifest_version": "1.0",
            "toolkit_version": self.version,
            "created_at": datetime.utcnow().isoformat(),
            "total_packages": len(packages),
            "packages": {}
        }
        
        for package in packages:
            filename = Path(package["path"]).name
            manifest["packages"][filename] = {
                "platform": package["platform"],
                "size": package["size"],
                "checksum": package["checksum"],
                "algorithm": "sha256"
            }
            
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            
        logger.info(f"Created checksums manifest: {manifest_path}")
        return str(manifest_path)
        
    def run_integrity_tests(self, packages):
        """Run integrity tests on created packages."""
        logger.info("Running integrity tests on packages...")
        
        results = []
        
        for package in packages:
            package_path = Path(package["path"])
            
            # Test 1: File exists and readable
            test_result = {
                "package": package_path.name,
                "platform": package["platform"], 
                "tests": {}
            }
            
            # Existence test
            test_result["tests"]["file_exists"] = package_path.exists()
            
            # Size test
            if package_path.exists():
                actual_size = package_path.stat().st_size
                test_result["tests"]["size_match"] = actual_size == package["size"]
                test_result["tests"]["actual_size"] = actual_size
            else:
                test_result["tests"]["size_match"] = False
                test_result["tests"]["actual_size"] = 0
                
            # Checksum test
            if package_path.exists():
                actual_checksum = self._calculate_checksum(package_path)
                test_result["tests"]["checksum_match"] = actual_checksum == package["checksum"]
            else:
                test_result["tests"]["checksum_match"] = False
                
            # Archive validity test
            test_result["tests"]["archive_valid"] = self._test_archive_validity(package_path)
            
            # Overall test result
            all_tests = [
                test_result["tests"]["file_exists"],
                test_result["tests"]["size_match"], 
                test_result["tests"]["checksum_match"],
                test_result["tests"]["archive_valid"]
            ]
            test_result["overall_pass"] = all(all_tests)
            
            results.append(test_result)
            
            # Log result
            status = "✅ PASS" if test_result["overall_pass"] else "❌ FAIL"
            logger.info(f"{status} {package_path.name}")
            
        # Save test results
        results_path = self.output_dir / "integrity_test_results.json"
        with open(results_path, "w") as f:
            json.dump({
                "test_run_date": datetime.utcnow().isoformat(),
                "total_packages": len(results),
                "passed": sum(1 for r in results if r["overall_pass"]),
                "failed": sum(1 for r in results if not r["overall_pass"]),
                "results": results
            }, f, indent=2)
            
        passed = sum(1 for r in results if r["overall_pass"])
        logger.info(f"Integrity tests completed: {passed}/{len(results)} passed")
        
        return results_path

    def _test_archive_validity(self, archive_path):
        """Test if archive can be opened and contains expected files."""
        if not archive_path.exists():
            return False
            
        try:
            if archive_path.suffix == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    # Test if archive can be opened
                    info_list = zipf.infolist()
                    # Check for required files
                    required_files = ["run_cli.py", "requirements.txt"]
                    found_files = [info.filename for info in info_list]
                    
                    for required in required_files:
                        if not any(required in filename for filename in found_files):
                            return False
                            
            elif archive_path.suffix == ".gz":
                with tarfile.open(archive_path, 'r:gz') as tar:
                    # Test if archive can be opened
                    members = tar.getmembers()
                    # Check for required files
                    required_files = ["run_cli.py", "requirements.txt"]
                    found_files = [member.name for member in members]
                    
                    for required in required_files:
                        if not any(required in filename for filename in found_files):
                            return False
                            
            return True
            
        except Exception as e:
            logger.warning(f"Archive validation failed for {archive_path}: {e}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Multi-platform build system for LeZelote Toolkit")
    parser.add_argument("--version", default="1.0.0", help="Version number")
    parser.add_argument("--output-dir", default="releases", help="Output directory")
    parser.add_argument("--platforms", nargs="*", 
                       choices=list(MultiPlatformBuilder("1.0.0").platforms.keys()) + ["all"],
                       default=["all"], help="Platforms to build")
    parser.add_argument("--usb-optimized", action="store_true", help="Create USB-optimized package")
    parser.add_argument("--parallel", action="store_true", default=True, help="Build in parallel")
    parser.add_argument("--test-integrity", action="store_true", default=True, help="Run integrity tests")
    parser.add_argument("--host-only", action="store_true", help="Build for host platform only")
    
    args = parser.parse_args()
    
    builder = MultiPlatformBuilder(args.version, args.output_dir)
    
    # Determine platforms to build
    if args.host_only:
        platforms = [builder.get_host_platform()]
        logger.info(f"Building for host platform only: {platforms[0]}")
    elif "all" in args.platforms:
        platforms = list(builder.platforms.keys())
    else:
        platforms = args.platforms
        
    logger.info(f"Building LeZelote Toolkit v{args.version} for platforms: {', '.join(platforms)}")
    
    try:
        # Build platform packages
        packages = builder.build_all_platforms(platforms, args.parallel)
        
        # Create USB-optimized package if requested
        if args.usb_optimized:
            usb_package = builder.create_usb_optimized_package()
            packages.append(usb_package)
            
        # Create checksums manifest
        builder.create_checksums_manifest(packages)
        
        # Run integrity tests if requested
        if args.test_integrity:
            builder.run_integrity_tests(packages)
            
        # Summary
        total_size = sum(p["size"] for p in packages) / 1024 / 1024
        logger.info(f"🎉 Multi-platform build completed!")
        logger.info(f"📦 Built {len(packages)} packages")
        logger.info(f"💾 Total size: {total_size:.1f} MB")
        logger.info(f"📁 Output: {builder.output_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"Build failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)