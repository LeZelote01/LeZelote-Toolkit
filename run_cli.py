#!/usr/bin/env python3
"""
LeZelote-Toolkit - Main CLI Entry Point
=======================================

This is the main entry point for the LeZelote-Toolkit CLI interface.
It launches the comprehensive penetration testing toolkit.

Usage:
    python3 run_cli.py [options]
    ./run_cli.py [options]
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for LeZelote-Toolkit CLI"""
    try:
        # Import and run the CLI
        from interfaces.cli.main_cli import PentestCLI
        
        # Create and run CLI
        cli = PentestCLI()
        cli.run()
        
    except ImportError as e:
        print(f"❌ Error: Failed to import CLI modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 LeZelote-Toolkit CLI interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()