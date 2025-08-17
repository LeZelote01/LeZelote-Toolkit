#!/usr/bin/env python3
"""
LeZelote-Toolkit - Backup System
==============================

This script provides comprehensive backup functionality for the
Pentest-USB Toolkit, including:
- Complete system backups
- Configuration backups
- Project and scan data backups
- Database backups
- Incremental backups
- Backup verification and restoration

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import json
import shutil
import tarfile
import hashlib
import datetime
import sqlite3
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import argparse
import zipfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging
try:
    from core.db.sqlite_manager import SQLiteManager as DatabaseManager
except ImportError:
    DatabaseManager = None

# Simple helper functions
def safe_copy_file(src: str, dst: str) -> bool:
    """Safely copy a file."""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

def get_file_size(filepath: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(filepath)
    except Exception:
        return 0

def calculate_file_hash(filepath: str) -> str:
    """Calculate file hash."""
    try:
        from core.utils.file_ops import FileOperations
        return FileOperations().calculate_hash(filepath, 'md5')
    except Exception:
        return None

class BackupManager:
    """Comprehensive backup and restoration system."""
    
    def __init__(self, backup_dir: str = None):
        """Initialize the backup manager."""
        self.logger = setup_logging(__name__)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.backup_dir = backup_dir or os.path.join(self.project_root, 'backups')
        self.ensure_backup_directory()
        
        self.backup_config = {
            'core_dirs': ['core', 'modules', 'interfaces'],
            'config_dirs': ['config'],
            'data_dirs': ['data', 'reports', 'outputs'],
            'script_dirs': ['scripts'],
            'log_dirs': ['logs'],
            'exclude_patterns': [
                '*.pyc', '__pycache__', '.git', '.gitignore',
                '*.tmp', '*.temp', '*.lock', 'node_modules',
                '*.log.gz', 'archive'
            ],
            'compression': True,
            'verify_backups': True
        }
        
        self.stats = {
            'files_backed_up': 0,
            'bytes_backed_up': 0,
            'backup_time': None,
            'backup_path': None,
            'errors': []
        }
    
    def ensure_backup_directory(self):
        """Ensure backup directory exists."""
        os.makedirs(self.backup_dir, exist_ok=True)
        self.logger.info(f"Backup directory: {self.backup_dir}")
    
    def create_full_backup(self, include_logs: bool = False, 
                          include_outputs: bool = True) -> str:
        """Create a complete system backup."""
        self.logger.info("Starting full system backup...")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"lezelote_toolkit_full_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Backup core system files
                self._backup_core_files(tar)
                
                # Backup configuration
                self._backup_configuration(tar)
                
                # Backup data directories
                self._backup_data_files(tar, include_outputs)
                
                # Backup scripts
                self._backup_scripts(tar)
                
                # Backup logs if requested
                if include_logs:
                    self._backup_logs(tar)
                
                # Backup databases
                self._backup_databases(tar)
                
                # Add backup manifest
                self._add_backup_manifest(tar, backup_name)
            
            # Verify backup if enabled
            if self.backup_config['verify_backups']:
                if self._verify_backup(backup_path):
                    self.logger.info("Backup verification successful")
                else:
                    raise Exception("Backup verification failed")
            
            self.stats['backup_path'] = backup_path
            self.stats['backup_time'] = datetime.datetime.now().isoformat()
            
            backup_size = os.path.getsize(backup_path)
            self.stats['bytes_backed_up'] = backup_size
            
            self.logger.info(f"Full backup completed: {backup_path}")
            self.logger.info(f"Backup size: {backup_size / (1024*1024):.2f} MB")
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise
    
    def create_incremental_backup(self, reference_backup: str = None) -> str:
        """Create an incremental backup since last full backup."""
        self.logger.info("Starting incremental backup...")
        
        if not reference_backup:
            reference_backup = self._find_latest_backup()
            if not reference_backup:
                self.logger.warning("No reference backup found, creating full backup")
                return self.create_full_backup()
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"lezelote_toolkit_incremental_{timestamp}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        # Get reference backup timestamp
        ref_stat = os.stat(reference_backup)
        ref_time = datetime.datetime.fromtimestamp(ref_stat.st_mtime)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Only backup files newer than reference
                self._backup_modified_files(tar, ref_time)
                
                # Always backup critical config and database
                self._backup_configuration(tar)
                self._backup_databases(tar)
                
                # Add incremental manifest
                self._add_incremental_manifest(tar, backup_name, reference_backup)
            
            self.stats['backup_path'] = backup_path
            self.stats['backup_time'] = datetime.datetime.now().isoformat()
            
            backup_size = os.path.getsize(backup_path)
            self.stats['bytes_backed_up'] = backup_size
            
            self.logger.info(f"Incremental backup completed: {backup_path}")
            self.logger.info(f"Backup size: {backup_size / (1024*1024):.2f} MB")
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Incremental backup failed: {e}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise
    
    def create_config_backup(self) -> str:
        """Create a backup of configuration files only."""
        self.logger.info("Starting configuration backup...")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"lezelote_toolkit_config_{timestamp}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                config_dir = os.path.join(self.project_root, 'config')
                if os.path.exists(config_dir):
                    for root, dirs, files in os.walk(config_dir):
                        for file in files:
                            if not self._should_exclude(file):
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, self.project_root)
                                zip_file.write(file_path, arc_path)
                                self.stats['files_backed_up'] += 1
                
                # Add backup info
                backup_info = {
                    'type': 'configuration',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'files_count': self.stats['files_backed_up']
                }
                
                zip_file.writestr('backup_info.json', json.dumps(backup_info, indent=2))
            
            self.stats['backup_path'] = backup_path
            self.stats['backup_time'] = datetime.datetime.now().isoformat()
            
            backup_size = os.path.getsize(backup_path)
            self.stats['bytes_backed_up'] = backup_size
            
            self.logger.info(f"Configuration backup completed: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Configuration backup failed: {e}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise
    
    def create_database_backup(self) -> str:
        """Create a backup of all databases."""
        self.logger.info("Starting database backup...")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"lezelote_toolkit_database_{timestamp}"
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                self._backup_databases(tar)
                
                # Add database backup info
                db_info = {
                    'type': 'database',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'databases': []
                }
                
                # Find all database files
                for root, dirs, files in os.walk(self.project_root):
                    for file in files:
                        if file.endswith(('.db', '.sqlite', '.sqlite3')):
                            db_path = os.path.join(root, file)
                            rel_path = os.path.relpath(db_path, self.project_root)
                            db_info['databases'].append(rel_path)
                
                db_info_json = json.dumps(db_info, indent=2)
                tarinfo = tarfile.TarInfo(name='database_backup_info.json')
                tarinfo.size = len(db_info_json.encode())
                tar.addfile(tarinfo, fileobj=io.BytesIO(db_info_json.encode()))
            
            self.stats['backup_path'] = backup_path
            self.stats['backup_time'] = datetime.datetime.now().isoformat()
            
            backup_size = os.path.getsize(backup_path)
            self.stats['bytes_backed_up'] = backup_size
            
            self.logger.info(f"Database backup completed: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise
    
    def restore_backup(self, backup_path: str, target_dir: str = None, 
                      selective: List[str] = None) -> bool:
        """Restore from a backup file."""
        self.logger.info(f"Starting backup restoration from: {backup_path}")
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        target_dir = target_dir or self.project_root
        
        try:
            # Create restoration directory
            restore_temp = os.path.join(target_dir, 'restore_temp')
            os.makedirs(restore_temp, exist_ok=True)
            
            # Extract backup
            if backup_path.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tar:
                    if selective:
                        # Selective restoration
                        for member in tar.getmembers():
                            if any(pattern in member.name for pattern in selective):
                                tar.extract(member, restore_temp)
                    else:
                        tar.extractall(restore_temp)
            
            elif backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    if selective:
                        for file_info in zip_file.filelist:
                            if any(pattern in file_info.filename for pattern in selective):
                                zip_file.extract(file_info, restore_temp)
                    else:
                        zip_file.extractall(restore_temp)
            
            # Move files from temp to target
            self._move_restored_files(restore_temp, target_dir)
            
            # Clean up temp directory
            shutil.rmtree(restore_temp, ignore_errors=True)
            
            self.logger.info("Backup restoration completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            # Clean up on failure
            if 'restore_temp' in locals() and os.path.exists(restore_temp):
                shutil.rmtree(restore_temp, ignore_errors=True)
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups with metadata."""
        backups = []
        
        for file in os.listdir(self.backup_dir):
            if file.startswith('lezelote_toolkit_') and (file.endswith('.tar.gz') or file.endswith('.zip')):
                backup_path = os.path.join(self.backup_dir, file)
                stat = os.stat(backup_path)
                
                # Determine backup type from filename
                if 'full' in file:
                    backup_type = 'full'
                elif 'incremental' in file:
                    backup_type = 'incremental'
                elif 'config' in file:
                    backup_type = 'configuration'
                elif 'database' in file:
                    backup_type = 'database'
                else:
                    backup_type = 'unknown'
                
                backups.append({
                    'filename': file,
                    'path': backup_path,
                    'type': backup_type,
                    'size_mb': round(stat.st_size / (1024*1024), 2),
                    'created': datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backups, keeping only the most recent ones."""
        self.logger.info(f"Cleaning up old backups, keeping {keep_count} most recent")
        
        backups = self.list_backups()
        deleted_count = 0
        
        if len(backups) > keep_count:
            to_delete = backups[keep_count:]
            
            for backup in to_delete:
                try:
                    os.remove(backup['path'])
                    self.logger.info(f"Deleted old backup: {backup['filename']}")
                    deleted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to delete backup {backup['filename']}: {e}")
        
        self.logger.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count
    
    def _backup_core_files(self, tar: tarfile.TarFile):
        """Backup core system files."""
        for dir_name in self.backup_config['core_dirs']:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                self._add_directory_to_tar(tar, dir_path, dir_name)
    
    def _backup_configuration(self, tar: tarfile.TarFile):
        """Backup configuration files."""
        for dir_name in self.backup_config['config_dirs']:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                self._add_directory_to_tar(tar, dir_path, dir_name)
    
    def _backup_data_files(self, tar: tarfile.TarFile, include_outputs: bool):
        """Backup data directories."""
        data_dirs = self.backup_config['data_dirs'].copy()
        if not include_outputs:
            data_dirs = [d for d in data_dirs if d != 'outputs']
        
        for dir_name in data_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                self._add_directory_to_tar(tar, dir_path, dir_name)
    
    def _backup_scripts(self, tar: tarfile.TarFile):
        """Backup script directories."""
        for dir_name in self.backup_config['script_dirs']:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                self._add_directory_to_tar(tar, dir_path, dir_name)
    
    def _backup_logs(self, tar: tarfile.TarFile):
        """Backup log directories."""
        for dir_name in self.backup_config['log_dirs']:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                self._add_directory_to_tar(tar, dir_path, dir_name)
    
    def _backup_databases(self, tar: tarfile.TarFile):
        """Backup database files."""
        # Find and backup all database files
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_path = os.path.join(root, file)
                    arc_path = os.path.relpath(db_path, self.project_root)
                    
                    # Create a copy for backup to avoid locks
                    temp_db = f"{db_path}.backup_temp"
                    try:
                        # For SQLite, use backup API if possible
                        if file.endswith(('.db', '.sqlite', '.sqlite3')):
                            self._backup_sqlite_database(db_path, temp_db)
                        else:
                            shutil.copy2(db_path, temp_db)
                        
                        tar.add(temp_db, arcname=arc_path)
                        os.remove(temp_db)
                        self.stats['files_backed_up'] += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to backup database {db_path}: {e}")
                        if os.path.exists(temp_db):
                            os.remove(temp_db)
    
    def _backup_sqlite_database(self, source_db: str, target_db: str):
        """Backup SQLite database using proper backup API."""
        try:
            # Use SQLite backup API for consistent backup
            source = sqlite3.connect(source_db)
            target = sqlite3.connect(target_db)
            
            source.backup(target)
            
            source.close()
            target.close()
            
        except Exception as e:
            # Fallback to file copy
            self.logger.warning(f"SQLite backup API failed for {source_db}, using file copy: {e}")
            shutil.copy2(source_db, target_db)
    
    def _add_directory_to_tar(self, tar: tarfile.TarFile, dir_path: str, arc_name: str):
        """Add a directory to tar archive with filtering."""
        for root, dirs, files in os.walk(dir_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            for file in files:
                if not self._should_exclude(file):
                    file_path = os.path.join(root, file)
                    arc_path = os.path.join(arc_name, os.path.relpath(file_path, dir_path))
                    try:
                        tar.add(file_path, arcname=arc_path)
                        self.stats['files_backed_up'] += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to add {file_path} to backup: {e}")
    
    def _should_exclude(self, name: str) -> bool:
        """Check if a file or directory should be excluded."""
        for pattern in self.backup_config['exclude_patterns']:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            elif pattern.endswith('*') and name.startswith(pattern[:-1]):
                return True
            elif pattern in name:
                return True
        return False
    
    def _add_backup_manifest(self, tar: tarfile.TarFile, backup_name: str):
        """Add backup manifest with metadata."""
        import io
        
        manifest = {
            'backup_name': backup_name,
            'backup_type': 'full',
            'timestamp': datetime.datetime.now().isoformat(),
            'files_count': self.stats['files_backed_up'],
            'toolkit_version': '1.0.0',
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        manifest_json = json.dumps(manifest, indent=2)
        tarinfo = tarfile.TarInfo(name='backup_manifest.json')
        tarinfo.size = len(manifest_json.encode())
        tar.addfile(tarinfo, fileobj=io.BytesIO(manifest_json.encode()))
    
    def _verify_backup(self, backup_path: str) -> bool:
        """Verify backup integrity."""
        try:
            if backup_path.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tar:
                    # Try to read all members
                    for member in tar.getmembers():
                        if member.isreg():
                            try:
                                tar.extractfile(member).read(1024)  # Read first KB
                            except Exception:
                                return False
            
            elif backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    # Test the archive
                    bad_file = zip_file.testzip()
                    if bad_file:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return False
    
    def _find_latest_backup(self) -> Optional[str]:
        """Find the latest full backup."""
        backups = self.list_backups()
        full_backups = [b for b in backups if b['type'] == 'full']
        
        if full_backups:
            return full_backups[0]['path']  # Already sorted by date
        return None

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit Backup Manager')
    parser.add_argument('action', choices=['full', 'incremental', 'config', 'database', 'restore', 'list', 'cleanup'],
                       help='Backup action to perform')
    parser.add_argument('--backup-dir', help='Custom backup directory')
    parser.add_argument('--backup-path', help='Backup file path for restore')
    parser.add_argument('--target-dir', help='Target directory for restore')
    parser.add_argument('--include-logs', action='store_true', help='Include logs in backup')
    parser.add_argument('--exclude-outputs', action='store_true', help='Exclude outputs from backup')
    parser.add_argument('--keep-count', type=int, default=10, help='Number of backups to keep during cleanup')
    
    args = parser.parse_args()
    
    try:
        backup_manager = BackupManager(backup_dir=args.backup_dir)
        
        if args.action == 'full':
            backup_path = backup_manager.create_full_backup(
                include_logs=args.include_logs,
                include_outputs=not args.exclude_outputs
            )
            print(f"Full backup created: {backup_path}")
        
        elif args.action == 'incremental':
            backup_path = backup_manager.create_incremental_backup()
            print(f"Incremental backup created: {backup_path}")
        
        elif args.action == 'config':
            backup_path = backup_manager.create_config_backup()
            print(f"Configuration backup created: {backup_path}")
        
        elif args.action == 'database':
            backup_path = backup_manager.create_database_backup()
            print(f"Database backup created: {backup_path}")
        
        elif args.action == 'restore':
            if not args.backup_path:
                print("Error: --backup-path required for restore", file=sys.stderr)
                sys.exit(1)
            
            success = backup_manager.restore_backup(args.backup_path, args.target_dir)
            if success:
                print("Backup restored successfully")
            else:
                print("Backup restoration failed", file=sys.stderr)
                sys.exit(1)
        
        elif args.action == 'list':
            backups = backup_manager.list_backups()
            print("\n=== AVAILABLE BACKUPS ===")
            for backup in backups:
                print(f"File: {backup['filename']}")
                print(f"Type: {backup['type']}")
                print(f"Size: {backup['size_mb']} MB")
                print(f"Created: {backup['created']}")
                print()
        
        elif args.action == 'cleanup':
            deleted_count = backup_manager.cleanup_old_backups(args.keep_count)
            print(f"Cleaned up {deleted_count} old backups")
        
    except Exception as e:
        print(f"Error during backup operation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()