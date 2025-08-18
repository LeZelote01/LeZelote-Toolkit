# Routes package for Pentest-USB Toolkit Web Interface

# Import all route modules to make them available
from . import auth, scan, report, api, projects, settings

__all__ = ['auth', 'scan', 'report', 'api', 'projects', 'settings']