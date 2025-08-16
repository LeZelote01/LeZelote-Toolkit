#!/usr/bin/env python3
"""
LeZelote-Toolkit - Binary Download Manager
Automated download and installation of security tools binaries
"""

import os
import sys
import json
import requests
import hashlib
import zipfile
import tarfile
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.logging_handler import get_logger
from core.utils.file_ops import FileOperations

logger = get_logger(__name__)

class BinaryDownloadManager:
    """Manages automated download and installation of security tools"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.file_ops = FileOperations()
        self.project_root = project_root
        self.binaries_dir = self.project_root / "tools" / "binaries"
        self.downloads_dir = self.project_root / "downloads"
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Tool configurations
        self.tools_config = self._load_tools_config()
        self.download_stats = {
            'total': 0,
            'downloaded': 0,
            'failed': 0,
            'skipped': 0
        }
        
    def _load_tools_config(self) -> Dict:
        """Load tools configuration with download URLs and checksums"""
        # Import configuration from external file
        try:
            from scripts.install.tools_config import COMPLETE_TOOLS_CONFIG
            return COMPLETE_TOOLS_CONFIG
        except ImportError:
            # Fallback to basic configuration if extended config not available
            self.logger.warning("Extended tools config not found, using basic configuration")
            return self._get_basic_config()
    
    def _get_basic_config(self) -> Dict:
        """Fallback basic configuration"""
        return {
            "nmap": {
                "priority": 1,
                "category": "reconnaissance",
                "description": "Network discovery and security auditing",
                "license": "free",
                "install_method": "package_manager",
                "windows": {
                    "url": "https://nmap.org/dist/nmap-7.95-win32.zip",
                    "binary": "nmap.exe",
                    "size_mb": 25
                },
                "linux": {
                    "package_name": "nmap",
                    "binary": "nmap",
                    "install_cmd": "apt-get update && apt-get install -y nmap || yum install -y nmap || pacman -S nmap",
                    "size_mb": 5
                },
                "macos": {
                    "package_name": "nmap",
                    "binary": "nmap",
                    "install_cmd": "brew install nmap",
                    "size_mb": 5
                }
            }
        }
    
    def detect_platform(self) -> str:
        """Detect current platform"""
        import platform
        system = platform.system().lower()
        
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        else:
            raise ValueError(f"Unsupported platform: {system}")
    
    def download_file(self, url: str, filepath: Path, 
                     expected_checksum: Optional[str] = None) -> bool:
        """Download file with progress and verification"""
        try:
            self.logger.info(f"Downloading: {url}")
            
            # Stream download with progress
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            
            # Verify checksum if provided
            if expected_checksum:
                if not self.verify_checksum(filepath, expected_checksum):
                    self.logger.error(f"Checksum verification failed: {filepath}")
                    return False
            
            self.logger.info(f"Downloaded successfully: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {url} - {e}")
            return False
    
    def verify_checksum(self, filepath: Path, expected: str) -> bool:
        """Verify file checksum"""
        try:
            algorithm, expected_hash = expected.split(':', 1)
            
            hasher = hashlib.new(algorithm)
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            actual_hash = hasher.hexdigest()
            return actual_hash == expected_hash
            
        except Exception as e:
            self.logger.error(f"Checksum verification error: {e}")
            return False
    
    def extract_archive(self, filepath: Path, extract_dir: Path) -> bool:
        """Extract archive (zip, tar.gz, etc.)"""
        try:
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            if filepath.suffix.lower() == '.zip':
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    
            elif filepath.name.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(filepath, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_dir)
                    
            elif filepath.suffix.lower() == '.tar':
                with tarfile.open(filepath, 'r') as tar_ref:
                    tar_ref.extractall(extract_dir)
                    
            else:
                # Single file, copy directly
                import shutil
                shutil.copy2(filepath, extract_dir)
            
            self.logger.info(f"Extracted: {filepath} -> {extract_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {filepath} - {e}")
            return False
    
    def install_tool(self, tool_name: str, platform: str = None) -> bool:
        """Install a single tool for specified platform"""
        if platform is None:
            platform = self.detect_platform()
            
        if tool_name not in self.tools_config:
            self.logger.error(f"Unknown tool: {tool_name}")
            return False
            
        tool_config = self.tools_config[tool_name]
        if platform not in tool_config:
            self.logger.error(f"Platform {platform} not supported for {tool_name}")
            return False
            
        platform_config = tool_config[platform]
        
        # Target directories
        target_dir = self.binaries_dir / platform
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if already installed
        binary_name = platform_config['binary']
        target_binary = target_dir / binary_name
        
        if target_binary.exists():
            self.logger.info(f"Tool already installed: {tool_name} ({binary_name})")
            self.download_stats['skipped'] += 1
            return True
        
        self.logger.info(f"Installing {tool_name} for {platform}...")
        
        # Choose installation method
        install_method = tool_config.get('install_method', 'download')
        
        if install_method == 'package_manager':
            return self._install_via_package_manager(tool_name, platform_config, target_dir)
        elif install_method == 'git_clone':
            return self._install_via_git_clone(tool_name, platform_config, target_dir)
        else:
            # Default download method
            return self._install_via_download(tool_name, platform_config, target_dir)
    
    def _install_binary(self, extract_dir: Path, target_dir: Path, 
                       config: Dict, tool_name: str) -> bool:
        """Find and install binary from extracted directory"""
        try:
            binary_name = config['binary']
            
            # Search for binary in extracted directory
            binary_path = None
            for root, dirs, files in os.walk(extract_dir):
                if binary_name in files:
                    binary_path = Path(root) / binary_name
                    break
            
            if not binary_path or not binary_path.exists():
                self.logger.error(f"Binary not found: {binary_name} in {extract_dir}")
                return False
            
            # Copy binary to target directory
            target_binary = target_dir / binary_name
            import shutil
            shutil.copy2(binary_path, target_binary)
            
            # Make executable on Unix systems
            if os.name == 'posix':
                os.chmod(target_binary, 0o755)
            
            # Create wrapper script if specified
            if 'wrapper' in config:
                self._create_wrapper(target_dir, config, tool_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Binary installation failed: {e}")
            return False
    
    def _create_wrapper(self, target_dir: Path, config: Dict, tool_name: str):
        """Create wrapper script for Python/Perl tools"""
        wrapper_name = config['wrapper']
        binary_name = config['binary']
        wrapper_path = target_dir / wrapper_name
        
        if wrapper_name.endswith('.bat'):
            # Windows batch wrapper
            wrapper_content = f'''@echo off
python "%~dp0{binary_name}" %*
'''
        else:
            # Unix shell wrapper
            wrapper_content = f'''#!/bin/bash
exec python3 "$(dirname "$0")/{binary_name}" "$@"
'''
        
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        if os.name == 'posix':
            os.chmod(wrapper_path, 0o755)
    
    def _install_via_package_manager(self, tool_name: str, config: Dict, target_dir: Path) -> bool:
        """Install tool via system package manager"""
        try:
            install_cmd = config.get('install_cmd')
            if not install_cmd:
                self.logger.error(f"No install command configured for {tool_name}")
                return False
            
            self.logger.info(f"Installing {tool_name} via package manager...")
            
            # Execute install command
            result = subprocess.run(
                install_cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Find installed binary
                binary_name = config['binary']
                system_paths = ['/usr/bin', '/usr/local/bin', '/bin']
                
                for path in system_paths:
                    system_binary = Path(path) / binary_name
                    if system_binary.exists():
                        # Create symlink in our binaries directory
                        target_binary = target_dir / binary_name
                        target_binary.symlink_to(system_binary)
                        self.logger.info(f"Created symlink: {target_binary} -> {system_binary}")
                        self.download_stats['downloaded'] += 1
                        return True
                
                self.logger.error(f"Binary not found after package installation: {binary_name}")
                return False
            else:
                self.logger.error(f"Package installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Package installation error: {e}")
            return False
    
    def _install_via_git_clone(self, tool_name: str, config: Dict, target_dir: Path) -> bool:
        """Install tool via git clone"""
        try:
            url = config['url']
            clone_dir = self.downloads_dir / f"{tool_name}_clone"
            
            # Remove existing clone directory if it exists
            if clone_dir.exists():
                import shutil
                shutil.rmtree(clone_dir)
            
            self.logger.info(f"Cloning {tool_name} from {url}...")
            
            # Clone repository
            result = subprocess.run(
                ['git', 'clone', url, str(clone_dir)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                self.logger.error(f"Git clone failed: {result.stderr}")
                return False
            
            # Find and copy binary
            binary_name = config['binary']
            binary_path = None
            
            # Handle paths with subdirectories (e.g., "program/nikto.pl")
            if '/' in binary_name:
                potential_path = clone_dir / binary_name
                if potential_path.exists():
                    binary_path = potential_path
            else:
                # Search for main binary in all subdirectories
                for root, dirs, files in os.walk(clone_dir):
                    if binary_name in files:
                        binary_path = Path(root) / binary_name
                        break
                    # Also check for binary without extension
                    binary_stem = binary_name.split('.')[0]
                    if binary_stem in files:
                        binary_path = Path(root) / binary_stem
                        binary_name = binary_stem  # Update binary name
                        break
            
            if not binary_path or not binary_path.exists():
                self.logger.error(f"Binary not found after clone: {binary_name} in {clone_dir}")
                # List files for debugging
                self.logger.info("Available files:")
                for root, dirs, files in os.walk(clone_dir):
                    for file in files[:5]:  # Limit output
                        self.logger.info(f"  {Path(root).relative_to(clone_dir)}/{file}")
                return False
            
            # Copy entire directory structure to maintain dependencies
            tool_dir = target_dir / tool_name
            if tool_dir.exists():
                import shutil
                shutil.rmtree(tool_dir)
            
            import shutil
            shutil.copytree(clone_dir, tool_dir)
            
            # Create direct link to main binary in target directory
            final_binary_name = Path(binary_name).name  # Extract just the filename
            target_binary = target_dir / final_binary_name
            source_binary = tool_dir / binary_name  # Full path within tool directory
            
            if target_binary.exists() or target_binary.is_symlink():
                target_binary.unlink()
            
            # Create symlink
            target_binary.symlink_to(source_binary)
            
            # Make executable
            if os.name == 'posix':
                os.chmod(source_binary, 0o755)
            
            # Create wrapper script if specified
            if 'wrapper' in config:
                self._create_wrapper(target_dir, config, tool_name)
            
            self.logger.info(f"Successfully cloned and installed: {tool_name}")
            self.download_stats['downloaded'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Git clone installation error: {e}")
            return False
    
    def _install_via_download(self, tool_name: str, config: Dict, target_dir: Path) -> bool:
        """Install tool via direct download (original method)"""
        try:
            url = config['url']
            filename = urlparse(url).path.split('/')[-1]
            download_path = self.downloads_dir / filename
            
            # Download if not cached
            if not download_path.exists():
                checksum = config.get('checksum')
                if not self.download_file(url, download_path, checksum):
                    self.download_stats['failed'] += 1
                    return False
            
            # Extract
            extract_dir = self.downloads_dir / f"{tool_name}_{self.detect_platform()}"
            if not self.extract_archive(download_path, extract_dir):
                self.download_stats['failed'] += 1
                return False
            
            # Find and copy binary
            if not self._install_binary(extract_dir, target_dir, config, tool_name):
                self.download_stats['failed'] += 1
                return False
            
            self.download_stats['downloaded'] += 1
            self.logger.info(f"Successfully installed: {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download installation error: {e}")
            return False
    
    def install_priority_tools(self, priority: int = 1, platform: str = None) -> Dict:
        """Install all tools of specified priority level"""
        if platform is None:
            platform = self.detect_platform()
            
        priority_tools = [
            name for name, config in self.tools_config.items()
            if config.get('priority', 999) == priority
        ]
        
        results = {}
        self.logger.info(f"Installing Priority {priority} tools for {platform}...")
        self.logger.info(f"Tools to install: {', '.join(priority_tools)}")
        
        for tool_name in priority_tools:
            self.download_stats['total'] += 1
            results[tool_name] = self.install_tool(tool_name, platform)
            
        return results
    
    def install_all_tools(self, platform: str = None) -> Dict:
        """Install all configured tools"""
        if platform is None:
            platform = self.detect_platform()
            
        results = {}
        self.logger.info(f"Installing ALL tools for {platform}...")
        
        # Sort by priority
        sorted_tools = sorted(
            self.tools_config.items(),
            key=lambda x: x[1].get('priority', 999)
        )
        
        for tool_name, config in sorted_tools:
            self.download_stats['total'] += 1
            results[tool_name] = self.install_tool(tool_name, platform)
        
        return results
    
    def get_installation_summary(self) -> str:
        """Get installation summary"""
        total = self.download_stats['total']
        downloaded = self.download_stats['downloaded']
        failed = self.download_stats['failed']
        skipped = self.download_stats['skipped']
        
        success_rate = (downloaded / total * 100) if total > 0 else 0
        
        return f"""
