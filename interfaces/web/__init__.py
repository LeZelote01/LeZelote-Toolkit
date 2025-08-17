"""
Web Interface Module
====================

Web-based graphical interface for the Pentest-USB Toolkit.
Provides dashboard, project management, and interactive reporting.
"""

from .app import create_app
from . import routes

__all__ = ['create_app', 'routes']