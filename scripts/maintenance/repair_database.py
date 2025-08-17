#!/usr/bin/env python3
"""
LeZelote-Toolkit - Database Repair and Recovery Utility
=====================================================

This script provides comprehensive database repair and recovery for the
Pentest-USB Toolkit, including:
- SQLite database integrity checking
- Automatic repair procedures
- Backup and recovery operations
- Index rebuilding
- Schema validation
- Data migration tools

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import sqlite3
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import argparse
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging
from core.db.sqlite_manager import DatabaseManager

# Simple helper functions
def safe_copy_file(src: str, dst: str) -> bool:
    """Safely copy a file."""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

class DatabaseRepairer:
    """Comprehensive database repair and recovery system."""
    
    def __init__(self):
        """Initialize the database repairer."""
        self.logger = setup_logging(__name__)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        self.repair_stats = {
            'databases_found': 0,
            'databases_checked': 0,
            'databases_repaired': 0,
            'databases_recovered': 0,
            'integrity_errors': 0,
            'schema_errors': 0,
            'backup_created': 0,
            'errors': []
        }
        
        # Expected database schema definitions
        self.expected_schemas = {
            'knowledge_base.db': {
                'tables': ['projects', 'scans', 'vulnerabilities', 'reports'],
                'indexes': ['idx_projects_name', 'idx_scans_timestamp', 'idx_vulns_severity']
            }
        }
    
    def repair_all_databases(self, create_backup: bool = True) -> Dict:
        """Repair all databases in the project."""
        self.logger.info("Starting comprehensive database repair...")
        
        # Find all database files
        db_files = self._find_database_files()
        
        for db_path in db_files:
            try:
                self.repair_database(db_path, create_backup)
            except Exception as e:
                error_msg = f"Failed to repair database {db_path}: {e}"
                self.logger.error(error_msg)
                self.repair_stats['errors'].append(error_msg)
        
        self._generate_repair_report()
        return self.repair_stats
    
    def repair_database(self, db_path: str, create_backup: bool = True) -> bool:
        """Repair a specific database file."""
        self.logger.info(f"Repairing database: {os.path.basename(db_path)}")
        
        if not os.path.exists(db_path):
            self.logger.error(f"Database file not found: {db_path}")
            return False
        
        self.repair_stats['databases_found'] += 1
        
        # Create backup if requested
        backup_path = None
        if create_backup:
            backup_path = self._create_backup(db_path)
            if backup_path:
                self.repair_stats['backup_created'] += 1
        
        try:
            # Check database accessibility
            if not self._check_database_accessibility(db_path):
                self.logger.error(f"Database is not accessible: {db_path}")
                return False
            
            # Perform integrity check
            integrity_issues = self._check_database_integrity(db_path)
            
            if integrity_issues:
                self.repair_stats['integrity_errors'] += len(integrity_issues)
                
                # Attempt to repair integrity issues
                if self._repair_integrity_issues(db_path, integrity_issues):
                    self.logger.info(f"Successfully repaired integrity issues in {db_path}")
                    self.repair_stats['databases_repaired'] += 1
                else:
                    # Try recovery from backup if repair fails
                    if backup_path and self._recover_from_backup(db_path, backup_path):
                        self.logger.info(f"Recovered database from backup: {db_path}")
                        self.repair_stats['databases_recovered'] += 1
                    else:
                        self.logger.error(f"Failed to repair or recover database: {db_path}")
                        return False
            
            # Check and repair schema
            schema_issues = self._check_schema(db_path)
            if schema_issues:
                self.repair_stats['schema_errors'] += len(schema_issues)
                self._repair_schema_issues(db_path, schema_issues)
            
            # Rebuild indexes
            self._rebuild_indexes(db_path)
            
            # Optimize database
            self._optimize_database(db_path)
            
            # Final verification
            if self._verify_database_health(db_path):
                self.logger.info(f"Database repair completed successfully: {db_path}")
                self.repair_stats['databases_checked'] += 1
                return True
            else:
                self.logger.error(f"Database verification failed after repair: {db_path}")
                return False
        
        except Exception as e:
            error_msg = f"Error during database repair {db_path}: {e}"
            self.logger.error(error_msg)
            self.repair_stats['errors'].append(error_msg)
            return False
    
    def _find_database_files(self) -> List[str]:
        """Find all database files in the project."""
        db_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_path = os.path.join(root, file)
                    db_files.append(db_path)
        
        self.logger.info(f"Found {len(db_files)} database files")
        return db_files
    
    def _create_backup(self, db_path: str) -> Optional[str]:
        """Create a backup of the database file."""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(db_path)}.backup_{timestamp}"
            backup_path = os.path.join(os.path.dirname(db_path), backup_name)
            
            if safe_copy_file(db_path, backup_path):
                self.logger.info(f"Created backup: {backup_path}")
                return backup_path
            else:
                self.logger.error(f"Failed to create backup for {db_path}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error creating backup for {db_path}: {e}")
            return None
    
    def _check_database_accessibility(self, db_path: str) -> bool:
        """Check if database file is accessible."""
        try:
            # Try to connect to the database
            with sqlite3.connect(db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                self.logger.warning(f"Database is locked: {db_path}")
                # Try to wait and retry
                time.sleep(2)
                try:
                    with sqlite3.connect(db_path, timeout=10) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        return True
                except:
                    return False
            else:
                self.logger.error(f"Database operational error: {e}")
                return False
        
        except Exception as e:
            self.logger.error(f"Cannot access database {db_path}: {e}")
            return False
    
    def _check_database_integrity(self, db_path: str) -> List[str]:
        """Check database integrity and return list of issues."""
        issues = []
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Run integrity check
                cursor.execute("PRAGMA integrity_check")
                results = cursor.fetchall()
                
                for result in results:
                    if result[0] != 'ok':
                        issues.append(result[0])
                        self.logger.warning(f"Integrity issue in {db_path}: {result[0]}")
                
                # Check for quick check
                cursor.execute("PRAGMA quick_check")
                quick_results = cursor.fetchall()
                
                for result in quick_results:
                    if result[0] != 'ok':
                        if result[0] not in issues:
                            issues.append(result[0])
                            self.logger.warning(f"Quick check issue in {db_path}: {result[0]}")
        
        except Exception as e:
            issues.append(f"Cannot perform integrity check: {e}")
            self.logger.error(f"Error checking integrity of {db_path}: {e}")
        
        return issues
    
    def _repair_integrity_issues(self, db_path: str, issues: List[str]) -> bool:
        """Attempt to repair database integrity issues."""
        try:
            # Create a recovery database
            recovery_path = f"{db_path}.recovery"
            
            with sqlite3.connect(db_path) as source_conn:
                with sqlite3.connect(recovery_path) as recovery_conn:
                    
                    # Get list of tables
                    cursor = source_conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        try:
                            # Get table schema
                            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name=?", (table,))
                            schema_result = cursor.fetchone()
                            
                            if schema_result and schema_result[0]:
                                # Create table in recovery database
                                recovery_conn.execute(schema_result[0])
                                
                                # Copy data that can be read
                                cursor.execute(f"SELECT * FROM {table}")
                                rows = cursor.fetchall()
                                
                                if rows:
                                    placeholders = ','.join(['?' for _ in range(len(rows[0]))])
                                    recovery_conn.executemany(
                                        f"INSERT INTO {table} VALUES ({placeholders})", 
                                        rows
                                    )
                                
                                self.logger.info(f"Recovered table: {table}")
                        
                        except Exception as e:
                            self.logger.warning(f"Could not recover table {table}: {e}")
                            continue
                    
                    # Copy indexes and views
                    cursor.execute("SELECT sql FROM sqlite_master WHERE type IN ('index', 'view') AND sql IS NOT NULL")
                    for (sql,) in cursor.fetchall():
                        try:
                            recovery_conn.execute(sql)
                        except Exception as e:
                            self.logger.warning(f"Could not recreate index/view: {e}")
            
            # Replace original with recovered database
            if os.path.exists(recovery_path):
                shutil.move(recovery_path, db_path)
                self.logger.info(f"Database repaired using recovery method: {db_path}")
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to repair integrity issues in {db_path}: {e}")
            # Clean up recovery file
            recovery_path = f"{db_path}.recovery"
            if os.path.exists(recovery_path):
                os.remove(recovery_path)
        
        return False
    
    def _recover_from_backup(self, db_path: str, backup_path: str) -> bool:
        """Recover database from backup."""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, db_path)
                self.logger.info(f"Database recovered from backup: {db_path}")
                return True
            else:
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to recover from backup {backup_path}: {e}")
            return False
    
    def _check_schema(self, db_path: str) -> List[str]:
        """Check database schema against expected schema."""
        issues = []
        db_name = os.path.basename(db_path)
        
        if db_name not in self.expected_schemas:
            return issues  # No expected schema defined
        
        expected = self.expected_schemas[db_name]
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Check tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = set(row[0] for row in cursor.fetchall())
                expected_tables = set(expected.get('tables', []))
                
                missing_tables = expected_tables - existing_tables
                for table in missing_tables:
                    issues.append(f"Missing table: {table}")
                
                # Check indexes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
                existing_indexes = set(row[0] for row in cursor.fetchall() if row[0])
                expected_indexes = set(expected.get('indexes', []))
                
                missing_indexes = expected_indexes - existing_indexes
                for index in missing_indexes:
                    issues.append(f"Missing index: {index}")
        
        except Exception as e:
            issues.append(f"Cannot check schema: {e}")
        
        return issues
    
    def _repair_schema_issues(self, db_path: str, issues: List[str]):
        """Repair schema issues."""
        db_name = os.path.basename(db_path)
        
        if db_name not in self.expected_schemas:
            return
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Create missing tables (basic schema - would need to be customized)
                for issue in issues:
                    if issue.startswith("Missing table:"):
                        table_name = issue.split(": ")[1]
                        self._create_default_table(cursor, table_name)
                    
                    elif issue.startswith("Missing index:"):
                        index_name = issue.split(": ")[1]
                        self._create_default_index(cursor, index_name)
                
                conn.commit()
                self.logger.info(f"Schema issues repaired for {db_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to repair schema issues in {db_path}: {e}")
    
    def _create_default_table(self, cursor: sqlite3.Cursor, table_name: str):
        """Create a default table structure."""
        # Basic table schemas - would need customization for real use
        table_schemas = {
            'projects': '''
                CREATE TABLE projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'scans': '''
                CREATE TABLE scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    target TEXT NOT NULL,
                    scan_type TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''',
            'vulnerabilities': '''
                CREATE TABLE vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT,
                    cvss_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                )
            ''',
            'reports': '''
                CREATE TABLE reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    title TEXT NOT NULL,
                    format TEXT,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            '''
        }
        
        if table_name in table_schemas:
            cursor.execute(table_schemas[table_name])
            self.logger.info(f"Created missing table: {table_name}")
    
    def _create_default_index(self, cursor: sqlite3.Cursor, index_name: str):
        """Create a default index."""
        index_definitions = {
            'idx_projects_name': 'CREATE INDEX idx_projects_name ON projects (name)',
            'idx_scans_timestamp': 'CREATE INDEX idx_scans_timestamp ON scans (created_at)',
            'idx_vulns_severity': 'CREATE INDEX idx_vulns_severity ON vulnerabilities (severity)'
        }
        
        if index_name in index_definitions:
            cursor.execute(index_definitions[index_name])
            self.logger.info(f"Created missing index: {index_name}")
    
    def _rebuild_indexes(self, db_path: str):
        """Rebuild database indexes."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Reindex all indexes
                cursor.execute("REINDEX")
                
                # Update statistics
                cursor.execute("ANALYZE")
                
                self.logger.info(f"Indexes rebuilt for {db_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to rebuild indexes for {db_path}: {e}")
    
    def _optimize_database(self, db_path: str):
        """Optimize database performance."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Vacuum to reclaim space
                cursor.execute("VACUUM")
                
                # Update query planner statistics
                cursor.execute("ANALYZE")
                
                # Set pragmas for better performance
                cursor.execute("PRAGMA optimize")
                
                self.logger.info(f"Database optimized: {db_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to optimize database {db_path}: {e}")
    
    def _verify_database_health(self, db_path: str) -> bool:
        """Verify database health after repair."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Quick integrity check
                cursor.execute("PRAGMA quick_check")
                result = cursor.fetchone()
                
                if result and result[0] == 'ok':
                    # Test basic operations
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                    cursor.fetchone()
                    
                    self.logger.info(f"Database health verification passed: {db_path}")
                    return True
                else:
                    self.logger.error(f"Database health verification failed: {db_path}")
                    return False
        
        except Exception as e:
            self.logger.error(f"Cannot verify database health {db_path}: {e}")
            return False
    
    def _generate_repair_report(self):
        """Generate repair summary report."""
        self.logger.info("Database Repair Summary:")
        self.logger.info(f"  Databases found: {self.repair_stats['databases_found']}")
        self.logger.info(f"  Databases checked: {self.repair_stats['databases_checked']}")
        self.logger.info(f"  Databases repaired: {self.repair_stats['databases_repaired']}")
        self.logger.info(f"  Databases recovered: {self.repair_stats['databases_recovered']}")
        self.logger.info(f"  Integrity errors: {self.repair_stats['integrity_errors']}")
        self.logger.info(f"  Schema errors: {self.repair_stats['schema_errors']}")
        self.logger.info(f"  Backups created: {self.repair_stats['backup_created']}")
        
        if self.repair_stats['errors']:
            self.logger.warning(f"  Errors encountered: {len(self.repair_stats['errors'])}")
            for error in self.repair_stats['errors']:
                self.logger.warning(f"    {error}")
    
    def check_all_databases(self) -> Dict:
        """Check all databases without repairing."""
        self.logger.info("Checking all databases...")
        
        db_files = self._find_database_files()
        check_results = {}
        
        for db_path in db_files:
            db_name = os.path.basename(db_path)
            
            result = {
                'path': db_path,
                'accessible': False,
                'integrity_issues': [],
                'schema_issues': [],
                'size_mb': 0,
                'table_count': 0
            }
            
            try:
                # Check accessibility
                result['accessible'] = self._check_database_accessibility(db_path)
                
                if result['accessible']:
                    # Check integrity
                    result['integrity_issues'] = self._check_database_integrity(db_path)
                    
                    # Check schema
                    result['schema_issues'] = self._check_schema(db_path)
                    
                    # Get database info
                    result['size_mb'] = round(os.path.getsize(db_path) / (1024*1024), 2)
                    
                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        result['table_count'] = cursor.fetchone()[0]
                
                check_results[db_name] = result
            
            except Exception as e:
                result['error'] = str(e)
                check_results[db_name] = result
        
        return check_results
    
    def migrate_database_schema(self, db_path: str, migration_script: str) -> bool:
        """Apply database schema migration."""
        try:
            backup_path = self._create_backup(db_path)
            if not backup_path:
                self.logger.error("Cannot create backup before migration")
                return False
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Execute migration script
                cursor.executescript(migration_script)
                
                # Verify migration
                if self._verify_database_health(db_path):
                    self.logger.info(f"Database migration completed: {db_path}")
                    return True
                else:
                    # Rollback to backup
                    self._recover_from_backup(db_path, backup_path)
                    self.logger.error("Migration failed, rolled back to backup")
                    return False
        
        except Exception as e:
            self.logger.error(f"Migration failed for {db_path}: {e}")
            return False

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit Database Repair Utility')
    parser.add_argument('action', choices=['repair', 'check', 'recover', 'optimize'],
                       help='Action to perform')
    parser.add_argument('--database', help='Specific database file to repair')
    parser.add_argument('--backup-path', help='Backup file for recovery')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--migration-script', help='SQL migration script file')
    parser.add_argument('--save-report', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    try:
        repairer = DatabaseRepairer()
        
        if args.action == 'repair':
            if args.database:
                # Repair specific database
                success = repairer.repair_database(args.database, not args.no_backup)
                if success:
                    print(f"Database repair completed: {args.database}")
                else:
                    print(f"Database repair failed: {args.database}")
                    sys.exit(1)
            else:
                # Repair all databases
                results = repairer.repair_all_databases(not args.no_backup)
                print(f"Database repair completed")
                print(f"Repaired: {results['databases_repaired']} databases")
                print(f"Recovered: {results['databases_recovered']} databases")
        
        elif args.action == 'check':
            if args.database:
                # Check specific database
                issues = repairer._check_database_integrity(args.database)
                print(f"Database check results for {args.database}:")
                if issues:
                    for issue in issues:
                        print(f"  ISSUE: {issue}")
                else:
                    print("  No issues found")
            else:
                # Check all databases
                results = repairer.check_all_databases()
                print("\n=== DATABASE CHECK RESULTS ===")
                for db_name, result in results.items():
                    print(f"{db_name}:")
                    print(f"  Accessible: {result['accessible']}")
                    print(f"  Size: {result['size_mb']} MB")
                    print(f"  Tables: {result['table_count']}")
                    if result['integrity_issues']:
                        print(f"  Integrity issues: {len(result['integrity_issues'])}")
                    if result['schema_issues']:
                        print(f"  Schema issues: {len(result['schema_issues'])}")
        
        elif args.action == 'recover':
            if not args.database or not args.backup_path:
                print("Error: --database and --backup-path required for recovery", file=sys.stderr)
                sys.exit(1)
            
            success = repairer._recover_from_backup(args.database, args.backup_path)
            if success:
                print(f"Database recovered from backup: {args.database}")
            else:
                print(f"Database recovery failed: {args.database}")
                sys.exit(1)
        
        elif args.action == 'optimize':
            if args.database:
                repairer._optimize_database(args.database)
                print(f"Database optimized: {args.database}")
            else:
                db_files = repairer._find_database_files()
                for db_path in db_files:
                    repairer._optimize_database(db_path)
                print(f"Optimized {len(db_files)} databases")
        
        # Save report if requested
        if args.save_report:
            with open(args.save_report, 'w') as f:
                json.dump(repairer.repair_stats, f, indent=2)
            print(f"Report saved to: {args.save_report}")
    
    except Exception as e:
        print(f"Error during database repair operation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()