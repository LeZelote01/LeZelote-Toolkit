#!/usr/bin/env python3
"""
Simple launcher script for Pentest-USB Toolkit CLI
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 Launching Pentest-USB Toolkit CLI...")
    
    try:
        from interfaces.cli.main_cli import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error launching CLI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()