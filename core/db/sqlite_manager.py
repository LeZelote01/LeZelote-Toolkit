"""
Pentest-USB Toolkit - SQLite Manager
===================================

SQLite database management with CRUD operations,
transactions and connection pooling.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import sys

# Fix imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.logging_handler import get_logger
from core.utils.error_handler import PentestError
from core.utils.file_ops import FileOperations


class SQLiteManager:
    """
    SQLite database manager with connection pooling
    """
    
    def __init__(self, db_path: str):
        """Initialize SQLite manager"""
        self.db_path = Path(db_path)
        self.logger = get_logger(__name__)
        self.file_ops = FileOperations()
        
        # Ensure database directory exists
        self.file_ops.ensure_directory(self.db_path.parent)
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Initialize database
        self._init_database()
        
        self.logger.info(f"SQLiteManager initialized: {self.db_path}")
    
    def _init_database(self):
        """Initialize database with basic schema"""
        with self.get_connection() as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Create basic tables if they don't exist
            self._create_basic_tables(conn)
    
    def _create_basic_tables(self, conn: sqlite3.Connection):
        """Create basic database tables"""
        # Projects table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                profile TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Scan results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                module TEXT NOT NULL,
                target TEXT NOT NULL,
                result_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        
        try:
            yield self._local.connection
        except Exception as e:
            self._local.connection.rollback()
            raise PentestError(f"Database operation failed: {str(e)}")
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute any SQL query and return appropriate result"""
        query_type = query.strip().upper()
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            
            if query_type.startswith(('SELECT', 'PRAGMA')):
                # For SELECT queries, return results
                return [dict(row) for row in cursor.fetchall()]
            else:
                # For CREATE, INSERT, UPDATE, DELETE queries, commit and return success
                conn.commit()
                return True
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute UPDATE/INSERT/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
    
    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Execute SELECT query and return all results as tuples"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchall()
    
    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[tuple]:
        """Execute SELECT query and return first result as tuple"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return cursor.fetchone()
    
    def initialize_database(self) -> bool:
        """Initialize database with all required tables and data"""
        try:
            self.logger.info("Initializing database...")
            
            with self.get_connection() as conn:
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create all required tables
                self._create_projects_table(conn)
                self._create_hosts_table(conn)
                self._create_ports_table(conn)
                self._create_vulnerabilities_table(conn)
                self._create_scan_results_table(conn)
                
                conn.commit()
            
            self.logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
            raise PentestError(f"Database initialization failed: {str(e)}")
    
    def migrate_database(self) -> Dict[str, Any]:
        """Migrate database schema to latest version"""
        try:
            self.logger.info("Starting database migration...")
            
            migration_result = {
                'success': True,
                'migrations_applied': [],
                'current_version': '1.0.0'
            }
            
            with self.get_connection() as conn:
                # Check current version
                try:
                    version_row = conn.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1").fetchone()
                    current_version = version_row[0] if version_row else '0.0.0'
                except:
                    # Schema version table doesn't exist, create it
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS schema_version (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            version TEXT NOT NULL,
                            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    current_version = '0.0.0'
                
                # Apply migrations based on current version
                if current_version < '1.0.0':
                    self._apply_migration_1_0_0(conn)
                    migration_result['migrations_applied'].append('1.0.0')
                
                # Update schema version
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    ('1.0.0',)
                )
                
                conn.commit()
            
            self.logger.info("Database migration completed successfully")
            return migration_result
            
        except Exception as e:
            self.logger.error(f"Database migration failed: {str(e)}")
            raise PentestError(f"Database migration failed: {str(e)}")
    
    def _create_projects_table(self, conn: sqlite3.Connection):
        """Create projects table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                profile TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                description TEXT,
                tags TEXT
            )
        """)
    
    def _create_hosts_table(self, conn: sqlite3.Connection):
        """Create hosts table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                ip_address TEXT NOT NULL,
                hostname TEXT,
                os_family TEXT,
                os_version TEXT,
                status TEXT DEFAULT 'up',
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
    
    def _create_ports_table(self, conn: sqlite3.Connection):
        """Create ports table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ports (
                id TEXT PRIMARY KEY,
                host_id TEXT,
                port_number INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                state TEXT NOT NULL,
                service_name TEXT,
                service_version TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES hosts (id)
            )
        """)
    
    def _create_vulnerabilities_table(self, conn: sqlite3.Connection):
        """Create vulnerabilities table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id TEXT PRIMARY KEY,
                host_id TEXT,
                port_id TEXT,
                vuln_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                cvss_score REAL,
                cve_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                solution TEXT,
                proof_of_concept TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES hosts (id),
                FOREIGN KEY (port_id) REFERENCES ports (id)
            )
        """)
    
    def _create_scan_results_table(self, conn: sqlite3.Connection):
        """Create scan results table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                module TEXT NOT NULL,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                result_data TEXT,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
    
    def _apply_migration_1_0_0(self, conn: sqlite3.Connection):
        """Apply migration to version 1.0.0"""
        # Add new columns to existing tables if they don't exist
        try:
            conn.execute("ALTER TABLE projects ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            conn.execute("ALTER TABLE projects ADD COLUMN description TEXT")
        except sqlite3.OperationalError:
            pass
        
        try:
            conn.execute("ALTER TABLE projects ADD COLUMN tags TEXT")
        except sqlite3.OperationalError:
            pass
    
    def get_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get projects for a specific user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT id, name, target, profile, created_at, updated_at, status, description, tags
                    FROM projects 
                    ORDER BY updated_at DESC
                """)
                
                projects = []
                for row in cursor.fetchall():
                    projects.append({
                        'id': row[0],
                        'name': row[1],
                        'target': row[2],
                        'profile': row[3],
                        'created_at': row[4],
                        'updated_at': row[5],
                        'status': row[6],
                        'description': row[7],
                        'tags': row[8]
                    })
                
                return projects
                
        except Exception as e:
            self.logger.error(f"Error getting user projects: {str(e)}")
            return []
    
    def get_user_reports(self, user_id: str) -> List[Dict[str, Any]]:
        """Get reports for a specific user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT sr.id, sr.project_id, sr.module, sr.target, sr.scan_type, 
                           sr.status, sr.created_at, sr.duration, p.name as project_name
                    FROM scan_results sr
                    LEFT JOIN projects p ON sr.project_id = p.id
                    WHERE sr.status = 'completed'
                    ORDER BY sr.created_at DESC
                """)
                
                reports = []
                for row in cursor.fetchall():
                    reports.append({
                        'id': row[0],
                        'project_id': row[1],
                        'module': row[2],
                        'target': row[3],
                        'scan_type': row[4],
                        'status': row[5],
                        'created_at': row[6],
                        'duration': row[7],
                        'project_name': row[8]
                    })
                
                return reports
                
        except Exception as e:
            self.logger.error(f"Error getting user reports: {str(e)}")
            return []
    
    def get_recent_scans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scans"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT sr.id, sr.project_id, sr.module, sr.target, sr.scan_type, 
                           sr.status, sr.created_at, sr.duration, p.name as project_name
                    FROM scan_results sr
                    LEFT JOIN projects p ON sr.project_id = p.id
                    ORDER BY sr.created_at DESC
                    LIMIT ?
                """, (limit,))
                
                scans = []
                for row in cursor.fetchall():
                    scans.append({
                        'id': row[0],
                        'project_id': row[1],
                        'module': row[2],
                        'target': row[3],
                        'scan_type': row[4],
                        'status': row[5],
                        'created_at': row[6],
                        'duration': row[7],
                        'project_name': row[8]
                    })
                
                return scans
                
        except Exception as e:
            self.logger.error(f"Error getting recent scans: {str(e)}")
            return []
    
    def save_scan_results(self, scan_info: Dict[str, Any]) -> bool:
        """Save scan results to database"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO scan_results (id, project_id, module, target, scan_type, 
                                            result_data, status, created_at, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scan_info.get('id'),
                    scan_info.get('project_id'),
                    'web_scanner',
                    scan_info.get('target'),
                    scan_info.get('scan_type'),
                    str(scan_info.get('vulnerabilities', [])),
                    scan_info.get('status'),
                    scan_info.get('started_at'),
                    scan_info.get('duration', 0)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving scan results: {str(e)}")
            return False


# Alias pour la compatibilité
DatabaseManager = SQLiteManager