📊 INSTALLATION SUMMARY
=======================
✅ Successfully installed: {downloaded}
⏭️  Already installed: {skipped}
❌ Failed installations: {failed}
📈 Success rate: {success_rate:.1f}%
📦 Total processed: {total}
"""

def main():
    """Main installation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LeZelote-Toolkit Binary Installer')
    parser.add_argument('--tool', help='Install specific tool')
    parser.add_argument('--priority', type=int, help='Install tools by priority (1=critical, 2=important)')
    parser.add_argument('--all', action='store_true', help='Install all tools')
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos'], 
                       help='Target platform (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    manager = BinaryDownloadManager()
    
    print("🔧 LeZelote-Toolkit Binary Installation Manager")
    print("=" * 50)
    
    try:
        if args.tool:
            # Install specific tool
            success = manager.install_tool(args.tool, args.platform)
            print(f"Tool {args.tool}: {'✅ Success' if success else '❌ Failed'}")
            
        elif args.priority:
            # Install by priority
            results = manager.install_priority_tools(args.priority, args.platform)
            for tool, success in results.items():
                print(f"{tool}: {'✅ Success' if success else '❌ Failed'}")
                
        elif args.all:
            # Install all tools
            results = manager.install_all_tools(args.platform)
            for tool, success in results.items():
                print(f"{tool}: {'✅ Success' if success else '❌ Failed'}")
                
        else:
            # Default: Install priority 1 tools
            print("Installing Priority 1 (Critical) tools...")
            results = manager.install_priority_tools(1, args.platform)
            for tool, success in results.items():
                print(f"{tool}: {'✅ Success' if success else '❌ Failed'}")
        
        print(manager.get_installation_summary())
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Installation interrupted by user")
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())