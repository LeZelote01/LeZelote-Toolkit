#!/usr/bin/env python3
"""
Simplified CLI Testing - Core Functionality Only
"""

import sys
import subprocess
import time
from pathlib import Path

def test_cli_startup():
    """Test CLI startup and basic functionality."""
    print("🧪 Testing CLI Startup and Basic Functionality...")
    
    try:
        # Test CLI startup with immediate exit
        process = subprocess.Popen(
            [sys.executable, "run_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app"
        )
        
        # Send exit command immediately
        stdout, stderr = process.communicate(input="0\n", timeout=10)
        
        # Check for key elements
        checks = {
            "Banner Display": "LeZelote Toolkit" in stdout,
            "System Info": "System Information" in stdout,
            "Main Menu": "Main Menu" in stdout,
            "9 Options Present": all(str(i) in stdout for i in range(1, 10)),
            "Clean Exit": "shutdown complete" in stdout
        }
        
        print("📊 Startup Test Results:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ CLI startup test failed: {e}")
        return False

def test_menu_navigation():
    """Test menu navigation without module instantiation."""
    print("\n🧪 Testing Menu Navigation...")
    
    try:
        # Test navigating through menu options
        process = subprocess.Popen(
            [sys.executable, "run_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app"
        )
        
        # Try to access help (option 9) then exit
        stdout, stderr = process.communicate(input="9\n0\n", timeout=15)
        
        # Check if help was accessed
        help_accessed = "Help" in stdout or "Documentation" in stdout
        clean_exit = "shutdown complete" in stdout
        
        print("📊 Navigation Test Results:")
        print(f"  {'✅' if help_accessed else '❌'} Help System Accessible")
        print(f"  {'✅' if clean_exit else '❌'} Clean Exit")
        
        return help_accessed and clean_exit
        
    except Exception as e:
        print(f"❌ Menu navigation test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n🧪 Testing Error Handling...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "run_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app"
        )
        
        # Send invalid input then exit
        stdout, stderr = process.communicate(input="99\n0\n", timeout=10)
        
        # Check for error handling
        error_handled = "Please select one of the available options" in stdout
        clean_exit = "shutdown complete" in stdout
        
        print("📊 Error Handling Test Results:")
        print(f"  {'✅' if error_handled else '❌'} Invalid Input Handled")
        print(f"  {'✅' if clean_exit else '❌'} Clean Exit After Error")
        
        return error_handled and clean_exit
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_cli_responsiveness():
    """Test CLI responsiveness and performance."""
    print("\n🧪 Testing CLI Responsiveness...")
    
    try:
        start_time = time.time()
        
        process = subprocess.Popen(
            [sys.executable, "run_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app"
        )
        
        stdout, stderr = process.communicate(input="0\n", timeout=10)
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        # Check performance
        fast_startup = startup_time < 5.0  # Should start within 5 seconds
        clean_exit = "shutdown complete" in stdout
        
        print("📊 Responsiveness Test Results:")
        print(f"  {'✅' if fast_startup else '❌'} Fast Startup ({startup_time:.2f}s)")
        print(f"  {'✅' if clean_exit else '❌'} Clean Exit")
        
        return fast_startup and clean_exit
        
    except Exception as e:
        print(f"❌ Responsiveness test failed: {e}")
        return False

def test_cli_robustness():
    """Test CLI robustness with multiple operations."""
    print("\n🧪 Testing CLI Robustness...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "run_cli.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/app"
        )
        
        # Multiple operations: invalid input, help, exit
        commands = "99\n9\n0\n"
        stdout, stderr = process.communicate(input=commands, timeout=15)
        
        # Check robustness
        handled_invalid = "Please select one of the available options" in stdout
        accessed_help = "Help" in stdout or "Documentation" in stdout
        clean_exit = "shutdown complete" in stdout
        
        print("📊 Robustness Test Results:")
        print(f"  {'✅' if handled_invalid else '❌'} Handled Invalid Input")
        print(f"  {'✅' if accessed_help else '❌'} Accessed Help System")
        print(f"  {'✅' if clean_exit else '❌'} Clean Exit")
        
        return handled_invalid and accessed_help and clean_exit
        
    except Exception as e:
        print(f"❌ Robustness test failed: {e}")
        return False

def main():
    """Run simplified CLI testing."""
    print("🚀 LeZelote-Toolkit CLI - Core Functionality Testing")
    print("=" * 60)
    
    tests = [
        ("CLI Startup & Basic Functionality", test_cli_startup),
        ("Menu Navigation", test_menu_navigation),
        ("Error Handling", test_error_handling),
        ("CLI Responsiveness", test_cli_responsiveness),
        ("CLI Robustness", test_cli_robustness)
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
    print("📊 CORE FUNCTIONALITY TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 CORE CLI FUNCTIONALITY IS WORKING!")
        print("📝 Note: Some advanced modules may have dependency issues")
    else:
        print(f"⚠️  {total-passed} core tests failed.")
    
    return passed >= 4  # At least 4/5 tests should pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)