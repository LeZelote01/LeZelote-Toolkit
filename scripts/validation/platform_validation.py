#!/usr/bin/env python3
"""
LeZelote Toolkit - Platform Validation Script
Tests toolkit functionality across different platforms and environments
"""

import os
import sys
import platform
import subprocess
import json
import time
import tempfile
import logging
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.utils.logging_handler import get_logger
    from core.security.consent_manager import ConsentManager
    from core.engine.orchestrator import PentestOrchestrator
except ImportError:
    # Fallback logging
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

class PlatformValidator:
    """Validates LeZelote Toolkit functionality across platforms."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "platform": self._get_platform_info(),
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "overall_status": "UNKNOWN",
            "score": 0,
            "total_tests": 0
        }
        
    def _get_platform_info(self):
        """Get detailed platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
        
    def _run_test(self, test_name, test_function, *args, **kwargs):
        """Run a single test and record results."""
        logger.info(f"Running test: {test_name}")
        start_time = time.time()
        
        try:
            result = test_function(*args, **kwargs)
            duration = time.time() - start_time
            
            self.test_results["tests"][test_name] = {
                "status": "PASS" if result.get("success", False) else "FAIL",
                "duration": round(duration, 2),
                "details": result.get("details", ""),
                "score": result.get("score", 0),
                "max_score": result.get("max_score", 1)
            }
            
            if result.get("success", False):
                logger.info(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            else:
                logger.error(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                logger.error(f"   Details: {result.get('details', 'No details')}")
                
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {test_name} - ERROR ({duration:.2f}s): {str(e)}")
            
            self.test_results["tests"][test_name] = {
                "status": "ERROR",
                "duration": round(duration, 2),
                "details": str(e),
                "score": 0,
                "max_score": 1
            }
        
        self.test_results["total_tests"] += 1
        
    def test_python_compatibility(self):
        """Test Python version and module compatibility."""
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version < (3, 9):
                return {
                    "success": False,
                    "details": f"Python 3.9+ required, found {python_version.major}.{python_version.minor}",
                    "score": 0,
                    "max_score": 10
                }
            
            # Test core imports
            core_modules = [
                "core.engine.orchestrator",
                "core.security.consent_manager", 
                "core.utils.logging_handler",
                "core.db.sqlite_manager",
                "modules.reconnaissance.network_scanner"
            ]
            
            failed_imports = []
            for module in core_modules:
                try:
                    __import__(module)
                except ImportError as e:
                    failed_imports.append(f"{module}: {str(e)}")
            
            if failed_imports:
                return {
                    "success": False,
                    "details": f"Import failures: {'; '.join(failed_imports)}",
                    "score": max(0, 10 - len(failed_imports) * 2),
                    "max_score": 10
                }
            
            return {
                "success": True,
                "details": f"Python {python_version.major}.{python_version.minor}.{python_version.micro} compatible",
                "score": 10,
                "max_score": 10
            }
            
        except Exception as e:
            return {
                "success": False,
                "details": f"Exception during compatibility test: {str(e)}",
                "score": 0,
                "max_score": 10
            }
    
    def test_cli_interface(self):
        """Test CLI interface functionality."""
        try:
            # Test CLI import and basic functionality
            cli_script = self.project_root / "run_cli.py"
            if not cli_script.exists():
                return {
                    "success": False,
                    "details": "CLI script (run_cli.py) not found",
                    "score": 0,
                    "max_score": 15
                }
            
            # Try to run CLI with help flag (non-interactive)
            result = subprocess.run([
                sys.executable, str(cli_script), "--version"
            ], capture_output=True, text=True, timeout=30)
            
            # Check if CLI loaded without major errors
            if "LeZelote Toolkit" in result.stdout or result.returncode == 0:
                return {
                    "success": True,
                    "details": "CLI interface loads successfully",
                    "score": 15,
                    "max_score": 15
                }
            else:
                return {
                    "success": False,
                    "details": f"CLI failed: {result.stderr[:200]}",
                    "score": 5,
                    "max_score": 15
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "details": "CLI test timed out (30s)",
                "score": 0,
                "max_score": 15
            }
        except Exception as e:
            return {
                "success": False,
                "details": f"CLI test exception: {str(e)}",
                "score": 0,
                "max_score": 15
            }
    
    def test_dependencies(self):
        """Test required dependencies installation."""
        required_packages = [
            "requests", "beautifulsoup4", "flask", "sqlalchemy",
            "pyyaml", "psutil", "cryptography", "scapy"
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                installed_packages.append(package)
            except ImportError:
                # Try alternative names
                alt_names = {
                    "beautifulsoup4": "bs4",
                    "pyyaml": "yaml"
                }
                try:
                    __import__(alt_names.get(package, package))
                    installed_packages.append(package)
                except ImportError:
                    missing_packages.append(package)
        
        score = len(installed_packages) * 2
        max_score = len(required_packages) * 2
        
        if missing_packages:
            return {
                "success": len(missing_packages) <= 2,  # Allow up to 2 missing
                "details": f"Missing: {', '.join(missing_packages)}; Installed: {len(installed_packages)}/{len(required_packages)}",
                "score": score,
                "max_score": max_score
            }
        else:
            return {
                "success": True,
                "details": f"All {len(required_packages)} required packages installed",
                "score": max_score,
                "max_score": max_score
            }
    
    def test_file_structure(self):
        """Test project file structure integrity."""
        required_files = [
            "run_cli.py", "requirements.txt", "README.md", "LICENSE"
        ]
        
        required_dirs = [
            "core", "modules", "interfaces", "data", "config", "docs"
        ]
        
        missing_items = []
        
        # Check files
        for file_name in required_files:
            if not (self.project_root / file_name).exists():
                missing_items.append(f"File: {file_name}")
        
        # Check directories
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing_items.append(f"Dir: {dir_name}")
        
        total_items = len(required_files) + len(required_dirs)
        found_items = total_items - len(missing_items)
        score = (found_items / total_items) * 20
        
        return {
            "success": len(missing_items) == 0,
            "details": f"Found {found_items}/{total_items} items" + 
                      (f"; Missing: {', '.join(missing_items)}" if missing_items else ""),
            "score": int(score),
            "max_score": 20
        }
    
    def test_database_functionality(self):
        """Test database initialization and basic operations."""
        try:
            from core.db.sqlite_manager import SQLiteManager
            
            # Create temp database for testing
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
                db_path = tmp_db.name
            
            try:
                # Test database creation
                db_manager = SQLiteManager(db_path)
                
                # Test basic operations
                db_manager.execute_query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
                db_manager.execute_query("INSERT INTO test (name) VALUES (?)", ("test_entry",))
                
                result = db_manager.fetch_one("SELECT name FROM test WHERE id = 1")
                
                success = result and result[0] == "test_entry"
                
                return {
                    "success": success,
                    "details": "Database operations successful" if success else "Database test failed",
                    "score": 15 if success else 0,
                    "max_score": 15
                }
                
            finally:
                # Clean up temp database
                if os.path.exists(db_path):
                    os.unlink(db_path)
                    
        except Exception as e:
            return {
                "success": False,
                "details": f"Database test failed: {str(e)}",
                "score": 0,
                "max_score": 15
            }
    
    def test_consent_manager(self):
        """Test consent management functionality."""
        try:
            from core.security.consent_manager import ConsentManager
            
            consent_manager = ConsentManager()
            
            # Test basic consent operations
            test_target = "192.168.1.100"
            
            # Add consent
            consent_id = consent_manager.add_consent(
                target=test_target,
                scope=["network_scanning"],
                authorization_doc="validation_test_doc",
                contact_info={"name": "Platform Validation", "email": "test@localhost"}
            )
            
            # Verify consent
            is_authorized = consent_manager.verify_consent(test_target)
            
            # Clean up
            if consent_id:
                consent_manager.revoke_consent(consent_id)
            
            return {
                "success": bool(consent_id and is_authorized),
                "details": "Consent management functional" if is_authorized else "Consent test failed",
                "score": 20 if is_authorized else 0,
                "max_score": 20
            }
            
        except Exception as e:
            return {
                "success": False,
                "details": f"Consent manager test failed: {str(e)}",
                "score": 0,
                "max_score": 20
            }
    
    def test_web_interface(self):
        """Test web interface availability."""
        try:
            # Check if Flask app can be imported
            web_app_path = self.project_root / "interfaces" / "web" / "app.py"
            if not web_app_path.exists():
                return {
                    "success": False,
                    "details": "Web interface app.py not found",
                    "score": 0,
                    "max_score": 10
                }
            
            # Try importing Flask components
            from flask import Flask
            from flask_cors import CORS
            
            return {
                "success": True,
                "details": "Web interface components available",
                "score": 10,
                "max_score": 10
            }
            
        except ImportError as e:
            return {
                "success": False,
                "details": f"Web interface dependencies missing: {str(e)}",
                "score": 0,
                "max_score": 10
            }
        except Exception as e:
            return {
                "success": False,
                "details": f"Web interface test failed: {str(e)}",
                "score": 5,
                "max_score": 10
            }
    
    def test_system_resources(self):
        """Test system resource availability."""
        try:
            import psutil
            
            # Check available resources
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Scoring based on resources
            score = 0
            max_score = 10
            details = []
            
            # CPU check
            if cpu_count >= 2:
                score += 3
                details.append(f"CPU: {cpu_count} cores ✓")
            else:
                details.append(f"CPU: {cpu_count} cores (low)")
            
            # Memory check (4GB minimum, 8GB recommended)
            memory_gb = memory.total / (1024**3)
            if memory_gb >= 8:
                score += 4
                details.append(f"RAM: {memory_gb:.1f}GB ✓")
            elif memory_gb >= 4:
                score += 2
                details.append(f"RAM: {memory_gb:.1f}GB (minimum)")
            else:
                details.append(f"RAM: {memory_gb:.1f}GB (low)")
            
            # Disk check (2GB minimum free)
            disk_gb = disk.free / (1024**3)
            if disk_gb >= 2:
                score += 3
                details.append(f"Disk: {disk_gb:.1f}GB free ✓")
            else:
                details.append(f"Disk: {disk_gb:.1f}GB free (low)")
            
            return {
                "success": score >= 6,
                "details": "; ".join(details),
                "score": score,
                "max_score": max_score
            }
            
        except Exception as e:
            return {
                "success": False,
                "details": f"Resource check failed: {str(e)}",
                "score": 0,
                "max_score": 10
            }
    
    def run_full_validation(self):
        """Run complete platform validation suite."""
        logger.info(f"Starting platform validation for {self.test_results['platform']['system']}")
        logger.info(f"Python: {self.test_results['platform']['python_version']}")
        logger.info(f"Architecture: {self.test_results['platform']['architecture']}")
        
        # Define all tests
        tests = [
            ("Python Compatibility", self.test_python_compatibility),
            ("CLI Interface", self.test_cli_interface),
            ("Dependencies", self.test_dependencies),
            ("File Structure", self.test_file_structure),
            ("Database Functionality", self.test_database_functionality),
            ("Consent Manager", self.test_consent_manager),
            ("Web Interface", self.test_web_interface),
            ("System Resources", self.test_system_resources)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self._run_test(test_name, test_func)
        
        # Calculate overall results
        total_score = sum(test["score"] for test in self.test_results["tests"].values())
        max_total_score = sum(test["max_score"] for test in self.test_results["tests"].values())
        
        self.test_results["score"] = total_score
        self.test_results["max_score"] = max_total_score
        
        if max_total_score > 0:
            percentage = (total_score / max_total_score) * 100
            
            if percentage >= 90:
                self.test_results["overall_status"] = "EXCELLENT"
            elif percentage >= 80:
                self.test_results["overall_status"] = "GOOD"
            elif percentage >= 70:
                self.test_results["overall_status"] = "ACCEPTABLE"
            elif percentage >= 50:
                self.test_results["overall_status"] = "MARGINAL"
            else:
                self.test_results["overall_status"] = "POOR"
        
        return self.test_results
    
    def generate_report(self, output_file=None):
        """Generate detailed validation report."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"platform_validation_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Validation report saved to: {output_file}")
        return output_file
    
    def print_summary(self):
        """Print validation summary to console."""
        results = self.test_results
        
        print("\n" + "="*80)
        print("LEZELOTE TOOLKIT - PLATFORM VALIDATION RESULTS")
        print("="*80)
        
        print(f"\nPlatform: {results['platform']['system']} {results['platform']['release']}")
        print(f"Architecture: {results['platform']['architecture']}")
        print(f"Python: {results['platform']['python_version']}")
        print(f"Test Date: {results['timestamp']}")
        
        print(f"\nOverall Status: {results['overall_status']}")
        print(f"Total Score: {results['score']}/{results['max_score']} ({(results['score']/results['max_score']*100):.1f}%)")
        
        print("\nTest Results:")
        print("-" * 60)
        
        for test_name, test_result in results["tests"].items():
            status_icon = "✅" if test_result["status"] == "PASS" else "❌"
            print(f"{status_icon} {test_name:<25} {test_result['status']:<8} {test_result['score']:>2}/{test_result['max_score']:<2} ({test_result['duration']:>5.2f}s)")
            
            if test_result["status"] != "PASS" and test_result["details"]:
                print(f"    └─ {test_result['details']}")
        
        print("\n" + "="*80)
        
        # Recommendations
        if results["overall_status"] in ["POOR", "MARGINAL"]:
            print("\n⚠️  RECOMMENDATIONS:")
            
            failed_tests = [name for name, result in results["tests"].items() 
                          if result["status"] != "PASS"]
            
            if failed_tests:
                print("- Review and fix the following failed tests:")
                for test in failed_tests:
                    print(f"  • {test}")
                    
            if results["score"] / results["max_score"] < 0.7:
                print("- Consider upgrading system resources")
                print("- Ensure all dependencies are properly installed")
                print("- Check platform compatibility requirements")
        
        print("\n")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="LeZelote Toolkit Platform Validation")
    parser.add_argument("--output", "-o", help="Output file for detailed report")
    parser.add_argument("--quiet", "-q", action="store_true", 
                       help="Only show summary, no detailed logging")
    parser.add_argument("--json-only", action="store_true",
                       help="Only output JSON report, no console summary")
    
    args = parser.parse_args()
    
    if args.quiet:
        logger.setLevel(logging.WARNING)
    
    # Run validation
    validator = PlatformValidator()
    results = validator.run_full_validation()
    
    # Generate outputs
    report_file = validator.generate_report(args.output)
    
    if not args.json_only:
        validator.print_summary()
    
    # Exit with appropriate code
    if results["overall_status"] in ["EXCELLENT", "GOOD"]:
        sys.exit(0)
    elif results["overall_status"] == "ACCEPTABLE":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()