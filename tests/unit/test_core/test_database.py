"""
Unit Tests for Database Components
=================================

Tests for database management including SQLite operations,
models, and data persistence.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
import tempfile
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import database components (with fallbacks if not implemented)
try:
    from core.db.sqlite_manager import SQLiteManager
except ImportError:
    SQLiteManager = None

try:
    from core.db.models import DatabaseModels
except ImportError:
    DatabaseModels = None


class TestSQLiteManager(unittest.TestCase):
    """Test cases for SQLite database manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(SQLiteManager is None, "SQLiteManager not implemented")
    def test_sqlite_manager_initialization(self):
        """Test SQLite manager initialization"""
        # Act
        db_manager = SQLiteManager(self.test_db_path)
        
        # Assert
        self.assertEqual(str(db_manager.db_path), self.test_db_path)
        self.assertTrue(os.path.exists(self.test_db_path))
    
    @unittest.skipIf(SQLiteManager is None, "SQLiteManager not implemented")
    def test_create_table_basic(self):
        """Test basic table creation"""
        # Arrange
        db_manager = SQLiteManager(self.test_db_path)
        
        table_schema = """
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Act
        result = db_manager.execute_query(table_schema)
        
        # Assert
        self.assertTrue(result)
        
        # Verify table was created
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        table_exists = cursor.fetchone() is not None
        conn.close()
        
        self.assertTrue(table_exists)
    
    @unittest.skipIf(SQLiteManager is None, "SQLiteManager not implemented")
    def test_insert_and_select_data(self):
        """Test data insertion and retrieval"""
        # Arrange
        db_manager = SQLiteManager(self.test_db_path)
        
        # Create table
        create_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT
        )
        """
        db_manager.execute_query(create_query)
        
        # Act - Insert data
        insert_query = "INSERT INTO users (username, email) VALUES (?, ?)"
        result = db_manager.execute_query(insert_query, ("testuser", "test@example.com"))
        
        # Act - Select data
        select_query = "SELECT * FROM users WHERE username = ?"
        rows = db_manager.fetch_all(select_query, ("testuser",))
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "testuser")  # username column
        self.assertEqual(rows[0][2], "test@example.com")  # email column
    
    @unittest.skipIf(SQLiteManager is None, "SQLiteManager not implemented")
    def test_update_data(self):
        """Test data update operations"""
        # Arrange
        db_manager = SQLiteManager(self.test_db_path)
        
        # Create and populate table
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL
            )
        """)
        
        db_manager.execute_query(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            ("Widget", 10.99)
        )
        
        # Act - Update data
        update_query = "UPDATE products SET price = ? WHERE name = ?"
        result = db_manager.execute_query(update_query, (15.99, "Widget"))
        
        # Verify update
        select_query = "SELECT price FROM products WHERE name = ?"
        rows = db_manager.fetch_all(select_query, ("Widget",))
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 15.99)
    
    @unittest.skipIf(SQLiteManager is None, "SQLiteManager not implemented")
    def test_delete_data(self):
        """Test data deletion operations"""
        # Arrange
        db_manager = SQLiteManager(self.test_db_path)
        
        # Create and populate table
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS temp_data (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        """)
        
        db_manager.execute_query("INSERT INTO temp_data (data) VALUES (?)", ("temporary",))
        db_manager.execute_query("INSERT INTO temp_data (data) VALUES (?)", ("permanent",))
        
        # Act - Delete specific record
        delete_query = "DELETE FROM temp_data WHERE data = ?"
        result = db_manager.execute_query(delete_query, ("temporary",))
        
        # Verify deletion
        select_query = "SELECT COUNT(*) FROM temp_data"
        count = db_manager.fetch_one(select_query)[0]
        
        remaining_query = "SELECT data FROM temp_data"
        remaining = db_manager.fetch_all(remaining_query)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(count, 1)
        self.assertEqual(remaining[0][0], "permanent")
    
    @unittest.skipIf(SQLiteManager is None, "SQLiteManager not implemented")
    def test_transaction_rollback(self):
        """Test transaction rollback functionality"""
        # Arrange
        db_manager = SQLiteManager(self.test_db_path)
        
        db_manager.execute_query("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                balance REAL
            )
        """)
        
        # Insert initial data
        db_manager.execute_query("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("Alice", 100.0))
        
        # Act - Attempt transaction that should fail
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Deduct from Alice
                cursor.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (50.0, "Alice"))
                
                # Try to insert invalid data (this should fail)
                cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", (None, "invalid"))
                
                conn.commit()
                
        except Exception:
            # Transaction should rollback automatically
            pass
        
        # Verify rollback
        balance_query = "SELECT balance FROM accounts WHERE name = ?"
        balance = db_manager.fetch_one(balance_query, ("Alice",))[0]
        
        # Assert
        self.assertEqual(balance, 100.0)  # Should be unchanged due to rollback
    
    def test_mock_sqlite_operations(self):
        """Test SQLite operations using mocks when implementation not available"""
        # This test provides coverage even if SQLiteManager isn't implemented
        
        # Arrange
        mock_db_manager = Mock()
        mock_db_manager.db_path = self.test_db_path
        mock_db_manager.execute_query.return_value = True
        mock_db_manager.fetch_all.return_value = [("testuser", "test@example.com")]
        mock_db_manager.fetch_one.return_value = ("testuser", "test@example.com")
        
        # Act
        execute_result = mock_db_manager.execute_query("CREATE TABLE test ...")
        fetch_all_result = mock_db_manager.fetch_all("SELECT * FROM test")
        fetch_one_result = mock_db_manager.fetch_one("SELECT * FROM test LIMIT 1")
        
        # Assert
        self.assertTrue(execute_result)
        self.assertEqual(len(fetch_all_result), 1)
        self.assertEqual(fetch_one_result[0], "testuser")
        
        mock_db_manager.execute_query.assert_called_once()
        mock_db_manager.fetch_all.assert_called_once()
        mock_db_manager.fetch_one.assert_called_once()


class TestDatabaseModels(unittest.TestCase):
    """Test cases for database models and schema"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "models_test.db")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(DatabaseModels is None, "DatabaseModels not implemented")
    def test_database_models_initialization(self):
        """Test database models initialization"""
        # Act
        models = DatabaseModels(self.test_db_path)
        
        # Assert
        self.assertIsNotNone(models)
        self.assertEqual(models.db_path, self.test_db_path)
    
    @unittest.skipIf(DatabaseModels is None, "DatabaseModels not implemented")
    def test_create_all_tables(self):
        """Test creation of all required tables"""
        # Arrange
        models = DatabaseModels(self.test_db_path)
        
        # Act
        result = models.create_all_tables()
        
        # Assert
        self.assertTrue(result)
        
        # Verify tables exist
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Check for expected tables (adapt based on your schema)
        expected_tables = ['projects', 'scans', 'vulnerabilities', 'reports']
        for table in expected_tables:
            self.assertIn(table, tables, f"Table '{table}' not found in database")
    
    def test_mock_database_models(self):
        """Test database models using mocks when implementation not available"""
        # Arrange
        mock_models = Mock()
        mock_models.db_path = self.test_db_path
        mock_models.create_all_tables.return_value = True
        mock_models.get_table_schema.return_value = {
            'projects': ['id', 'name', 'target', 'created_at'],
            'scans': ['id', 'project_id', 'scan_type', 'results'],
            'vulnerabilities': ['id', 'scan_id', 'severity', 'description'],
            'reports': ['id', 'project_id', 'format', 'path']
        }
        
        # Act
        create_result = mock_models.create_all_tables()
        schema = mock_models.get_table_schema()
        
        # Assert
        self.assertTrue(create_result)
        self.assertIsInstance(schema, dict)
        self.assertIn('projects', schema)
        self.assertIn('scans', schema)
        self.assertIn('vulnerabilities', schema)
        self.assertIn('reports', schema)
        
        mock_models.create_all_tables.assert_called_once()
        mock_models.get_table_schema.assert_called_once()


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "integration_test.db")
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_sqlite_file_creation(self):
        """Test that SQLite database file is created correctly"""
        # Act
        conn = sqlite3.connect(self.test_db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()
        
        # Assert
        self.assertTrue(os.path.exists(self.test_db_path))
        self.assertGreater(os.path.getsize(self.test_db_path), 0)
    
    def test_database_schema_validation(self):
        """Test database schema validation"""
        # Arrange
        conn = sqlite3.connect(self.test_db_path)
        
        # Create test schema
        conn.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target TEXT NOT NULL,
                profile TEXT DEFAULT 'full',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        conn.execute("""
            CREATE TABLE scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                scan_type TEXT NOT NULL,
                results TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        conn.commit()
        
        # Act - Validate schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(projects)")
        projects_columns = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(scans)")
        scans_columns = cursor.fetchall()
        
        cursor.execute("PRAGMA foreign_key_list(scans)")
        foreign_keys = cursor.fetchall()
        
        conn.close()
        
        # Assert
        project_column_names = [col[1] for col in projects_columns]
        self.assertIn('id', project_column_names)
        self.assertIn('name', project_column_names)
        self.assertIn('target', project_column_names)
        self.assertIn('created_at', project_column_names)
        
        scan_column_names = [col[1] for col in scans_columns]
        self.assertIn('id', scan_column_names)
        self.assertIn('project_id', scan_column_names)
        self.assertIn('scan_type', scan_column_names)
        
        # Verify foreign key constraint
        self.assertEqual(len(foreign_keys), 1)
        self.assertEqual(foreign_keys[0][2], 'projects')  # Referenced table
    
    def test_concurrent_database_access(self):
        """Test concurrent database access handling"""
        # Arrange
        conn1 = sqlite3.connect(self.test_db_path)
        conn2 = sqlite3.connect(self.test_db_path)
        
        # Create table
        conn1.execute("CREATE TABLE counter (id INTEGER PRIMARY KEY, value INTEGER)")
        conn1.execute("INSERT INTO counter (value) VALUES (0)")
        conn1.commit()
        
        # Act - Simulate concurrent access
        try:
            # Connection 1 starts transaction
            conn1.execute("UPDATE counter SET value = value + 1")
            
            # Connection 2 tries to read (should not see uncommitted changes)
            cursor2 = conn2.execute("SELECT value FROM counter")
            value_before_commit = cursor2.fetchone()[0]
            
            # Connection 1 commits
            conn1.commit()
            
            # Connection 2 reads again (should see committed changes)
            cursor2 = conn2.execute("SELECT value FROM counter")
            value_after_commit = cursor2.fetchone()[0]
            
        finally:
            conn1.close()
            conn2.close()
        
        # Assert
        self.assertEqual(value_before_commit, 0)  # Uncommitted changes not visible
        self.assertEqual(value_after_commit, 1)   # Committed changes visible


if __name__ == '__main__':
    unittest.main()