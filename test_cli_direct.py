#!/usr/bin/env python3
"""
Direct CLI Module Testing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_direct_cli_import():
    """Test direct import and execution of CLI modules."""
    print("🧪 Testing Direct CLI Module Imports...")
    
    try:
        # Test main CLI import
        from interfaces.cli.main_cli import PentestCLI
        print("✅ Main CLI import successful")
        
        # Test individual module imports
        from interfaces.cli.module_cli.recon_cli import ReconCLI
        print("✅ Reconnaissance CLI import successful")
        
        from interfaces.cli.module_cli.vuln_cli import VulnCLI
        print("✅ Vulnerability CLI import successful")
        
        from interfaces.cli.module_cli.exploit_cli import ExploitCLI
        print("✅ Exploitation CLI import successful")
        
        from interfaces.cli.module_cli.post_exploit_cli import PostExploitCLI
        print("✅ Post-Exploitation CLI import successful")
        
        from interfaces.cli.module_cli.report_cli import ReportCLI
        print("✅ Reporting CLI import successful")
        
        # Test CLI instantiation
        cli = PentestCLI()
        print("✅ Main CLI instantiation successful")
        
        # Test banner display
        cli.startup_banner()
        print("✅ Banner display successful")
        
        # Test menu display
        cli.show_main_menu()
        print("✅ Menu display successful")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI import/instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_help_systems():
    """Test help systems of individual modules."""
    print("\n🧪 Testing Module Help Systems...")
    
    try:
        # Test Reconnaissance module help
        from interfaces.cli.module_cli.recon_cli import ReconCLI
        recon = ReconCLI()
        print("✅ Reconnaissance module instantiated")
        recon.show_help()
        print("✅ Reconnaissance help displayed")
        
        # Test Vulnerability module help
        from interfaces.cli.module_cli.vuln_cli import VulnCLI
        vuln = VulnCLI()
        print("✅ Vulnerability module instantiated")
        vuln.show_help()
        print("✅ Vulnerability help displayed")
        
        return True
        
    except Exception as e:
        print(f"❌ Module help test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_functionality():
    """Test dashboard functionality."""
    print("\n🧪 Testing Dashboard Functionality...")
    
    try:
        from interfaces.cli.dashboard import Dashboard
        dashboard = Dashboard()
        print("✅ Dashboard import successful")
        
        # Test dashboard layout creation
        layout = dashboard.create_layout()
        print("✅ Dashboard layout creation successful")
        
        # Test system metrics update
        dashboard.update_system_metrics()
        print("✅ System metrics update successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_parser():
    """Test command parser functionality."""
    print("\n🧪 Testing Command Parser...")
    
    try:
        from interfaces.cli.command_parser import CommandParser
        parser = CommandParser()
        print("✅ Command parser import successful")
        
        # Test command parsing
        result = parser.parse("help")
        print(f"✅ Help command parsed: {result}")
        
        result = parser.parse("scan 192.168.1.1")
        print(f"✅ Scan command parsed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Command parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run direct CLI testing."""
    print("🚀 Direct CLI Module Testing")
    print("=" * 50)
    
    tests = [
        ("CLI Import & Instantiation", test_direct_cli_import),
        ("Module Help Systems", test_module_help_systems),
        ("Dashboard Functionality", test_dashboard_functionality),
        ("Command Parser", test_command_parser)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIRECT TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)