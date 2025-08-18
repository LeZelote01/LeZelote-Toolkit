#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Offline Update Manager
# =============================================================================
# Description: Handle offline updates using USB drives and update packages
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import yaml
import shutil
import hashlib
import zipfile
import tarfile
import logging
import argparse
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import sqlite3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/offline_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OfflineUpdateManager:
    """Manages offline updates for LeZelote-Toolkit"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.update_packages_dir = self.project_root / "update_packages"
        self.offline_cache_dir = self.project_root / "offline_cache"
        self.config_dir = self.project_root / "config"
        self.offline_config_file = self.config_dir / "offline_update_config.yaml"
        
        # Create directories
        for directory in [self.update_packages_dir, self.offline_cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def print_banner(self):
        """Print offline update banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   LeZelote-Toolkit Offline Update Manager                    ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def load_offline_config(self) -> Dict[str, Any]:
        """Load offline update configuration"""
        default_config = {
            'update_package_format': 'zip',
            'compression_level': 6,
            'include_binaries': True,
            'include_databases': True,
            'include_wordlists': True,
            'include_configs': True,
            'verification': {
                'enabled': True,
                'algorithm': 'sha256',
                'create_manifest': True
            },
            'usb_mount_points': [
                '/media/usb',
                '/mnt/usb',
                'E:\\',
                'F:\\',
                'G:\\'
            ],
            'auto_detect_usb': True,
            'backup_before_update': True,
            'rollback_enabled': True
        }
        
        if self.offline_config_file.exists():
            try:
                with open(self.offline_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                default_config.update(config)
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load offline config, using defaults: {e}")
        
        # Create default config file
        self.create_offline_config(default_config)
        return default_config
    
    def create_offline_config(self, config: Dict[str, Any]) -> None:
        """Create offline configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.offline_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"Created offline configuration: {self.offline_config_file}")
    
    def detect_usb_drives(self) -> List[Path]:
        """Detect available USB drives"""
        config = self.load_offline_config()
        usb_drives = []
        
        if not config.get('auto_detect_usb', True):
            return usb_drives
        
        # Check configured mount points
        mount_points = config.get('usb_mount_points', [])
        
        for mount_point in mount_points:
            mount_path = Path(mount_point)
            
            try:
                if mount_path.exists() and mount_path.is_dir():
                    # Check if it's actually a removable drive
                    if self.is_removable_drive(mount_path):
                        usb_drives.append(mount_path)
            except Exception as e:
                logger.debug(f"Error checking mount point {mount_point}: {e}")
        
        # On Linux, also check /media and /mnt
        if os.name == 'posix':
            for media_dir in [Path('/media'), Path('/mnt')]:
                if media_dir.exists():
                    try:
                        for user_dir in media_dir.iterdir():
                            if user_dir.is_dir():
                                for mount in user_dir.iterdir():
                                    if mount.is_dir() and self.is_removable_drive(mount):
                                        usb_drives.append(mount)
                    except Exception as e:
                        logger.debug(f"Error scanning {media_dir}: {e}")
        
        logger.info(f"Detected {len(usb_drives)} USB drives: {[str(d) for d in usb_drives]}")
        return usb_drives
    
    def is_removable_drive(self, path: Path) -> bool:
        """Check if path is on a removable drive"""
        try:
            # On Linux, check /proc/mounts
            if os.name == 'posix':
                with open('/proc/mounts', 'r') as f:
                    mounts = f.read()
                
                for line in mounts.splitlines():
                    if str(path) in line and ('usb' in line or 'removable' in line):
                        return True
            
            # On Windows, check drive type
            elif os.name == 'nt':
                import ctypes
                drive = str(path)[:3]  # Get drive letter (e.g., "E:\\")
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                return drive_type == 2  # DRIVE_REMOVABLE
            
            # Additional check: see if we can write to it
            test_file = path / '.lezelote_test'
            try:
                test_file.write_text('test')
                test_file.unlink()
                return True
            except:
                return False
            
        except Exception:
            return False
    
    def calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash"""
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def create_update_package(self, package_name: str, include_components: Optional[List[str]] = None) -> Optional[Path]:
        """Create offline update package"""
        logger.info(f"Creating offline update package: {package_name}")
        
        config = self.load_offline_config()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_filename = f"{package_name}_{timestamp}.{config['update_package_format']}"
        package_path = self.update_packages_dir / package_filename
        
        # Determine what to include
        if include_components is None:
            include_components = []
            if config.get('include_binaries', True):
                include_components.append('binaries')
            if config.get('include_databases', True):
                include_components.append('databases')
            if config.get('include_wordlists', True):
                include_components.append('wordlists')
            if config.get('include_configs', True):
                include_components.append('configs')
        
        # Create temporary directory for packaging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            package_content_dir = temp_path / "lezelote_update"
            package_content_dir.mkdir()
            
            manifest = {
                'package_name': package_name,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': '1.0.0',
                'components': include_components,
                'files': {}
            }
            
            # Copy components based on selection
            files_copied = 0
            
            if 'binaries' in include_components:
                files_copied += self.copy_component('binaries', package_content_dir, manifest)
            
            if 'databases' in include_components:
                files_copied += self.copy_component('databases', package_content_dir, manifest)
            
            if 'wordlists' in include_components:
                files_copied += self.copy_component('wordlists', package_content_dir, manifest)
            
            if 'configs' in include_components:
                files_copied += self.copy_component('configs', package_content_dir, manifest)
            
            # Create manifest file
            manifest_file = package_content_dir / "update_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Create the package archive
            try:
                if config['update_package_format'] == 'zip':
                    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED,
                                       compresslevel=config.get('compression_level', 6)) as zipf:
                        for file_path in package_content_dir.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(package_content_dir)
                                zipf.write(file_path, arcname)
                
                elif config['update_package_format'] == 'tar':
                    with tarfile.open(package_path, 'w:gz') as tarf:
                        tarf.add(package_content_dir, arcname='lezelote_update')
                
                else:
                    logger.error(f"Unsupported package format: {config['update_package_format']}")
                    return None
                
                logger.info(f"Created update package: {package_path} ({files_copied} files)")
                
                # Create checksum file if verification is enabled
                if config.get('verification', {}).get('enabled', True):
                    checksum = self.calculate_file_hash(package_path, 
                                                      config.get('verification', {}).get('algorithm', 'sha256'))
                    checksum_file = package_path.with_suffix(package_path.suffix + '.sha256')
                    checksum_file.write_text(f"{checksum}  {package_path.name}\n")
                    logger.info(f"Created checksum file: {checksum_file}")
                
                return package_path
                
            except Exception as e:
                logger.error(f"Failed to create update package: {e}")
                return None
    
    def copy_component(self, component: str, dest_dir: Path, manifest: Dict[str, Any]) -> int:
        """Copy component files to package directory"""
        files_copied = 0
        
        try:
            if component == 'binaries':
                source_dir = self.project_root / "tools" / "binaries"
                if source_dir.exists():
                    dest_component_dir = dest_dir / "tools" / "binaries"
                    shutil.copytree(source_dir, dest_component_dir)
                    files_copied = sum(1 for _ in dest_component_dir.rglob('*') if _.is_file())
                    
            elif component == 'databases':
                source_dir = self.project_root / "data" / "databases"
                if source_dir.exists():
                    dest_component_dir = dest_dir / "data" / "databases"
                    shutil.copytree(source_dir, dest_component_dir)
                    files_copied = sum(1 for _ in dest_component_dir.rglob('*') if _.is_file())
                    
            elif component == 'wordlists':
                source_dir = self.project_root / "data" / "wordlists"
                if source_dir.exists():
                    dest_component_dir = dest_dir / "data" / "wordlists"
                    # Only copy essential wordlists to reduce size
                    dest_component_dir.mkdir(parents=True)
                    essential_lists = ['passwords/rockyou.txt', 'directories/common.txt', 'dns/subdomains.txt']
                    for essential in essential_lists:
                        source_file = source_dir / essential
                        if source_file.exists():
                            dest_file = dest_component_dir / essential
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(source_file, dest_file)
                            files_copied += 1
                            
            elif component == 'configs':
                source_dir = self.project_root / "config"
                if source_dir.exists():
                    dest_component_dir = dest_dir / "config"
                    shutil.copytree(source_dir, dest_component_dir)
                    files_copied = sum(1 for _ in dest_component_dir.rglob('*') if _.is_file())
            
            # Update manifest with file information
            if files_copied > 0:
                manifest['files'][component] = {
                    'count': files_copied,
                    'copied_at': datetime.now(timezone.utc).isoformat()
                }
            
            logger.info(f"Copied {component}: {files_copied} files")
            
        except Exception as e:
            logger.error(f"Failed to copy component {component}: {e}")
        
        return files_copied
    
    def find_update_packages(self, search_paths: Optional[List[Path]] = None) -> List[Path]:
        """Find available update packages"""
        if search_paths is None:
            search_paths = []
            # Check USB drives
            search_paths.extend(self.detect_usb_drives())
            # Check local update packages directory
            search_paths.append(self.update_packages_dir)
        
        found_packages = []
        
        for search_path in search_paths:
            try:
                if search_path.exists() and search_path.is_dir():
                    # Look for update packages
                    for pattern in ['*.zip', '*.tar.gz', '*.tar']:
                        for package_file in search_path.glob(pattern):
                            if self.is_valid_update_package(package_file):
                                found_packages.append(package_file)
            except Exception as e:
                logger.debug(f"Error searching {search_path}: {e}")
        
        logger.info(f"Found {len(found_packages)} update packages")
        return found_packages
    
    def is_valid_update_package(self, package_path: Path) -> bool:
        """Check if file is a valid update package"""
        try:
            if package_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(package_path, 'r') as zipf:
                    # Check if manifest exists
                    try:
                        manifest_content = zipf.read('lezelote_update/update_manifest.json')
                        manifest = json.loads(manifest_content.decode('utf-8'))
                        return 'package_name' in manifest and 'components' in manifest
                    except KeyError:
                        return False
            
            elif package_path.suffix.lower() in ['.tar', '.gz']:
                with tarfile.open(package_path, 'r:*') as tarf:
                    # Check if manifest exists
                    try:
                        manifest_member = tarf.getmember('lezelote_update/update_manifest.json')
                        manifest_content = tarf.extractfile(manifest_member).read()
                        manifest = json.loads(manifest_content.decode('utf-8'))
                        return 'package_name' in manifest and 'components' in manifest
                    except KeyError:
                        return False
            
            return False
            
        except Exception as e:
            logger.debug(f"Error validating package {package_path}: {e}")
            return False
    
    def verify_package_integrity(self, package_path: Path) -> bool:
        """Verify package integrity using checksum"""
        config = self.load_offline_config()
        verification_config = config.get('verification', {})
        
        if not verification_config.get('enabled', True):
            return True
        
        algorithm = verification_config.get('algorithm', 'sha256')
        checksum_file = package_path.with_suffix(package_path.suffix + f'.{algorithm}')
        
        if not checksum_file.exists():
            logger.warning(f"Checksum file not found: {checksum_file}")
            return False
        
        try:
            # Read expected checksum
            checksum_content = checksum_file.read_text().strip()
            expected_hash = checksum_content.split()[0]
            
            # Calculate actual checksum
            actual_hash = self.calculate_file_hash(package_path, algorithm)
            
            if expected_hash.lower() == actual_hash.lower():
                logger.info(f"Package integrity verified: {package_path}")
                return True
            else:
                logger.error(f"Package integrity check failed: {package_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify package integrity: {e}")
            return False
    
    def apply_offline_update(self, package_path: Path) -> bool:
        """Apply offline update from package"""
        logger.info(f"Applying offline update: {package_path}")
        
        # Verify package integrity
        if not self.verify_package_integrity(package_path):
            logger.error("Package integrity verification failed")
            return False
        
        # Create backup if enabled
        config = self.load_offline_config()
        if config.get('backup_before_update', True):
            if not self.create_backup_before_update():
                logger.warning("Failed to create backup, continuing anyway...")
        
        # Extract and apply update
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Extract package
                if package_path.suffix.lower() == '.zip':
                    with zipfile.ZipFile(package_path, 'r') as zipf:
                        zipf.extractall(temp_path)
                
                elif package_path.suffix.lower() in ['.tar', '.gz']:
                    with tarfile.open(package_path, 'r:*') as tarf:
                        tarf.extractall(temp_path)
                
                else:
                    logger.error(f"Unsupported package format: {package_path}")
                    return False
                
                # Read manifest
                manifest_file = temp_path / "lezelote_update" / "update_manifest.json"
                if not manifest_file.exists():
                    logger.error("Update manifest not found in package")
                    return False
                
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                logger.info(f"Applying update package: {manifest['package_name']}")
                logger.info(f"Components: {', '.join(manifest['components'])}")
                
                # Apply each component
                update_content_dir = temp_path / "lezelote_update"
                
                for component in manifest['components']:
                    if not self.apply_component_update(component, update_content_dir):
                        logger.error(f"Failed to apply component: {component}")
                        return False
                
                logger.info("Offline update applied successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to apply offline update: {e}")
                return False
    
    def apply_component_update(self, component: str, source_dir: Path) -> bool:
        """Apply update for a specific component"""
        try:
            if component == 'binaries':
                source_comp_dir = source_dir / "tools" / "binaries"
                dest_comp_dir = self.project_root / "tools" / "binaries"
                
            elif component == 'databases':
                source_comp_dir = source_dir / "data" / "databases"
                dest_comp_dir = self.project_root / "data" / "databases"
                
            elif component == 'wordlists':
                source_comp_dir = source_dir / "data" / "wordlists"
                dest_comp_dir = self.project_root / "data" / "wordlists"
                
            elif component == 'configs':
                source_comp_dir = source_dir / "config"
                dest_comp_dir = self.project_root / "config"
                
            else:
                logger.warning(f"Unknown component: {component}")
                return True
            
            if not source_comp_dir.exists():
                logger.warning(f"Component source directory not found: {source_comp_dir}")
                return True
            
            # Copy files
            dest_comp_dir.parent.mkdir(parents=True, exist_ok=True)
            
            if dest_comp_dir.exists():
                # Merge/overwrite existing files
                for source_file in source_comp_dir.rglob('*'):
                    if source_file.is_file():
                        relative_path = source_file.relative_to(source_comp_dir)
                        dest_file = dest_comp_dir / relative_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
            else:
                # Copy entire directory
                shutil.copytree(source_comp_dir, dest_comp_dir)
            
            logger.info(f"Applied component update: {component}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply component update {component}: {e}")
            return False
    
    def create_backup_before_update(self) -> bool:
        """Create backup before applying update"""
        try:
            backup_dir = self.project_root / "backups" / "pre_offline_update"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / timestamp
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup critical directories
            backup_dirs = ['config', 'data/databases', 'tools/binaries']
            
            for backup_dir_name in backup_dirs:
                source_dir = self.project_root / backup_dir_name
                if source_dir.exists():
                    dest_dir = backup_path / backup_dir_name
                    shutil.copytree(source_dir, dest_dir)
            
            logger.info(f"Created backup before update: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def list_update_packages(self) -> None:
        """List available update packages"""
        packages = self.find_update_packages()
        
        if not packages:
            print("No update packages found")
            return
        
        print(f"\nFound {len(packages)} update packages:")
        print("-" * 80)
        
        for i, package in enumerate(packages, 1):
            try:
                size = package.stat().st_size
                size_mb = size / (1024 * 1024)
                modified = datetime.fromtimestamp(package.stat().st_mtime)
                
                print(f"{i}. {package.name}")
                print(f"   Path: {package}")
                print(f"   Size: {size_mb:.1f} MB")
                print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Try to read manifest for more details
                try:
                    if self.is_valid_update_package(package):
                        print(f"   Status: ✓ Valid update package")
                    else:
                        print(f"   Status: ✗ Invalid update package")
                except:
                    print(f"   Status: ? Unknown")
                
                print()
                
            except Exception as e:
                print(f"{i}. {package.name} - Error reading details: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Offline Update Manager")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create package command
    create_parser = subparsers.add_parser('create', help='Create update package')
    create_parser.add_argument('--name', required=True, help='Package name')
    create_parser.add_argument('--components', nargs='*', 
                              choices=['binaries', 'databases', 'wordlists', 'configs'],
                              help='Components to include')
    
    # Apply update command
    apply_parser = subparsers.add_parser('apply', help='Apply update package')
    apply_parser.add_argument('--package', required=True, help='Path to update package')
    
    # List packages command
    list_parser = subparsers.add_parser('list', help='List available update packages')
    
    # Detect USB command
    usb_parser = subparsers.add_parser('detect-usb', help='Detect USB drives')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create offline update manager
    manager = OfflineUpdateManager(args.project_root)
    manager.print_banner()
    
    try:
        if args.command == 'create':
            package_path = manager.create_update_package(args.name, args.components)
            if package_path:
                print(f"✅ Update package created: {package_path}")
                sys.exit(0)
            else:
                print("❌ Failed to create update package")
                sys.exit(1)
        
        elif args.command == 'apply':
            package_path = Path(args.package)
            if not package_path.exists():
                print(f"❌ Package not found: {package_path}")
                sys.exit(1)
            
            if manager.apply_offline_update(package_path):
                print("✅ Offline update applied successfully")
                sys.exit(0)
            else:
                print("❌ Failed to apply offline update")
                sys.exit(1)
        
        elif args.command == 'list':
            manager.list_update_packages()
        
        elif args.command == 'detect-usb':
            usb_drives = manager.detect_usb_drives()
            if usb_drives:
                print(f"Detected USB drives:")
                for drive in usb_drives:
                    print(f"  - {drive}")
            else:
                print("No USB drives detected")
        
    except KeyboardInterrupt:
        logger.info("Offline update interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()