#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Patch Application Manager
# =============================================================================
# Description: Apply security patches and hotfixes to the toolkit
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
import tempfile
import subprocess
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import sqlite3
import zipfile
import tarfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/patch_application.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PatchManager:
    """Manages application of security patches and hotfixes"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.patches_dir = self.project_root / "patches"
        self.applied_patches_dir = self.patches_dir / "applied"
        self.config_dir = self.project_root / "config"
        self.patch_config_file = self.config_dir / "patch_config.yaml"
        self.patch_db_file = self.project_root / "data" / "databases" / "patches.db"
        
        # Create directories
        for directory in [self.patches_dir, self.applied_patches_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def print_banner(self):
        """Print patch manager banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LeZelote-Toolkit Patch Application Manager               ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def load_patch_config(self) -> Dict[str, Any]:
        """Load patch configuration"""
        default_config = {
            'patch_sources': {
                'official_repo': {
                    'enabled': True,
                    'url': 'https://api.github.com/repos/LeZelote01/LeZelote-Toolkit-Patches/contents',
                    'verify_signatures': True
                }
            },
            'auto_apply': {
                'security_patches': True,
                'hotfixes': True,
                'feature_updates': False
            },
            'backup': {
                'enabled': True,
                'backup_dir': 'backups/pre_patch',
                'keep_versions': 10
            },
            'verification': {
                'enabled': True,
                'test_after_patch': True,
                'rollback_on_failure': True
            },
            'notification': {
                'enabled': True,
                'log_file': 'logs/patch_notifications.log'
            }
        }
        
        if self.patch_config_file.exists():
            try:
                with open(self.patch_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                default_config.update(config)
                return default_config
            except Exception as e:
                logger.warning(f"Failed to load patch config, using defaults: {e}")
        
        # Create default config file
        self.create_patch_config(default_config)
        return default_config
    
    def create_patch_config(self, config: Dict[str, Any]) -> None:
        """Create patch configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.patch_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        logger.info(f"Created patch configuration: {self.patch_config_file}")
    
    def init_patch_database(self) -> None:
        """Initialize patch tracking database"""
        self.patch_db_file.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.patch_db_file)
        cursor = conn.cursor()
        
        # Create patches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                version TEXT,
                description TEXT,
                patch_type TEXT,
                severity TEXT,
                status TEXT DEFAULT 'pending',
                applied_at TIMESTAMP,
                rollback_info TEXT,
                checksum TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create patch files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patch_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patch_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_checksum TEXT,
                patched_checksum TEXT,
                backup_path TEXT,
                action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patch_id) REFERENCES patches (patch_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patch_id ON patches(patch_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patch_status ON patches(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_patch_type ON patches(patch_type)')
        
        conn.commit()
        conn.close()
        
        logger.info("Patch database initialized")
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def parse_patch_file(self, patch_file: Path) -> Dict[str, Any]:
        """Parse patch file and extract metadata"""
        try:
            if patch_file.suffix.lower() == '.json':
                with open(patch_file, 'r') as f:
                    patch_data = json.load(f)
            elif patch_file.suffix.lower() in ['.yaml', '.yml']:
                with open(patch_file, 'r') as f:
                    patch_data = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported patch file format: {patch_file}")
                return {}
            
            # Validate required fields
            required_fields = ['patch_id', 'name', 'version', 'patch_type', 'files']
            for field in required_fields:
                if field not in patch_data:
                    logger.error(f"Missing required field '{field}' in patch file")
                    return {}
            
            return patch_data
            
        except Exception as e:
            logger.error(f"Failed to parse patch file {patch_file}: {e}")
            return {}
    
    def validate_patch(self, patch_data: Dict[str, Any]) -> bool:
        """Validate patch data and requirements"""
        try:
            # Check patch ID format
            patch_id = patch_data.get('patch_id', '')
            if not patch_id or not patch_id.startswith('LZT-'):
                logger.error(f"Invalid patch ID format: {patch_id}")
                return False
            
            # Check version compatibility
            toolkit_version = self.get_toolkit_version()
            min_version = patch_data.get('min_version')
            max_version = patch_data.get('max_version')
            
            if min_version and self.compare_versions(toolkit_version, min_version) < 0:
                logger.error(f"Patch requires minimum version {min_version}, current: {toolkit_version}")
                return False
            
            if max_version and self.compare_versions(toolkit_version, max_version) > 0:
                logger.error(f"Patch requires maximum version {max_version}, current: {toolkit_version}")
                return False
            
            # Check file paths exist
            files = patch_data.get('files', [])
            for file_info in files:
                target_path = self.project_root / file_info['path']
                if file_info.get('action') != 'create' and not target_path.exists():
                    logger.error(f"Target file does not exist: {target_path}")
                    return False
            
            # Check dependencies
            dependencies = patch_data.get('dependencies', [])
            for dep_patch_id in dependencies:
                if not self.is_patch_applied(dep_patch_id):
                    logger.error(f"Required dependency patch not applied: {dep_patch_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Patch validation failed: {e}")
            return False
    
    def get_toolkit_version(self) -> str:
        """Get current toolkit version"""
        version_file = self.project_root / "VERSION"
        if version_file.exists():
            try:
                return version_file.read_text().strip()
            except Exception:
                pass
        return "1.0.0"
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings (-1: v1 < v2, 0: v1 == v2, 1: v1 > v2)"""
        try:
            import packaging.version
            v1 = packaging.version.parse(version1)
            v2 = packaging.version.parse(version2)
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except Exception:
            # Fallback to string comparison
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0
    
    def is_patch_applied(self, patch_id: str) -> bool:
        """Check if patch is already applied"""
        conn = sqlite3.connect(self.patch_db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT status FROM patches WHERE patch_id = ?', (patch_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0] == 'applied'
    
    def backup_files(self, patch_data: Dict[str, Any]) -> Optional[Path]:
        """Create backup of files that will be modified"""
        config = self.load_patch_config()
        backup_config = config.get('backup', {})
        
        if not backup_config.get('enabled', True):
            return None
        
        patch_id = patch_data['patch_id']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / backup_config.get('backup_dir', 'backups/pre_patch')
        patch_backup_dir = backup_dir / f"{patch_id}_{timestamp}"
        patch_backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            files = patch_data.get('files', [])
            
            for file_info in files:
                source_path = self.project_root / file_info['path']
                
                # Only backup existing files that will be modified
                if source_path.exists() and file_info.get('action') in ['modify', 'replace']:
                    relative_path = file_info['path']
                    backup_file = patch_backup_dir / relative_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(source_path, backup_file)
                    logger.info(f"Backed up: {source_path} -> {backup_file}")
            
            # Save patch metadata with backup
            metadata = {
                'patch_id': patch_id,
                'backup_created_at': datetime.now(timezone.utc).isoformat(),
                'files': files,
                'original_checksums': {}
            }
            
            # Calculate checksums of original files
            for file_info in files:
                source_path = self.project_root / file_info['path']
                if source_path.exists():
                    metadata['original_checksums'][file_info['path']] = self.calculate_file_checksum(source_path)
            
            metadata_file = patch_backup_dir / 'backup_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup created: {patch_backup_dir}")
            
            # Cleanup old backups
            self.cleanup_old_backups(backup_dir, backup_config.get('keep_versions', 10))
            
            return patch_backup_dir
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def cleanup_old_backups(self, backup_dir: Path, keep_versions: int) -> None:
        """Clean up old backup directories"""
        try:
            if not backup_dir.exists():
                return
            
            backup_dirs = []
            for item in backup_dir.iterdir():
                if item.is_dir():
                    backup_dirs.append(item)
            
            # Sort by modification time (newest first)
            backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups beyond keep_versions
            for old_backup in backup_dirs[keep_versions:]:
                shutil.rmtree(old_backup)
                logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
    
    def apply_patch_files(self, patch_data: Dict[str, Any], backup_dir: Optional[Path]) -> bool:
        """Apply patch to files"""
        try:
            files = patch_data.get('files', [])
            
            for file_info in files:
                if not self.apply_single_file_patch(file_info, patch_data, backup_dir):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply patch files: {e}")
            return False
    
    def apply_single_file_patch(self, file_info: Dict[str, Any], patch_data: Dict[str, Any], backup_dir: Optional[Path]) -> bool:
        """Apply patch to a single file"""
        try:
            target_path = self.project_root / file_info['path']
            action = file_info.get('action', 'modify')
            
            logger.info(f"Applying {action} to {target_path}")
            
            if action == 'create':
                # Create new file
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                if 'content' in file_info:
                    # Write content directly
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(file_info['content'])
                elif 'source_file' in file_info:
                    # Copy from source file in patch
                    source_file = self.patches_dir / patch_data['patch_id'] / file_info['source_file']
                    if source_file.exists():
                        shutil.copy2(source_file, target_path)
                    else:
                        logger.error(f"Source file not found: {source_file}")
                        return False
                
            elif action == 'modify':
                # Modify existing file
                if not target_path.exists():
                    logger.error(f"Cannot modify non-existent file: {target_path}")
                    return False
                
                # Apply modifications based on patch type
                if 'replacements' in file_info:
                    # Text replacements
                    content = target_path.read_text(encoding='utf-8')
                    
                    for replacement in file_info['replacements']:
                        old_text = replacement['old']
                        new_text = replacement['new']
                        
                        if old_text not in content:
                            logger.warning(f"Replacement text not found in {target_path}: {old_text}")
                            continue
                        
                        content = content.replace(old_text, new_text)
                    
                    target_path.write_text(content, encoding='utf-8')
                
                elif 'patch_file' in file_info:
                    # Apply unified diff patch
                    patch_file = self.patches_dir / patch_data['patch_id'] / file_info['patch_file']
                    
                    if not patch_file.exists():
                        logger.error(f"Patch file not found: {patch_file}")
                        return False
                    
                    # Apply patch using system patch command
                    result = subprocess.run(['patch', '-p1', str(target_path)], 
                                          input=patch_file.read_text(),
                                          text=True, capture_output=True)
                    
                    if result.returncode != 0:
                        logger.error(f"Failed to apply patch: {result.stderr}")
                        return False
            
            elif action == 'replace':
                # Replace entire file
                if 'source_file' in file_info:
                    source_file = self.patches_dir / patch_data['patch_id'] / file_info['source_file']
                    
                    if source_file.exists():
                        shutil.copy2(source_file, target_path)
                    else:
                        logger.error(f"Source file not found: {source_file}")
                        return False
                elif 'content' in file_info:
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(file_info['content'])
            
            elif action == 'delete':
                # Delete file
                if target_path.exists():
                    target_path.unlink()
            
            else:
                logger.error(f"Unknown patch action: {action}")
                return False
            
            # Verify checksum if provided
            if target_path.exists() and 'checksum' in file_info:
                actual_checksum = self.calculate_file_checksum(target_path)
                expected_checksum = file_info['checksum']
                
                if actual_checksum != expected_checksum:
                    logger.error(f"Checksum mismatch for {target_path}")
                    logger.error(f"Expected: {expected_checksum}")
                    logger.error(f"Actual: {actual_checksum}")
                    return False
            
            # Record file change in database
            self.record_file_change(patch_data['patch_id'], file_info, target_path, backup_dir)
            
            logger.info(f"Successfully applied {action} to {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply patch to {file_info.get('path', 'unknown')}: {e}")
            return False
    
    def record_file_change(self, patch_id: str, file_info: Dict[str, Any], target_path: Path, backup_dir: Optional[Path]) -> None:
        """Record file change in database"""
        try:
            conn = sqlite3.connect(self.patch_db_file)
            cursor = conn.cursor()
            
            backup_path = None
            if backup_dir:
                backup_path = str(backup_dir / file_info['path'])
            
            original_checksum = None
            if backup_path and Path(backup_path).exists():
                original_checksum = self.calculate_file_checksum(Path(backup_path))
            
            patched_checksum = None
            if target_path.exists():
                patched_checksum = self.calculate_file_checksum(target_path)
            
            cursor.execute('''
                INSERT INTO patch_files
                (patch_id, file_path, original_checksum, patched_checksum, backup_path, action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                patch_id,
                file_info['path'],
                original_checksum,
                patched_checksum,
                backup_path,
                file_info.get('action', 'modify')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"Failed to record file change: {e}")
    
    def run_post_patch_tests(self, patch_data: Dict[str, Any]) -> bool:
        """Run tests after applying patch"""
        config = self.load_patch_config()
        verification_config = config.get('verification', {})
        
        if not verification_config.get('test_after_patch', True):
            return True
        
        try:
            tests = patch_data.get('tests', [])
            
            for test in tests:
                test_type = test.get('type', 'command')
                
                if test_type == 'command':
                    # Run command test
                    cmd = test['command']
                    expected_exit_code = test.get('expected_exit_code', 0)
                    
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                          cwd=self.project_root, timeout=test.get('timeout', 60))
                    
                    if result.returncode != expected_exit_code:
                        logger.error(f"Test failed - Command: {cmd}")
                        logger.error(f"Expected exit code: {expected_exit_code}, got: {result.returncode}")
                        logger.error(f"STDERR: {result.stderr}")
                        return False
                
                elif test_type == 'import':
                    # Test Python import
                    module = test['module']
                    
                    try:
                        __import__(module)
                        logger.info(f"Import test passed: {module}")
                    except ImportError as e:
                        logger.error(f"Import test failed for {module}: {e}")
                        return False
                
                elif test_type == 'file_exists':
                    # Check if file exists
                    file_path = self.project_root / test['path']
                    
                    if not file_path.exists():
                        logger.error(f"File existence test failed: {file_path}")
                        return False
            
            logger.info("All post-patch tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Post-patch tests failed: {e}")
            return False
    
    def record_patch_applied(self, patch_data: Dict[str, Any], backup_dir: Optional[Path]) -> None:
        """Record patch as successfully applied"""
        conn = sqlite3.connect(self.patch_db_file)
        cursor = conn.cursor()
        
        rollback_info = {}
        if backup_dir:
            rollback_info['backup_dir'] = str(backup_dir)
        
        cursor.execute('''
            INSERT OR REPLACE INTO patches
            (patch_id, name, version, description, patch_type, severity, status, 
             applied_at, rollback_info, checksum, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patch_data['patch_id'],
            patch_data['name'],
            patch_data.get('version', ''),
            patch_data.get('description', ''),
            patch_data.get('patch_type', ''),
            patch_data.get('severity', ''),
            'applied',
            datetime.now(timezone.utc).isoformat(),
            json.dumps(rollback_info),
            patch_data.get('checksum', ''),
            ''  # file_path - will be set when moving to applied directory
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded patch as applied: {patch_data['patch_id']}")
    
    def apply_patch(self, patch_file: Path) -> bool:
        """Apply a single patch"""
        logger.info(f"Applying patch: {patch_file}")
        
        # Initialize database if needed
        if not self.patch_db_file.exists():
            self.init_patch_database()
        
        # Parse patch file
        patch_data = self.parse_patch_file(patch_file)
        if not patch_data:
            return False
        
        patch_id = patch_data['patch_id']
        
        # Check if already applied
        if self.is_patch_applied(patch_id):
            logger.info(f"Patch {patch_id} is already applied")
            return True
        
        # Validate patch
        if not self.validate_patch(patch_data):
            logger.error(f"Patch validation failed: {patch_id}")
            return False
        
        # Create backup
        backup_dir = self.backup_files(patch_data)
        
        try:
            # Apply patch files
            if not self.apply_patch_files(patch_data, backup_dir):
                logger.error(f"Failed to apply patch files: {patch_id}")
                
                # Rollback if enabled
                config = self.load_patch_config()
                if config.get('verification', {}).get('rollback_on_failure', True) and backup_dir:
                    logger.info("Rolling back changes...")
                    self.rollback_patch_from_backup(backup_dir)
                
                return False
            
            # Run post-patch tests
            if not self.run_post_patch_tests(patch_data):
                logger.error(f"Post-patch tests failed: {patch_id}")
                
                # Rollback if enabled
                config = self.load_patch_config()
                if config.get('verification', {}).get('rollback_on_failure', True) and backup_dir:
                    logger.info("Rolling back changes due to test failures...")
                    self.rollback_patch_from_backup(backup_dir)
                
                return False
            
            # Record successful application
            self.record_patch_applied(patch_data, backup_dir)
            
            # Move patch to applied directory
            applied_patch_file = self.applied_patches_dir / patch_file.name
            shutil.move(patch_file, applied_patch_file)
            
            logger.info(f"Successfully applied patch: {patch_id}")
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error applying patch {patch_id}: {e}")
            
            # Rollback if enabled
            config = self.load_patch_config()
            if config.get('verification', {}).get('rollback_on_failure', True) and backup_dir:
                logger.info("Rolling back changes due to error...")
                self.rollback_patch_from_backup(backup_dir)
            
            return False
    
    def rollback_patch_from_backup(self, backup_dir: Path) -> bool:
        """Rollback patch using backup"""
        try:
            metadata_file = backup_dir / 'backup_metadata.json'
            
            if not metadata_file.exists():
                logger.error(f"Backup metadata not found: {metadata_file}")
                return False
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            files = metadata.get('files', [])
            
            for file_info in files:
                target_path = self.project_root / file_info['path']
                backup_file = backup_dir / file_info['path']
                
                if backup_file.exists():
                    # Restore from backup
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, target_path)
                    logger.info(f"Restored: {target_path}")
                elif file_info.get('action') == 'create':
                    # Remove created file
                    if target_path.exists():
                        target_path.unlink()
                        logger.info(f"Removed created file: {target_path}")
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def apply_all_patches(self) -> Dict[str, bool]:
        """Apply all available patches"""
        logger.info("Applying all available patches...")
        
        patch_files = list(self.patches_dir.glob('*.json')) + list(self.patches_dir.glob('*.yaml')) + list(self.patches_dir.glob('*.yml'))
        
        if not patch_files:
            logger.info("No patches found to apply")
            return {}
        
        results = {}
        
        # Sort patches by name to ensure consistent order
        patch_files.sort(key=lambda x: x.name)
        
        for patch_file in patch_files:
            try:
                results[patch_file.name] = self.apply_patch(patch_file)
            except Exception as e:
                logger.error(f"Error applying patch {patch_file}: {e}")
                results[patch_file.name] = False
        
        # Print summary
        successful = sum(1 for result in results.values() if result is True)
        failed = sum(1 for result in results.values() if result is False)
        
        logger.info(f"Patch application summary: {successful} successful, {failed} failed")
        
        return results
    
    def list_applied_patches(self) -> List[Dict[str, Any]]:
        """List all applied patches"""
        if not self.patch_db_file.exists():
            return []
        
        conn = sqlite3.connect(self.patch_db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT patch_id, name, version, description, patch_type, severity, applied_at
            FROM patches
            WHERE status = 'applied'
            ORDER BY applied_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        patches = []
        for row in results:
            patches.append({
                'patch_id': row[0],
                'name': row[1],
                'version': row[2],
                'description': row[3],
                'patch_type': row[4],
                'severity': row[5],
                'applied_at': row[6]
            })
        
        return patches

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Patch Application Manager")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply patch')
    apply_parser.add_argument('--patch', required=True, help='Path to patch file')
    
    # Apply all command
    apply_all_parser = subparsers.add_parser('apply-all', help='Apply all available patches')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List applied patches')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize patch database')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create patch manager
    manager = PatchManager(args.project_root)
    manager.print_banner()
    
    try:
        if args.command == 'apply':
            patch_file = Path(args.patch)
            if not patch_file.exists():
                print(f"❌ Patch file not found: {patch_file}")
                sys.exit(1)
            
            if manager.apply_patch(patch_file):
                print("✅ Patch applied successfully")
                sys.exit(0)
            else:
                print("❌ Failed to apply patch")
                sys.exit(1)
        
        elif args.command == 'apply-all':
            results = manager.apply_all_patches()
            failed_count = sum(1 for result in results.values() if result is False)
            
            if failed_count == 0:
                print("✅ All patches applied successfully")
                sys.exit(0)
            else:
                print(f"❌ {failed_count} patches failed to apply")
                sys.exit(1)
        
        elif args.command == 'list':
            patches = manager.list_applied_patches()
            
            if not patches:
                print("No patches have been applied")
            else:
                print(f"\nApplied patches ({len(patches)}):")
                print("-" * 80)
                for patch in patches:
                    print(f"ID: {patch['patch_id']}")
                    print(f"Name: {patch['name']}")
                    print(f"Type: {patch['patch_type']}")
                    print(f"Applied: {patch['applied_at']}")
                    print("-" * 40)
        
        elif args.command == 'init':
            manager.init_patch_database()
            print("✅ Patch database initialized")
        
    except KeyboardInterrupt:
        logger.info("Patch application interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()