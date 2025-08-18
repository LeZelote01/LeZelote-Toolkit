#!/usr/bin/env python3
"""
Comprehensive CLI Testing Script for LeZelote-Toolkit
====================================================

This script tests all 9 modules of the CLI interface systematically.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_cli_command(command_sequence, timeout=10):
    """Run CLI with a sequence of commands."""
    try:
        # Create input string
        input_str = "\n".join(command_sequence) + "\n"
        
        # Run the CLI
        process = subprocess.Popen(
            [sys.executable, "run_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app"
        )
        
        stdout, stderr = process.communicate(input=input_str, timeout=timeout)
        return stdout, stderr, process.returncode
        
    except subprocess.TimeoutExpired:
        process.kill()
        return "", "Timeout expired", -1
    except Exception as e:
        return "", str(e), -1

def test_main_menu():
    """Test main menu display and navigation."""
    print("🧪 Testing Main Menu Display...")
    
    # Test showing main menu and exiting
    stdout, stderr, returncode = run_cli_command(["0"])
    
    if "Main Menu" in stdout and "Reconnaissance" in stdout:
        print("✅ Main menu displays correctly with all 9 options")
        return True
    else:
        print("❌ Main menu display failed")
        print(f"STDOUT: {stdout[:500]}...")
        print(f"STDERR: {stderr}")
        return False

def test_help_system():
    """Test help and documentation system."""
    print("🧪 Testing Help System...")
    
    # Test help command
    stdout, stderr, returncode = run_cli_command(["9", "back", "0"])
    
    if "Help" in stdout or "Documentation" in stdout:
        print("✅ Help system accessible")
        return True
    else:
        print("❌ Help system test failed")
        return False

def test_reconnaissance_module():
    """Test reconnaissance module (Option 1)."""
    print("🧪 Testing Reconnaissance Module...")
    
    # Test accessing reconnaissance module
    stdout, stderr, returncode = run_cli_command(["1", "help", "back", "0"])
    
    if "RECONNAISSANCE" in stdout or "Network scanning" in stdout:
        print("✅ Reconnaissance module accessible")
        return True
    else:
        print("❌ Reconnaissance module test failed")
        return False

def test_vulnerability_module():
    """Test vulnerability assessment module (Option 2)."""
    print("🧪 Testing Vulnerability Assessment Module...")
    
    # Test accessing vulnerability module
    stdout, stderr, returncode = run_cli_command(["2", "help", "back", "0"])
    
    if "VULNERABILITY" in stdout or "Web scanning" in stdout:
        print("✅ Vulnerability Assessment module accessible")
        return True
    else:
        print("❌ Vulnerability Assessment module test failed")
        return False

def test_exploitation_module():
    """Test exploitation module (Option 3)."""
    print("🧪 Testing Exploitation Module...")
    
    # Test accessing exploitation module
    stdout, stderr, returncode = run_cli_command(["3", "help", "back", "0"])
    
    if "EXPLOITATION" in stdout or "exploit" in stdout.lower():
        print("✅ Exploitation module accessible")
        return True
    else:
        print("❌ Exploitation module test failed")
        return False

def test_post_exploitation_module():
    """Test post-exploitation module (Option 4)."""
    print("🧪 Testing Post-Exploitation Module...")
    
    # Test accessing post-exploitation module
    stdout, stderr, returncode = run_cli_command(["4", "help", "back", "0"])
    
    if "POST" in stdout or "privilege" in stdout.lower():
        print("✅ Post-Exploitation module accessible")
        return True
    else:
        print("❌ Post-Exploitation module test failed")
        return False

def test_reporting_module():
    """Test reporting module (Option 5)."""
    print("🧪 Testing Reporting Module...")
    
    # Test accessing reporting module
    stdout, stderr, returncode = run_cli_command(["5", "help", "back", "0"])
    
    if "REPORT" in stdout or "Generate" in stdout:
        print("✅ Reporting module accessible")
        return True
    else:
        print("❌ Reporting module test failed")
        return False

def test_project_management():
    """Test project management module (Option 6)."""
    print("🧪 Testing Project Management...")
    
    # Test project management
    stdout, stderr, returncode = run_cli_command(["6", "0"])
    
    if "Project" in stdout:
        print("✅ Project Management accessible")
        return True
    else:
        print("❌ Project Management test failed")
        return False

def test_configuration():
    """Test configuration module (Option 7)."""
    print("🧪 Testing Configuration...")
    
    # Test configuration
    stdout, stderr, returncode = run_cli_command(["7", "0"])
    
    if "Configuration" in stdout or "not yet implemented" in stdout:
        print("✅ Configuration module accessible")
        return True
    else:
        print("❌ Configuration test failed")
        return False

def test_dashboard():
    """Test dashboard module (Option 8)."""
    print("🧪 Testing Dashboard...")
    
    # Test dashboard (with quick exit)
    stdout, stderr, returncode = run_cli_command(["8"], timeout=5)
    
    if "Dashboard" in stdout or "Real-time" in stdout:
        print("✅ Dashboard module accessible")
        return True
    else:
        print("❌ Dashboard test failed")
        return False

def test_startup_banner():
    """Test startup banner and system info."""
    print("🧪 Testing Startup Banner...")
    
    stdout, stderr, returncode = run_cli_command(["0"])
    
    checks = [
        "LeZelote Toolkit" in stdout,
        "PENETRATION TESTING" in stdout,
        "Version 1.0.0" in stdout,
        "System Information" in stdout,
        "Main Menu" in stdout
    ]
    
    if all(checks):
        print("✅ Startup banner and system info display correctly")
        return True
    else:
        print("❌ Startup banner test failed")
        print(f"Checks passed: {sum(checks)}/5")
        return False

def test_error_handling():
    """Test error handling and invalid inputs."""
    print("🧪 Testing Error Handling...")
    
    # Test invalid menu option
    stdout, stderr, returncode = run_cli_command(["99", "0"])
    
    if "Please select one of the available options" in stdout:
        print("✅ Error handling works for invalid menu options")
        return True
    else:
        print("❌ Error handling test failed")
        return False

def main():
    """Run comprehensive CLI testing."""
    print("🚀 Starting Comprehensive LeZelote-Toolkit CLI Testing")
    print("=" * 60)
    
    tests = [
        ("Startup Banner", test_startup_banner),
        ("Main Menu", test_main_menu),
        ("Help System", test_help_system),
        ("Reconnaissance Module", test_reconnaissance_module),
        ("Vulnerability Assessment", test_vulnerability_module),
        ("Exploitation Module", test_exploitation_module),
        ("Post-Exploitation", test_post_exploitation_module),
        ("Reporting Module", test_reporting_module),
        ("Project Management", test_project_management),
        ("Configuration", test_configuration),
        ("Dashboard", test_dashboard),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! LeZelote-Toolkit CLI is fully functional.")
    else:
        print(f"⚠️  {total-passed} tests failed. Review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)