"""
Web Routes Package
==================

Flask routes for the web interface.
Handles authentication, scanning, reporting, and API endpoints.
"""

from .auth import auth_bp
from .scan import scan_bp
from .report import report_bp
from .api import api_bp
from .projects import projects_bp
from .settings import settings_bp

__all__ = ['auth_bp', 'scan_bp', 'report_bp', 'api_bp', 'projects_bp', 'settings_bp']