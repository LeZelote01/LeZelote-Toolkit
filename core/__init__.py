"""
Pentest-USB Toolkit - Core Module
========================================

Core functionality and engine for the Pentest-USB Toolkit.
Provides orchestration, security, APIs, utilities and database management.

Author: Pentest-USB Development Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Pentest-USB Development Team"

# Import core components
from .engine import orchestrator, task_scheduler, parallel_executor, resource_manager
from .security import stealth_engine, evasion_tactics, consent_manager, crypto_handler
from .utils import file_ops, network_utils, data_parser, logging_handler, error_handler
from .db import sqlite_manager, models

__all__ = [
    'orchestrator',
    'task_scheduler', 
    'parallel_executor',
    'resource_manager',
    'stealth_engine',
    'evasion_tactics',
    'consent_manager',
    'crypto_handler',
    'file_ops',
    'network_utils',
    'data_parser',
    'logging_handler',
    'error_handler',
    'sqlite_manager',
    'models'
]