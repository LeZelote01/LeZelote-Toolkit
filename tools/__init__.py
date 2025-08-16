"""
Tools Package
=============

External security tools integration for the Pentest-USB Toolkit.
Includes binary executables, Python scripts, and containerized tools.

Directory Structure:
- binaries/: Platform-specific binary executables
- python_scripts/: Custom Python tools and scripts
- containers/: Docker containers for complex tools

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import platform
import subprocess
from pathlib import Path

# Get current platform
CURRENT_OS = platform.system().lower()
if CURRENT_OS == "darwin":
    CURRENT_OS = "macos"

# Tool paths
TOOLS_ROOT = Path(__file__).parent
BINARIES_PATH = TOOLS_ROOT / "binaries" / CURRENT_OS
PYTHON_SCRIPTS_PATH = TOOLS_ROOT / "python_scripts"
CONTAINERS_PATH = TOOLS_ROOT / "containers"

def get_tool_path(tool_name):
    """Get the path to a specific tool binary."""
    if CURRENT_OS == "windows":
        tool_path = BINARIES_PATH / f"{tool_name}.exe"
    else:
        tool_path = BINARIES_PATH / tool_name
    
    return tool_path if tool_path.exists() else None

def is_tool_available(tool_name):
    """Check if a tool is available on the current platform."""
    return get_tool_path(tool_name) is not None

__all__ = ['get_tool_path', 'is_tool_available', 'TOOLS_ROOT', 'BINARIES_PATH']