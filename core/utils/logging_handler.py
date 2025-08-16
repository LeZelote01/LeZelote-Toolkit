"""
Pentest-USB Toolkit - Logging Handler
====================================

Centralized logging system with rotation, formatting,
and multiple output destinations.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Global logger cache
_loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get or create a logger with standardized configuration
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        setup_logging(logger)
    
    _loggers[name] = logger
    return logger


def setup_logging(logger: Optional[logging.Logger] = None, 
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5) -> logging.Logger:
    """
    Setup comprehensive logging configuration
    
    Args:
        logger: Logger instance (creates root if None)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path (uses default if None)
        max_file_size: Maximum file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger
    """
    if logger is None:
        logger = logging.getLogger()
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set log level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)8s | %(name)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file is None:
        log_dir = Path("/app/logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "pentest_toolkit.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = Path(log_file).parent / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_log_file,
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    logger.info(f"Logging system initialized - Level: {log_level}")
    return logger