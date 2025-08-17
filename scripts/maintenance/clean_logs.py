#!/usr/bin/env python3
"""
LeZelote-Toolkit - Log Cleaning Utility
======================================

This script provides comprehensive log cleaning functionality for the
Pentest-USB Toolkit, including:
- System logs cleanup
- Scan history management
- Tool logs rotation
- Audit trail maintenance
- Performance log optimization
- Error log archival

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import json
import shutil
import gzip
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import argparse
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging
try:
    from core.db.sqlite_manager import SQLiteManager as DatabaseManager
except ImportError:
    DatabaseManager = None

# Simple helper functions
def safe_delete_file(filepath: str) -> bool:
    """Safely delete a file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
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

class LogCleaner:
    """Comprehensive log cleaning and management system."""
    
    def __init__(self, config_file: str = None):
        """Initialize the log cleaner with configuration."""
        self.logger = setup_logging(__name__)
        self.config_file = config_file or self._get_default_config()
        self.config = self._load_config()
        self.stats = {
            'files_cleaned': 0,
            'files_archived': 0,
            'files_deleted': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
    def _get_default_config(self) -> str:
        """Get default configuration file path."""
        return os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'logging.yaml')
    
    def _load_config(self) -> Dict:
        """Load cleaning configuration."""
        default_config = {
            'retention_days': {
                'system_logs': 30,
                'scan_logs': 90,
                'tool_logs': 14,
                'audit_logs': 365,
                'error_logs': 60,
                'performance_logs': 7
            },
            'archive_after_days': {
                'system_logs': 7,
                'scan_logs': 30,
                'tool_logs': 3,
                'performance_logs': 3
            },
            'max_file_size_mb': {
                'system_logs': 100,
                'scan_logs': 500,
                'tool_logs': 50,
                'audit_logs': 200,
                'error_logs': 100
            },
            'log_directories': {
                'system': 'logs',
                'scans': 'logs/scan_history',
                'tools': 'logs/tool_logs',
                'performance': 'logs/performance',
                'audit': 'logs',
                'errors': 'logs'
            },
            'compress_archives': True,
            'keep_recent_files': 5
        }
        
        try:
            if os.path.exists(self.config_file):
                import yaml
                with open(self.config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    if 'log_cleaning' in loaded_config:
                        return {**default_config, **loaded_config['log_cleaning']}
            return default_config
        except Exception as e:
            self.logger.warning(f"Failed to load config, using defaults: {e}")
            return default_config
    
    def clean_all_logs(self, dry_run: bool = False) -> Dict:
        """Clean all log categories."""
        self.logger.info("Starting comprehensive log cleaning...")
        
        if dry_run:
            self.logger.info("DRY RUN MODE - No files will be modified")
        
        # Clean different log categories
        self._clean_system_logs(dry_run)
        self._clean_scan_logs(dry_run)
        self._clean_tool_logs(dry_run)
        self._clean_audit_logs(dry_run)
        self._clean_error_logs(dry_run)
        self._clean_performance_logs(dry_run)
        
        # Clean database logs if database exists
        self._clean_database_logs(dry_run)
        
        self._generate_cleanup_report()
        return self.stats
    
    def _clean_system_logs(self, dry_run: bool = False) -> None:
        """Clean system logs."""
        self.logger.info("Cleaning system logs...")
        log_dir = self._get_log_directory('system')
        
        if not os.path.exists(log_dir):
            return
        
        retention_days = self.config['retention_days']['system_logs']
        archive_days = self.config['archive_after_days']['system_logs']
        max_size_mb = self.config['max_file_size_mb']['system_logs']
        
        self._process_log_directory(
            log_dir, 
            retention_days, 
            archive_days, 
            max_size_mb,
            dry_run,
            log_type='system'
        )
    
    def _clean_scan_logs(self, dry_run: bool = False) -> None:
        """Clean scan history logs."""
        self.logger.info("Cleaning scan logs...")
        log_dir = self._get_log_directory('scans')
        
        if not os.path.exists(log_dir):
            return
        
        retention_days = self.config['retention_days']['scan_logs']
        archive_days = self.config['archive_after_days']['scan_logs']
        max_size_mb = self.config['max_file_size_mb']['scan_logs']
        
        self._process_log_directory(
            log_dir,
            retention_days,
            archive_days,
            max_size_mb,
            dry_run,
            log_type='scan'
        )
    
    def _clean_tool_logs(self, dry_run: bool = False) -> None:
        """Clean tool-specific logs."""
        self.logger.info("Cleaning tool logs...")
        log_dir = self._get_log_directory('tools')
        
        if not os.path.exists(log_dir):
            return
        
        retention_days = self.config['retention_days']['tool_logs']
        archive_days = self.config['archive_after_days']['tool_logs']
        max_size_mb = self.config['max_file_size_mb']['tool_logs']
        
        self._process_log_directory(
            log_dir,
            retention_days,
            archive_days,
            max_size_mb,
            dry_run,
            log_type='tool'
        )
    
    def _clean_audit_logs(self, dry_run: bool = False) -> None:
        """Clean audit logs (special handling - longer retention)."""
        self.logger.info("Cleaning audit logs...")
        log_dir = self._get_log_directory('audit')
        
        if not os.path.exists(log_dir):
            return
        
        retention_days = self.config['retention_days']['audit_logs']
        max_size_mb = self.config['max_file_size_mb']['audit_logs']
        
        # Audit logs are archived but rarely deleted
        self._process_log_directory(
            log_dir,
            retention_days,
            7,  # Archive after 7 days
            max_size_mb,
            dry_run,
            log_type='audit',
            patterns=['*audit*', '*consent*', '*authorization*']
        )
    
    def _clean_error_logs(self, dry_run: bool = False) -> None:
        """Clean error logs."""
        self.logger.info("Cleaning error logs...")
        log_dir = self._get_log_directory('errors')
        
        if not os.path.exists(log_dir):
            return
        
        retention_days = self.config['retention_days']['error_logs']
        max_size_mb = self.config['max_file_size_mb']['error_logs']
        
        self._process_log_directory(
            log_dir,
            retention_days,
            3,  # Archive errors quickly
            max_size_mb,
            dry_run,
            log_type='error',
            patterns=['*error*', '*exception*', '*crash*']
        )
    
    def _clean_performance_logs(self, dry_run: bool = False) -> None:
        """Clean performance monitoring logs."""
        self.logger.info("Cleaning performance logs...")
        log_dir = self._get_log_directory('performance')
        
        if not os.path.exists(log_dir):
            return
        
        retention_days = self.config['retention_days']['performance_logs']
        archive_days = self.config['archive_after_days']['performance_logs']
        max_size_mb = self.config['max_file_size_mb']['performance_logs']
        
        self._process_log_directory(
            log_dir,
            retention_days,
            archive_days,
            max_size_mb,
            dry_run,
            log_type='performance'
        )
    
    def _process_log_directory(self, log_dir: str, retention_days: int, 
                              archive_days: int, max_size_mb: int, 
                              dry_run: bool, log_type: str, 
                              patterns: List[str] = None) -> None:
        """Process a log directory with specified parameters."""
        if patterns is None:
            patterns = ['*.log', '*.out', '*.err']
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        archive_date = datetime.datetime.now() - datetime.timedelta(days=archive_days)
        
        for pattern in patterns:
            for log_file in Path(log_dir).glob(pattern):
                try:
                    file_stat = log_file.stat()
                    file_age = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                    file_size_mb = file_stat.st_size / (1024 * 1024)
                    
                    # Skip recently modified files
                    if (datetime.datetime.now() - file_age).seconds < 3600:  # 1 hour
                        continue
                    
                    if file_age < cutoff_date:
                        # File is old enough to delete
                        if not dry_run:
                            if safe_delete_file(str(log_file)):
                                self.stats['files_deleted'] += 1
                                self.stats['bytes_freed'] += file_stat.st_size
                                self.logger.info(f"Deleted old {log_type} log: {log_file}")
                        else:
                            self.logger.info(f"Would delete: {log_file}")
                    
                    elif file_age < archive_date or file_size_mb > max_size_mb:
                        # File should be archived
                        if not dry_run:
                            if self._archive_log_file(log_file, log_type):
                                self.stats['files_archived'] += 1
                        else:
                            self.logger.info(f"Would archive: {log_file}")
                    
                    elif file_size_mb > max_size_mb:
                        # File is too large, rotate it
                        if not dry_run:
                            if self._rotate_log_file(log_file):
                                self.stats['files_cleaned'] += 1
                        else:
                            self.logger.info(f"Would rotate: {log_file}")
                
                except Exception as e:
                    error_msg = f"Error processing {log_file}: {e}"
                    self.logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
    
    def _archive_log_file(self, log_file: Path, log_type: str) -> bool:
        """Archive a log file with compression."""
        try:
            archive_dir = log_file.parent / 'archive'
            archive_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{log_file.stem}_{timestamp}.gz"
            archive_path = archive_dir / archive_name
            
            with open(log_file, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Delete original after successful archive
            os.remove(log_file)
            self.logger.info(f"Archived {log_type} log: {log_file} -> {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to archive {log_file}: {e}")
            return False
    
    def _rotate_log_file(self, log_file: Path) -> bool:
        """Rotate a large log file."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
            rotated_path = log_file.parent / rotated_name
            
            # Move current log to rotated name
            shutil.move(str(log_file), str(rotated_path))
            
            # Create new empty log file
            log_file.touch()
            
            self.logger.info(f"Rotated log file: {log_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rotate {log_file}: {e}")
            return False
    
    def _clean_database_logs(self, dry_run: bool = False) -> None:
        """Clean database-related logs and optimize database."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'db', 'knowledge_base.db')
            
            if not os.path.exists(db_path):
                return
            
            self.logger.info("Cleaning database logs...")
            
            if not dry_run:
                # Vacuum database to reclaim space
                with sqlite3.connect(db_path) as conn:
                    conn.execute('VACUUM')
                    conn.execute('ANALYZE')
                
                # Clean old log entries from database
                db_manager = DatabaseManager()
                deleted_count = db_manager.cleanup_old_logs(days=30)
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned {deleted_count} old database log entries")
                    self.stats['files_cleaned'] += deleted_count
            else:
                self.logger.info("Would clean database logs and vacuum database")
        
        except Exception as e:
            error_msg = f"Error cleaning database logs: {e}"
            self.logger.error(error_msg)
            self.stats['errors'].append(error_msg)
    
    def _get_log_directory(self, log_type: str) -> str:
        """Get the full path to a log directory."""
        base_path = os.path.join(os.path.dirname(__file__), '..', '..')
        rel_path = self.config['log_directories'].get(log_type, 'logs')
        return os.path.join(base_path, rel_path)
    
    def _generate_cleanup_report(self) -> None:
        """Generate a cleanup summary report."""
        self.logger.info("Log Cleanup Summary:")
        self.logger.info(f"  Files deleted: {self.stats['files_deleted']}")
        self.logger.info(f"  Files archived: {self.stats['files_archived']}")
        self.logger.info(f"  Files cleaned: {self.stats['files_cleaned']}")
        self.logger.info(f"  Bytes freed: {self.stats['bytes_freed']:,}")
        
        if self.stats['errors']:
            self.logger.warning(f"  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                self.logger.warning(f"    {error}")
    
    def clean_specific_category(self, category: str, dry_run: bool = False) -> Dict:
        """Clean logs for a specific category only."""
        self.logger.info(f"Cleaning {category} logs...")
        
        category_methods = {
            'system': self._clean_system_logs,
            'scan': self._clean_scan_logs,
            'tool': self._clean_tool_logs,
            'audit': self._clean_audit_logs,
            'error': self._clean_error_logs,
            'performance': self._clean_performance_logs,
            'database': self._clean_database_logs
        }
        
        if category in category_methods:
            category_methods[category](dry_run)
            self._generate_cleanup_report()
            return self.stats
        else:
            raise ValueError(f"Unknown log category: {category}")
    
    def get_log_statistics(self) -> Dict:
        """Get statistics about current log usage."""
        stats = {}
        
        for log_type, directory in self.config['log_directories'].items():
            log_dir = self._get_log_directory(log_type)
            if os.path.exists(log_dir):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        if file.endswith(('.log', '.out', '.err')):
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except OSError:
                                continue
                
                stats[log_type] = {
                    'directory': log_dir,
                    'file_count': file_count,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'total_size_bytes': total_size
                }
        
        return stats

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit Log Cleaner')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be cleaned without making changes')
    parser.add_argument('--category', choices=['system', 'scan', 'tool', 'audit', 'error', 'performance', 'database'],
                       help='Clean specific log category only')
    parser.add_argument('--stats', action='store_true',
                       help='Show log statistics without cleaning')
    parser.add_argument('--config', help='Custom configuration file path')
    
    args = parser.parse_args()
    
    try:
        cleaner = LogCleaner(config_file=args.config)
        
        if args.stats:
            stats = cleaner.get_log_statistics()
            print("\n=== LOG STATISTICS ===")
            for category, data in stats.items():
                print(f"{category.upper()}:")
                print(f"  Directory: {data['directory']}")
                print(f"  Files: {data['file_count']}")
                print(f"  Size: {data['total_size_mb']} MB")
                print()
        
        elif args.category:
            results = cleaner.clean_specific_category(args.category, args.dry_run)
            print(f"\nCleaning completed for {args.category} logs")
            print(f"Files processed: {results['files_cleaned'] + results['files_archived'] + results['files_deleted']}")
        
        else:
            results = cleaner.clean_all_logs(args.dry_run)
            print("\nLog cleaning completed")
            print(f"Total files processed: {results['files_cleaned'] + results['files_archived'] + results['files_deleted']}")
            
        print(f"Space freed: {results.get('bytes_freed', 0):,} bytes")
        
    except Exception as e:
        print(f"Error during log cleaning: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()