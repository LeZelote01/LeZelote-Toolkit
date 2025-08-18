"""
Interfaces Package
==================

User interfaces for the Pentest-USB Toolkit.
Provides both Command Line Interface (CLI) and Web Interface.

Components:
- cli/: Command line interface and dashboard
- web/: Web-based graphical interface

Author: Pentest-USB Development Team
Version: 1.0.0
"""

from . import cli
from . import web

__all__ = ['cli', 'web']