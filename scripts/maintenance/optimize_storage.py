#!/usr/bin/env python3
"""
LeZelote-Toolkit - Storage Optimization Utility
=============================================

This script provides comprehensive storage optimization for the
Pentest-USB Toolkit, including:
- Duplicate file detection and removal
- Large file analysis and cleanup
- Temporary file cleanup
- Archive optimization
- Database optimization
- Cache cleanup

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import hashlib
import shutil
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import logging
import argparse
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging

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

class StorageOptimizer:
    """Comprehensive storage optimization and cleanup system."""
    
    def __init__(self):
        """Initialize the storage optimizer."""
        self.logger = setup_logging(__name__)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        self.config = {
            'scan_directories': [
                'outputs', 'reports', 'logs', 'data/loot',
                'tools/containers', 'tests', 'scripts'
            ],
            'exclude_directories': [
                '.git', 'node_modules', '__pycache__',
                '.venv', 'venv', '.emergent'
            ],
            'temporary_patterns': [
                '*.tmp', '*.temp', '*.bak', '*.old',
                '*~', '*.swp', '.DS_Store', 'Thumbs.db'
            ],
            'large_file_threshold_mb': 100,
            'old_file_threshold_days': 30,
            'duplicate_scan_extensions': [
                '.txt', '.log', '.json', '.xml', '.csv',
                '.pdf', '.doc', '.docx', '.zip', '.tar.gz'
            ]
        }
        
        self.stats = {
            'files_scanned': 0,
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'temp_files_removed': 0,
            'large_files_found': 0,
            'bytes_saved': 0,
            'databases_optimized': 0,
            'errors': []
        }
    
    def optimize_all(self, dry_run: bool = False) -> Dict:
        """Run comprehensive storage optimization."""
        self.logger.info("Starting comprehensive storage optimization...")
        
        if dry_run:
            self.logger.info("DRY RUN MODE - No files will be modified")
        
        # Clean temporary files
        self._cleanup_temporary_files(dry_run)
        
        # Find and remove duplicates
        self._find_and_remove_duplicates(dry_run)
        
        # Analyze large files
        self._analyze_large_files(dry_run)
        
        # Clean old files
        self._cleanup_old_files(dry_run)
        
        # Optimize databases
        self._optimize_databases(dry_run)
        
        # Clean caches
        self._cleanup_caches(dry_run)
        
        # Compress archives
        self._optimize_archives(dry_run)
        
        self._generate_optimization_report()
        return self.stats
    
    def _cleanup_temporary_files(self, dry_run: bool = False):
        """Remove temporary and backup files."""
        self.logger.info("Cleaning up temporary files...")
        
        for scan_dir in self.config['scan_directories']:
            dir_path = os.path.join(self.project_root, scan_dir)
            if not os.path.exists(dir_path):
                continue
            
            for pattern in self.config['temporary_patterns']:
                for temp_file in Path(dir_path).rglob(pattern):
                    try:
                        if self._should_exclude_directory(temp_file.parent):
                            continue
                        
                        file_size = temp_file.stat().st_size
                        
                        if not dry_run:
                            if safe_delete_file(str(temp_file)):
                                self.stats['temp_files_removed'] += 1
                                self.stats['bytes_saved'] += file_size
                                self.logger.debug(f"Removed temp file: {temp_file}")
                        else:
                            self.logger.info(f"Would remove temp file: {temp_file}")
                            self.stats['temp_files_removed'] += 1
                            self.stats['bytes_saved'] += file_size
                    
                    except Exception as e:
                        error_msg = f"Error removing temp file {temp_file}: {e}"
                        self.logger.error(error_msg)
                        self.stats['errors'].append(error_msg)
    
    def _find_and_remove_duplicates(self, dry_run: bool = False):
        """Find and remove duplicate files."""
        self.logger.info("Scanning for duplicate files...")
        
        # Build hash map of files
        file_hashes = defaultdict(list)
        
        for scan_dir in self.config['scan_directories']:
            dir_path = os.path.join(self.project_root, scan_dir)
            if not os.path.exists(dir_path):
                continue
            
            for root, dirs, files in os.walk(dir_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Only check certain extensions for duplicates
                    if not any(file_path.suffix.lower() == ext for ext in self.config['duplicate_scan_extensions']):
                        continue
                    
                    try:
                        if file_path.stat().st_size == 0:  # Skip empty files
                            continue
                        
                        # Calculate file hash
                        file_hash = self._calculate_file_hash(file_path)
                        if file_hash:
                            file_hashes[file_hash].append(file_path)
                            self.stats['files_scanned'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error processing file {file_path}: {e}"
                        self.logger.error(error_msg)
                        self.stats['errors'].append(error_msg)
        
        # Process duplicates
        for file_hash, file_list in file_hashes.items():
            if len(file_list) > 1:
                self.stats['duplicates_found'] += len(file_list) - 1
                
                # Keep the file with the shortest path (likely the original)
                file_list.sort(key=lambda x: (len(str(x)), str(x)))
                keep_file = file_list[0]
                duplicate_files = file_list[1:]
                
                self.logger.info(f"Found {len(duplicate_files)} duplicates of: {keep_file}")
                
                for duplicate in duplicate_files:
                    try:
                        file_size = duplicate.stat().st_size
                        
                        if not dry_run:
                            if safe_delete_file(str(duplicate)):
                                self.stats['duplicates_removed'] += 1
                                self.stats['bytes_saved'] += file_size
                                self.logger.info(f"Removed duplicate: {duplicate}")
                        else:
                            self.logger.info(f"Would remove duplicate: {duplicate}")
                            self.stats['duplicates_removed'] += 1
                            self.stats['bytes_saved'] += file_size
                    
                    except Exception as e:
                        error_msg = f"Error removing duplicate {duplicate}: {e}"
                        self.logger.error(error_msg)
                        self.stats['errors'].append(error_msg)
    
    def _analyze_large_files(self, dry_run: bool = False):
        """Analyze and report large files."""
        self.logger.info("Analyzing large files...")
        
        large_files = []
        threshold_bytes = self.config['large_file_threshold_mb'] * 1024 * 1024
        
        for scan_dir in self.config['scan_directories']:
            dir_path = os.path.join(self.project_root, scan_dir)
            if not os.path.exists(dir_path):
                continue
            
            for root, dirs, files in os.walk(dir_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    try:
                        file_size = file_path.stat().st_size
                        
                        if file_size > threshold_bytes:
                            large_files.append({
                                'path': file_path,
                                'size_mb': round(file_size / (1024 * 1024), 2),
                                'size_bytes': file_size,
                                'modified': file_path.stat().st_mtime
                            })
                            self.stats['large_files_found'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error analyzing file {file_path}: {e}"
                        self.logger.error(error_msg)
                        self.stats['errors'].append(error_msg)
        
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x['size_bytes'], reverse=True)
        
        # Report large files
        if large_files:
            self.logger.info(f"Found {len(large_files)} files larger than {self.config['large_file_threshold_mb']} MB:")
            for file_info in large_files[:10]:  # Show top 10
                self.logger.info(f"  {file_info['size_mb']} MB - {file_info['path']}")
        
        # Optionally compress or move large files
        # This would require additional logic based on file types and user preferences
    
    def _cleanup_old_files(self, dry_run: bool = False):
        """Clean up old files based on age threshold."""
        self.logger.info("Cleaning up old files...")
        
        threshold_time = time.time() - (self.config['old_file_threshold_days'] * 24 * 3600)
        old_files_removed = 0
        
        # Focus on specific directories for old file cleanup
        cleanup_dirs = ['outputs/temporary', 'logs', 'reports/archive']
        
        for cleanup_dir in cleanup_dirs:
            dir_path = os.path.join(self.project_root, cleanup_dir)
            if not os.path.exists(dir_path):
                continue
            
            for root, dirs, files in os.walk(dir_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    try:
                        file_stat = file_path.stat()
                        
                        # Check if file is older than threshold
                        if file_stat.st_mtime < threshold_time:
                            file_size = file_stat.st_size
                            
                            if not dry_run:
                                if safe_delete_file(str(file_path)):
                                    old_files_removed += 1
                                    self.stats['bytes_saved'] += file_size
                                    self.logger.debug(f"Removed old file: {file_path}")
                            else:
                                self.logger.info(f"Would remove old file: {file_path}")
                                old_files_removed += 1
                                self.stats['bytes_saved'] += file_size
                    
                    except Exception as e:
                        error_msg = f"Error processing old file {file_path}: {e}"
                        self.logger.error(error_msg)
                        self.stats['errors'].append(error_msg)
        
        if old_files_removed > 0:
            self.logger.info(f"Cleaned up {old_files_removed} old files")
    
    def _optimize_databases(self, dry_run: bool = False):
        """Optimize SQLite databases."""
        self.logger.info("Optimizing databases...")
        
        # Find all database files
        db_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_files.append(os.path.join(root, file))
        
        for db_path in db_files:
            try:
                if not os.path.exists(db_path):
                    continue
                
                original_size = os.path.getsize(db_path)
                
                if not dry_run:
                    # Connect and optimize
                    with sqlite3.connect(db_path) as conn:
                        # Run VACUUM to reclaim space
                        conn.execute('VACUUM')
                        
                        # Update statistics
                        conn.execute('ANALYZE')
                        
                        # Rebuild indexes
                        conn.execute('REINDEX')
                    
                    new_size = os.path.getsize(db_path)
                    bytes_saved = original_size - new_size
                    
                    if bytes_saved > 0:
                        self.stats['bytes_saved'] += bytes_saved
                        self.logger.info(f"Optimized database {os.path.basename(db_path)}: saved {bytes_saved} bytes")
                else:
                    self.logger.info(f"Would optimize database: {os.path.basename(db_path)}")
                
                self.stats['databases_optimized'] += 1
            
            except Exception as e:
                error_msg = f"Error optimizing database {db_path}: {e}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)
    
    def _cleanup_caches(self, dry_run: bool = False):
        """Clean up various cache directories."""
        self.logger.info("Cleaning up caches...")
        
        cache_patterns = [
            '__pycache__',
            '*.pyc',
            '.cache',
            '.pytest_cache',
            'node_modules/.cache',
            '.npm',
            '.yarn'
        ]
        
        cache_files_removed = 0
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove cache directories
            dirs_to_remove = []
            for dir_name in dirs:
                if any(pattern.replace('*', '') in dir_name for pattern in cache_patterns if '*' not in pattern):
                    dirs_to_remove.append(dir_name)
            
            for cache_dir in dirs_to_remove:
                cache_path = Path(root) / cache_dir
                try:
                    if cache_path.exists():
                        cache_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                        
                        if not dry_run:
                            shutil.rmtree(cache_path, ignore_errors=True)
                            self.stats['bytes_saved'] += cache_size
                            cache_files_removed += 1
                            self.logger.debug(f"Removed cache directory: {cache_path}")
                        else:
                            self.logger.info(f"Would remove cache directory: {cache_path}")
                            cache_files_removed += 1
                            self.stats['bytes_saved'] += cache_size
                
                except Exception as e:
                    error_msg = f"Error removing cache {cache_path}: {e}"
                    self.logger.error(error_msg)
                    self.stats['errors'].append(error_msg)
            
            # Remove cache files
            for file in files:
                if any(file.endswith(pattern.replace('*', '')) for pattern in cache_patterns if pattern.startswith('*')):
                    file_path = Path(root) / file
                    try:
                        file_size = file_path.stat().st_size
                        
                        if not dry_run:
                            if safe_delete_file(str(file_path)):
                                cache_files_removed += 1
                                self.stats['bytes_saved'] += file_size
                                self.logger.debug(f"Removed cache file: {file_path}")
                        else:
                            self.logger.info(f"Would remove cache file: {file_path}")
                            cache_files_removed += 1
                            self.stats['bytes_saved'] += file_size
                    
                    except Exception as e:
                        error_msg = f"Error removing cache file {file_path}: {e}"
                        self.logger.error(error_msg)
                        self.stats['errors'].append(error_msg)
        
        if cache_files_removed > 0:
            self.logger.info(f"Cleaned up {cache_files_removed} cache items")
    
    def _optimize_archives(self, dry_run: bool = False):
        """Optimize archive files by recompressing if beneficial."""
        self.logger.info("Optimizing archives...")
        
        archive_extensions = ['.zip', '.tar', '.tar.gz', '.tar.bz2']
        archives_optimized = 0
        
        for scan_dir in self.config['scan_directories']:
            dir_path = os.path.join(self.project_root, scan_dir)
            if not os.path.exists(dir_path):
                continue
            
            for root, dirs, files in os.walk(dir_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(Path(root) / d)]
                
                for file in files:
                    if any(file.lower().endswith(ext) for ext in archive_extensions):
                        file_path = Path(root) / file
                        
                        try:
                            original_size = file_path.stat().st_size
                            
                            # Skip very small archives
                            if original_size < 1024 * 1024:  # 1MB
                                continue
                            
                            if not dry_run:
                                # For now, just log potential optimization
                                # Actually recompressing archives is risky and would need more sophisticated logic
                                self.logger.info(f"Archive found for potential optimization: {file_path} ({original_size / (1024*1024):.2f} MB)")
                            else:
                                self.logger.info(f"Would analyze archive: {file_path}")
                            
                            archives_optimized += 1
                        
                        except Exception as e:
                            error_msg = f"Error analyzing archive {file_path}: {e}"
                            self.logger.error(error_msg)
                            self.stats['errors'].append(error_msg)
        
        if archives_optimized > 0:
            self.logger.info(f"Analyzed {archives_optimized} archives for optimization")
    
    def _calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate MD5 hash of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def _should_exclude_directory(self, dir_path: Path) -> bool:
        """Check if directory should be excluded from processing."""
        dir_name = dir_path.name
        return any(excluded in dir_name for excluded in self.config['exclude_directories'])
    
    def _generate_optimization_report(self):
        """Generate optimization summary report."""
        self.logger.info("Storage Optimization Summary:")
        self.logger.info(f"  Files scanned: {self.stats['files_scanned']}")
        self.logger.info(f"  Duplicates found: {self.stats['duplicates_found']}")
        self.logger.info(f"  Duplicates removed: {self.stats['duplicates_removed']}")
        self.logger.info(f"  Temp files removed: {self.stats['temp_files_removed']}")
        self.logger.info(f"  Large files found: {self.stats['large_files_found']}")
        self.logger.info(f"  Databases optimized: {self.stats['databases_optimized']}")
        self.logger.info(f"  Total bytes saved: {self.stats['bytes_saved']:,} ({self.stats['bytes_saved'] / (1024*1024):.2f} MB)")
        
        if self.stats['errors']:
            self.logger.warning(f"  Errors encountered: {len(self.stats['errors'])}")
    
    def analyze_storage_usage(self) -> Dict:
        """Analyze current storage usage by category."""
        self.logger.info("Analyzing storage usage...")
        
        usage_analysis = {
            'total_size': 0,
            'categories': {},
            'largest_files': [],
            'directory_sizes': {}
        }
        
        # Analyze each scan directory
        for scan_dir in self.config['scan_directories']:
            dir_path = os.path.join(self.project_root, scan_dir)
            if not os.path.exists(dir_path):
                continue
            
            dir_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(dir_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    try:
                        file_size = file_path.stat().st_size
                        dir_size += file_size
                        file_count += 1
                        
                        # Track largest files
                        usage_analysis['largest_files'].append({
                            'path': str(file_path),
                            'size': file_size,
                            'size_mb': round(file_size / (1024*1024), 2)
                        })
                    
                    except Exception as e:
                        self.logger.error(f"Error analyzing {file_path}: {e}")
            
            usage_analysis['categories'][scan_dir] = {
                'size_bytes': dir_size,
                'size_mb': round(dir_size / (1024*1024), 2),
                'file_count': file_count
            }
            
            usage_analysis['total_size'] += dir_size
        
        # Sort largest files
        usage_analysis['largest_files'].sort(key=lambda x: x['size'], reverse=True)
        usage_analysis['largest_files'] = usage_analysis['largest_files'][:20]  # Keep top 20
        
        return usage_analysis
    
    def get_duplicate_report(self) -> Dict:
        """Generate detailed duplicate file report."""
        self.logger.info("Generating duplicate file report...")
        
        file_hashes = defaultdict(list)
        
        for scan_dir in self.config['scan_directories']:
            dir_path = os.path.join(self.project_root, scan_dir)
            if not os.path.exists(dir_path):
                continue
            
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not self._should_exclude_directory(Path(root) / d)]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    try:
                        if file_path.stat().st_size == 0:
                            continue
                        
                        file_hash = self._calculate_file_hash(file_path)
                        if file_hash:
                            file_hashes[file_hash].append({
                                'path': str(file_path),
                                'size': file_path.stat().st_size,
                                'modified': file_path.stat().st_mtime
                            })
                    
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
        
        # Find duplicates
        duplicates = {}
        total_wasted_space = 0
        
        for file_hash, file_list in file_hashes.items():
            if len(file_list) > 1:
                # Sort by modification time (oldest first)
                file_list.sort(key=lambda x: x['modified'])
                original = file_list[0]
                duplicates_list = file_list[1:]
                
                wasted_space = sum(f['size'] for f in duplicates_list)
                total_wasted_space += wasted_space
                
                duplicates[file_hash] = {
                    'original': original,
                    'duplicates': duplicates_list,
                    'wasted_space': wasted_space
                }
        
        return {
            'duplicate_groups': len(duplicates),
            'total_duplicates': sum(len(group['duplicates']) for group in duplicates.values()),
            'total_wasted_space': total_wasted_space,
            'wasted_space_mb': round(total_wasted_space / (1024*1024), 2),
            'duplicates': duplicates
        }

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit Storage Optimizer')
    parser.add_argument('action', choices=['optimize', 'analyze', 'duplicates', 'cleanup-temp', 'cleanup-old'],
                       help='Action to perform')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--threshold-mb', type=int, default=100,
                       help='Large file threshold in MB')
    parser.add_argument('--old-days', type=int, default=30,
                       help='Old file threshold in days')
    parser.add_argument('--save-report', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    try:
        optimizer = StorageOptimizer()
        
        # Update configuration based on arguments
        if args.threshold_mb:
            optimizer.config['large_file_threshold_mb'] = args.threshold_mb
        if args.old_days:
            optimizer.config['old_file_threshold_days'] = args.old_days
        
        if args.action == 'optimize':
            results = optimizer.optimize_all(dry_run=args.dry_run)
            print(f"\nStorage optimization completed")
            print(f"Space saved: {results['bytes_saved']:,} bytes ({results['bytes_saved'] / (1024*1024):.2f} MB)")
            print(f"Files processed: {results['duplicates_removed']} duplicates + {results['temp_files_removed']} temp files")
        
        elif args.action == 'analyze':
            analysis = optimizer.analyze_storage_usage()
            print(f"\n=== STORAGE USAGE ANALYSIS ===")
            print(f"Total size: {analysis['total_size'] / (1024*1024):.2f} MB")
            print(f"\nBy category:")
            for category, data in analysis['categories'].items():
                print(f"  {category}: {data['size_mb']} MB ({data['file_count']} files)")
        
        elif args.action == 'duplicates':
            duplicate_report = optimizer.get_duplicate_report()
            print(f"\n=== DUPLICATE FILES REPORT ===")
            print(f"Duplicate groups: {duplicate_report['duplicate_groups']}")
            print(f"Total duplicates: {duplicate_report['total_duplicates']}")
            print(f"Wasted space: {duplicate_report['wasted_space_mb']} MB")
        
        elif args.action == 'cleanup-temp':
            optimizer._cleanup_temporary_files(dry_run=args.dry_run)
            print(f"Temp file cleanup completed: {optimizer.stats['temp_files_removed']} files removed")
        
        elif args.action == 'cleanup-old':
            optimizer._cleanup_old_files(dry_run=args.dry_run)
            print(f"Old file cleanup completed")
        
        # Save report if requested
        if args.save_report:
            import json
            report_data = {
                'action': args.action,
                'timestamp': time.time(),
                'stats': optimizer.stats
            }
            
            if args.action == 'analyze':
                report_data['analysis'] = analysis
            elif args.action == 'duplicates':
                report_data['duplicates'] = duplicate_report
            
            with open(args.save_report, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"Report saved to: {args.save_report}")
    
    except Exception as e:
        print(f"Error during storage optimization: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()