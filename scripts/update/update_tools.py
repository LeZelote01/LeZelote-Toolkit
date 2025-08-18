#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Tools Update Manager
# =============================================================================
# Description: Automated updating of security tools and binaries
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import yaml
import platform
import requests
import subprocess
import logging
import argparse
import shutil
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import zipfile
import tarfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/tools_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ToolUpdateManager:
    """Manages automated updates for security tools"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.tools_dir = self.project_root / "tools"
        self.binaries_dir = self.tools_dir / "binaries"
        self.config_dir = self.project_root / "config"
        self.update_config_file = self.config_dir / "update_config.yaml"
        self.tools_registry_file = self.config_dir / "tools_registry.json"
        self.system_info = self.get_system_info()
        
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Normalize architecture names
        if machine in ['x86_64', 'amd64']:
            machine = 'x64'
        elif machine in ['i386', 'i686']:
            machine = 'x86'
        elif machine in ['aarch64', 'arm64']:
            machine = 'arm64'
        
        return {
            'system': system,
            'machine': machine,
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
    
    def print_banner(self):
        """Print update banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     LeZelote-Toolkit Tools Update Manager                    ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def load_update_config(self) -> Dict[str, Any]:
        """Load update configuration"""
        default_config = {
            'update_servers': [
                'https://api.github.com',
                'https://github.com'
            ],
            'tools': {
                'nmap': {
                    'type': 'system_package',
                    'update_method': 'package_manager',
                    'auto_update': True
                },
                'masscan': {
                    'type': 'github_release',
                    'repo': 'robertdavidgraham/masscan',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'masscan-*-linux.tgz',
                        'windows': 'masscan-*-win64.zip',
                        'darwin': 'masscan-*-macos.zip'
                    }
                },
                'rustscan': {
                    'type': 'github_release',
                    'repo': 'RustScan/RustScan',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'rustscan_*_amd64.deb',
                        'windows': 'rustscan_*_x86_64-pc-windows-msvc.zip',
                        'darwin': 'rustscan_*_x86_64-apple-darwin.zip'
                    }
                },
                'gobuster': {
                    'type': 'github_release', 
                    'repo': 'OJ/gobuster',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'gobuster-linux-amd64.tar.gz',
                        'windows': 'gobuster-windows-amd64.zip',
                        'darwin': 'gobuster-darwin-amd64.tar.gz'
                    }
                },
                'ffuf': {
                    'type': 'github_release',
                    'repo': 'ffuf/ffuf',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'ffuf_*_linux_amd64.tar.gz',
                        'windows': 'ffuf_*_windows_amd64.zip', 
                        'darwin': 'ffuf_*_darwin_amd64.tar.gz'
                    }
                },
                'nuclei': {
                    'type': 'github_release',
                    'repo': 'projectdiscovery/nuclei',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'nuclei_*_linux_amd64.zip',
                        'windows': 'nuclei_*_windows_amd64.zip',
                        'darwin': 'nuclei_*_darwin_amd64.zip'
                    }
                },
                'subfinder': {
                    'type': 'github_release',
                    'repo': 'projectdiscovery/subfinder',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'subfinder_*_linux_amd64.zip',
                        'windows': 'subfinder_*_windows_amd64.zip',
                        'darwin': 'subfinder_*_darwin_amd64.zip'
                    }
                },
                'httpx': {
                    'type': 'github_release',
                    'repo': 'projectdiscovery/httpx',
                    'auto_update': True,
                    'asset_patterns': {
                        'linux': 'httpx_*_linux_amd64.zip',
                        'windows': 'httpx_*_windows_amd64.zip',
                        'darwin': 'httpx_*_darwin_amd64.zip'
                    }
                }
            },
            'update_interval': 86400,  # 24 hours
            'auto_backup': True,
            'verify_signatures': True,
            'max_concurrent_downloads': 3,
            'timeout': 300,  # 5 minutes
            'retry_attempts': 3
        }
        
        if self.update_config_file.exists():
            try:
                with open(self.update_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load update config, using defaults: {e}")
        
        # Create default config file
        self.create_update_config(default_config)
        return default_config
    
    def create_update_config(self, config: Dict[str, Any]) -> None:
        """Create update configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.update_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"Created update configuration: {self.update_config_file}")
    
    def load_tools_registry(self) -> Dict[str, Any]:
        """Load tools registry with current versions"""
        default_registry = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'tools': {}
        }
        
        if self.tools_registry_file.exists():
            try:
                with open(self.tools_registry_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load tools registry: {e}")
        
        return default_registry
    
    def save_tools_registry(self, registry: Dict[str, Any]) -> None:
        """Save tools registry"""
        registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        with open(self.tools_registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def check_github_releases(self, repo: str) -> List[Dict[str, Any]]:
        """Check GitHub releases for a repository"""
        url = f"https://api.github.com/repos/{repo}/releases"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            releases = response.json()
            return releases[:10]  # Get latest 10 releases
            
        except requests.RequestException as e:
            logger.error(f"Failed to check releases for {repo}: {e}")
            return []
    
    def get_latest_version_info(self, tool_name: str, tool_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get latest version information for a tool"""
        if tool_config['type'] == 'github_release':
            releases = self.check_github_releases(tool_config['repo'])
            
            if not releases:
                return None
            
            # Find the latest stable release (not pre-release)
            latest_release = None
            for release in releases:
                if not release.get('prerelease', False) and not release.get('draft', False):
                    latest_release = release
                    break
            
            if not latest_release:
                return None
            
            return {
                'version': latest_release['tag_name'],
                'published_at': latest_release['published_at'],
                'assets': latest_release.get('assets', []),
                'download_url': latest_release['html_url']
            }
        
        elif tool_config['type'] == 'system_package':
            # For system packages, we'll rely on package manager
            return self.check_system_package_version(tool_name)
        
        return None
    
    def check_system_package_version(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Check system package version"""
        try:
            if self.system_info['system'] == 'linux':
                # Try different package managers
                if shutil.which('apt'):
                    result = subprocess.run(['apt', 'list', '--upgradable', tool_name], 
                                          capture_output=True, text=True)
                    if tool_name in result.stdout:
                        return {'update_available': True, 'method': 'apt'}
                
                elif shutil.which('yum'):
                    result = subprocess.run(['yum', 'check-update', tool_name], 
                                          capture_output=True, text=True)
                    if result.returncode == 100:  # Updates available
                        return {'update_available': True, 'method': 'yum'}
                
                elif shutil.which('pacman'):
                    result = subprocess.run(['pacman', '-Qu', tool_name], 
                                          capture_output=True, text=True)
                    if tool_name in result.stdout:
                        return {'update_available': True, 'method': 'pacman'}
            
            elif self.system_info['system'] == 'darwin':
                if shutil.which('brew'):
                    result = subprocess.run(['brew', 'outdated', tool_name], 
                                          capture_output=True, text=True)
                    if tool_name in result.stdout:
                        return {'update_available': True, 'method': 'brew'}
            
            return {'update_available': False}
            
        except Exception as e:
            logger.warning(f"Failed to check system package version for {tool_name}: {e}")
            return None
    
    def find_matching_asset(self, assets: List[Dict[str, Any]], pattern: str) -> Optional[Dict[str, Any]]:
        """Find matching asset based on pattern"""
        import fnmatch
        
        for asset in assets:
            asset_name = asset.get('name', '')
            if fnmatch.fnmatch(asset_name.lower(), pattern.lower()):
                return asset
        
        return None
    
    def download_file(self, url: str, destination: Path, expected_size: Optional[int] = None) -> bool:
        """Download file with progress tracking"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rDownloading... {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            
            # Verify file size if expected
            if expected_size and destination.stat().st_size != expected_size:
                logger.warning(f"Downloaded file size mismatch: expected {expected_size}, got {destination.stat().st_size}")
                return False
            
            logger.info(f"Successfully downloaded: {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def verify_file_checksum(self, file_path: Path, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """Verify file checksum"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            calculated_hash = hash_obj.hexdigest()
            return calculated_hash.lower() == expected_hash.lower()
            
        except Exception as e:
            logger.error(f"Failed to verify checksum for {file_path}: {e}")
            return False
    
    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract archive file"""
        try:
            extract_to.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            
            elif archive_path.suffix.lower() in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            
            else:
                logger.warning(f"Unsupported archive format: {archive_path}")
                return False
            
            logger.info(f"Extracted {archive_path} to {extract_to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract {archive_path}: {e}")
            return False
    
    def backup_current_tool(self, tool_name: str) -> Optional[Path]:
        """Create backup of current tool version"""
        tool_path = self.find_tool_executable(tool_name)
        if not tool_path or not tool_path.exists():
            logger.info(f"No existing installation found for {tool_name}")
            return None
        
        backup_dir = self.project_root / "backups" / "tools"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{tool_name}_{timestamp}"
        
        try:
            if tool_path.is_file():
                shutil.copy2(tool_path, backup_path)
            else:
                shutil.copytree(tool_path, backup_path)
            
            logger.info(f"Backed up {tool_name} to {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup {tool_name}: {e}")
            return None
    
    def find_tool_executable(self, tool_name: str) -> Optional[Path]:
        """Find tool executable path"""
        # Check in project binaries directory first
        system_dir = self.binaries_dir / self.system_info['system']
        if system_dir.exists():
            for ext in ['', '.exe']:
                tool_path = system_dir / f"{tool_name}{ext}"
                if tool_path.exists():
                    return tool_path
        
        # Check system PATH
        system_path = shutil.which(tool_name)
        if system_path:
            return Path(system_path)
        
        return None
    
    def install_tool_update(self, tool_name: str, tool_config: Dict[str, Any], version_info: Dict[str, Any]) -> bool:
        """Install tool update"""
        logger.info(f"Installing update for {tool_name}...")
        
        if tool_config['type'] == 'system_package':
            return self.update_system_package(tool_name, version_info)
        
        elif tool_config['type'] == 'github_release':
            return self.update_github_tool(tool_name, tool_config, version_info)
        
        return False
    
    def update_system_package(self, tool_name: str, version_info: Dict[str, Any]) -> bool:
        """Update system package"""
        method = version_info.get('method')
        
        try:
            if method == 'apt':
                result = subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
                result = subprocess.run(['sudo', 'apt', 'install', '-y', tool_name], 
                                      check=True, capture_output=True)
            
            elif method == 'yum':
                result = subprocess.run(['sudo', 'yum', 'update', '-y', tool_name], 
                                      check=True, capture_output=True)
            
            elif method == 'pacman':
                result = subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', tool_name], 
                                      check=True, capture_output=True)
            
            elif method == 'brew':
                result = subprocess.run(['brew', 'upgrade', tool_name], 
                                      check=True, capture_output=True)
            
            else:
                logger.error(f"Unsupported package manager: {method}")
                return False
            
            logger.info(f"Successfully updated {tool_name} via {method}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update {tool_name} via {method}: {e.stderr.decode()}")
            return False
    
    def update_github_tool(self, tool_name: str, tool_config: Dict[str, Any], version_info: Dict[str, Any]) -> bool:
        """Update GitHub-based tool"""
        # Find appropriate asset for our system
        system = self.system_info['system']
        asset_patterns = tool_config.get('asset_patterns', {})
        
        if system not in asset_patterns:
            logger.error(f"No asset pattern defined for {system} in {tool_name}")
            return False
        
        pattern = asset_patterns[system]
        asset = self.find_matching_asset(version_info['assets'], pattern)
        
        if not asset:
            logger.error(f"No matching asset found for {tool_name} on {system}")
            return False
        
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            download_path = temp_path / asset['name']
            
            # Download the asset
            if not self.download_file(asset['browser_download_url'], download_path, asset.get('size')):
                return False
            
            # Backup current tool if it exists
            if tool_config.get('auto_backup', True):
                self.backup_current_tool(tool_name)
            
            # Extract if it's an archive
            if download_path.suffix.lower() in ['.zip', '.tar', '.gz', '.tgz']:
                extract_dir = temp_path / 'extracted'
                if not self.extract_archive(download_path, extract_dir):
                    return False
                
                # Find the executable in extracted files
                executable_path = self.find_executable_in_directory(extract_dir, tool_name)
                if not executable_path:
                    logger.error(f"Could not find executable for {tool_name} in extracted files")
                    return False
                
                source_path = executable_path
            else:
                source_path = download_path
            
            # Install to binaries directory
            system_bin_dir = self.binaries_dir / self.system_info['system']
            system_bin_dir.mkdir(parents=True, exist_ok=True)
            
            extension = '.exe' if self.system_info['system'] == 'windows' else ''
            target_path = system_bin_dir / f"{tool_name}{extension}"
            
            try:
                shutil.copy2(source_path, target_path)
                target_path.chmod(0o755)  # Make executable
                
                logger.info(f"Successfully installed {tool_name} v{version_info['version']} to {target_path}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to install {tool_name}: {e}")
                return False
    
    def find_executable_in_directory(self, directory: Path, tool_name: str) -> Optional[Path]:
        """Find executable file in extracted directory"""
        # Common executable extensions
        extensions = ['', '.exe'] if self.system_info['system'] == 'windows' else ['']
        
        # Search for exact match first
        for ext in extensions:
            exact_match = directory / f"{tool_name}{ext}"
            if exact_match.exists() and exact_match.is_file():
                return exact_match
        
        # Search recursively for files with tool name
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                for ext in extensions:
                    if file_path.name.lower() == f"{tool_name}{ext}".lower():
                        return file_path
                    # Also check if filename contains tool name
                    if tool_name.lower() in file_path.name.lower() and file_path.suffix.lower() in ['', '.exe']:
                        return file_path
        
        return None
    
    def update_single_tool(self, tool_name: str) -> bool:
        """Update a single tool"""
        logger.info(f"Checking updates for {tool_name}...")
        
        config = self.load_update_config()
        if tool_name not in config['tools']:
            logger.error(f"Tool {tool_name} not found in configuration")
            return False
        
        tool_config = config['tools'][tool_name]
        
        # Get current version info
        registry = self.load_tools_registry()
        current_version = registry['tools'].get(tool_name, {}).get('version', 'unknown')
        
        # Check for latest version
        latest_info = self.get_latest_version_info(tool_name, tool_config)
        if not latest_info:
            logger.warning(f"Could not get version information for {tool_name}")
            return False
        
        # Check if update is needed
        if tool_config['type'] == 'github_release':
            latest_version = latest_info['version']
            if current_version == latest_version:
                logger.info(f"{tool_name} is already up to date (v{current_version})")
                return True
            
            logger.info(f"Update available for {tool_name}: {current_version} -> {latest_version}")
        
        elif tool_config['type'] == 'system_package':
            if not latest_info.get('update_available', False):
                logger.info(f"{tool_name} is already up to date")
                return True
            
            logger.info(f"Update available for {tool_name}")
        
        # Perform update
        if self.install_tool_update(tool_name, tool_config, latest_info):
            # Update registry
            if tool_config['type'] == 'github_release':
                registry['tools'][tool_name] = {
                    'version': latest_info['version'],
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'type': tool_config['type']
                }
                self.save_tools_registry(registry)
            
            logger.info(f"Successfully updated {tool_name}")
            return True
        else:
            logger.error(f"Failed to update {tool_name}")
            return False
    
    def update_all_tools(self) -> Dict[str, bool]:
        """Update all configured tools"""
        logger.info("Starting update for all tools...")
        
        config = self.load_update_config()
        results = {}
        
        for tool_name, tool_config in config['tools'].items():
            if tool_config.get('auto_update', True):
                try:
                    results[tool_name] = self.update_single_tool(tool_name)
                except Exception as e:
                    logger.error(f"Error updating {tool_name}: {e}")
                    results[tool_name] = False
            else:
                logger.info(f"Skipping {tool_name} (auto_update disabled)")
                results[tool_name] = None
        
        # Print summary
        successful = sum(1 for result in results.values() if result is True)
        failed = sum(1 for result in results.values() if result is False)
        skipped = sum(1 for result in results.values() if result is None)
        
        logger.info(f"Update summary: {successful} successful, {failed} failed, {skipped} skipped")
        
        return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Tools Update Manager")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--tool', help='Update specific tool')
    parser.add_argument('--all', action='store_true', help='Update all tools')
    parser.add_argument('--check-only', action='store_true', help='Only check for updates')
    parser.add_argument('--force', action='store_true', help='Force update even if up to date')
    
    args = parser.parse_args()
    
    if not args.tool and not args.all:
        parser.print_help()
        sys.exit(1)
    
    # Create update manager
    manager = ToolUpdateManager(args.project_root)
    manager.print_banner()
    
    try:
        if args.tool:
            success = manager.update_single_tool(args.tool)
            sys.exit(0 if success else 1)
        
        elif args.all:
            results = manager.update_all_tools()
            failed_count = sum(1 for result in results.values() if result is False)
            sys.exit(0 if failed_count == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()