#!/bin/bash

# Pentest-USB Toolkit - Linux/macOS Launcher
# Version: 1.0.0

echo "===================================="
echo "   Pentest-USB Toolkit Launcher"
echo "===================================="
echo

# Get current directory
TOOLKIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
else
    echo "[ERROR] Unsupported operating system: $OSTYPE"
    exit 1
fi

PYTHON_PATH="$TOOLKIT_ROOT/runtime/python/$OS_TYPE"
TOOLS_PATH="$TOOLKIT_ROOT/tools/binaries/$OS_TYPE"

# Check if portable Python exists
if [ ! -f "$PYTHON_PATH/python3" ]; then
    echo "[ERROR] Portable Python not found!"
    echo "Please run setup.sh first to initialize the toolkit."
    exit 1
fi

# Add tools to PATH
export PATH="$TOOLS_PATH:$PATH"

# Set Python path
export PYTHONPATH="$TOOLKIT_ROOT"

# Change to toolkit directory
cd "$TOOLKIT_ROOT"

# Make tools executable
find "$TOOLS_PATH" -type f -exec chmod +x {} \; 2>/dev/null

echo "[INFO] Starting Pentest-USB Toolkit..."

# Launch the main CLI interface
"$PYTHON_PATH/python3" interfaces/cli/main_cli.py

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to start toolkit!"
    read -p "Press Enter to continue..."
fi