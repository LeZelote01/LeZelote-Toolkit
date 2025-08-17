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
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute UPDATE/INSERT/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params or ())
            conn.commit()
            return cursor.rowcount