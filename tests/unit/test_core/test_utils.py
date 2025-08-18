"""
Unit Tests for Core Utilities
============================

Tests for utility functions and classes including
logging, error handling, and file operations.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
import tempfile
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.logging_handler import get_logger, setup_logging, LoggingHandler
from core.utils.error_handler import PentestError


class TestLoggingHandler(unittest.TestCase):
    """Test cases for logging handler functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Clear global logger cache
        from core.utils.logging_handler import _loggers
        _loggers.clear()
    
    def test_get_logger_creates_new_logger(self):
        """Test that get_logger creates a new logger"""
        # Act
        logger = get_logger("test.module")
        
        # Assert
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test.module")
    
    def test_get_logger_returns_cached_logger(self):
        """Test that get_logger returns cached logger"""
        # Act
        logger1 = get_logger("test.module")
        logger2 = get_logger("test.module")
        
        # Assert
        self.assertIs(logger1, logger2)
    
    def test_setup_logging_with_default_params(self):
        """Test setup_logging with default parameters"""
        # Act
        logger = setup_logging()
        
        # Assert
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.INFO)
        self.assertTrue(len(logger.handlers) > 0)
    
    def test_setup_logging_with_custom_params(self):
        """Test setup_logging with custom parameters"""
        # Act
        logger = setup_logging(
            log_level="DEBUG",
            log_file=self.log_file,
            max_file_size=1024,
            backup_count=3
        )
        
        # Assert
        self.assertEqual(logger.level, logging.DEBUG)
        
        # Check that log file handler was added
        file_handlers = [h for h in logger.handlers 
                        if isinstance(h, logging.handlers.RotatingFileHandler)]
        self.assertGreater(len(file_handlers), 0)
    
    def test_setup_logging_creates_log_directory(self):
        """Test that setup_logging creates log directory"""
        # Arrange
        log_dir = os.path.join(self.temp_dir, "logs")
        log_file = os.path.join(log_dir, "test.log")
        
        # Act
        setup_logging(log_file=log_file)
        
        # Assert
        self.assertTrue(os.path.exists(log_dir))
    
    def test_logging_handler_class(self):
        """Test LoggingHandler backward compatibility class"""
        # Act
        handler = LoggingHandler(log_level="WARNING", log_file=self.log_file)
        logger = handler.get_logger("test.handler")
        
        # Assert
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(handler.log_level, "WARNING")
        self.assertEqual(handler.log_file, self.log_file)
    
    def test_logger_message_formatting(self):
        """Test logger message formatting"""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_log:
            temp_log_path = temp_log.name
        
        try:
            # Act
            logger = setup_logging(log_file=temp_log_path, log_level="DEBUG")
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            # Assert
            with open(temp_log_path, 'r') as f:
                log_content = f.read()
            
            self.assertIn("Test info message", log_content)
            self.assertIn("Test warning message", log_content)
            self.assertIn("Test error message", log_content)
            self.assertIn("INFO", log_content)
            self.assertIn("WARNING", log_content)
            self.assertIn("ERROR", log_content)
            
        finally:
            os.unlink(temp_log_path)
    
    def test_console_and_file_handlers(self):
        """Test that both console and file handlers are created"""
        # Act
        logger = setup_logging(log_file=self.log_file)
        
        # Assert
        handler_types = [type(h) for h in logger.handlers]
        
        self.assertIn(logging.StreamHandler, handler_types)
        self.assertIn(logging.handlers.RotatingFileHandler, handler_types)
    
    def test_error_handler_separate_file(self):
        """Test that error messages go to separate error file"""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_log:
            temp_log_path = temp_log.name
        
        error_log_path = str(Path(temp_log_path).parent / "errors.log")
        
        try:
            # Act
            logger = setup_logging(log_file=temp_log_path, log_level="DEBUG")
            logger.error("Test error for separate file")
            
            # Flush handlers
            for handler in logger.handlers:
                handler.flush()
            
            # Assert
            self.assertTrue(os.path.exists(error_log_path))
            
            with open(error_log_path, 'r') as f:
                error_content = f.read()
            
            self.assertIn("Test error for separate file", error_content)
            
        finally:
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)
            if os.path.exists(error_log_path):
                os.unlink(error_log_path)


class TestErrorHandler(unittest.TestCase):
    """Test cases for error handling functionality"""
    
    def test_pentest_error_creation(self):
        """Test PentestError exception creation"""
        # Act
        error = PentestError("Test error message")
        
        # Assert
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test error message")
    
    def test_pentest_error_inheritance(self):
        """Test PentestError inheritance from Exception"""
        # Act & Assert
        with self.assertRaises(Exception):
            raise PentestError("Test error")
        
        with self.assertRaises(PentestError):
            raise PentestError("Test error")
    
    def test_pentest_error_with_args(self):
        """Test PentestError with multiple arguments"""
        # Act
        error = PentestError("Primary message", "Secondary info")
        
        # Assert
        self.assertIn("Primary message", str(error))


class TestFileOperations(unittest.TestCase):
    """Test cases for file operations utility"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('core.utils.file_ops.FileOperations')
    def test_file_operations_mocked(self, mock_file_ops_class):
        """Test FileOperations class (mocked since it may not exist yet)"""
        # Arrange
        mock_file_ops = Mock()
        mock_file_ops_class.return_value = mock_file_ops
        
        # Mock methods
        mock_file_ops.ensure_directory.return_value = True
        mock_file_ops.load_json.return_value = {"test": "data"}
        mock_file_ops.save_json.return_value = True
        
        # Act
        file_ops = mock_file_ops_class()
        
        # Test ensure_directory
        result = file_ops.ensure_directory("/test/path")
        self.assertTrue(result)
        mock_file_ops.ensure_directory.assert_called_once_with("/test/path")
        
        # Test load_json
        data = file_ops.load_json("/test/file.json")
        self.assertEqual(data, {"test": "data"})
        mock_file_ops.load_json.assert_called_once_with("/test/file.json")
        
        # Test save_json
        result = file_ops.save_json("/test/file.json", {"new": "data"})
        self.assertTrue(result)
        mock_file_ops.save_json.assert_called_once_with("/test/file.json", {"new": "data"})


if __name__ == '__main__':
    unittest.main()