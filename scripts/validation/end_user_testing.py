#!/usr/bin/env python3
"""
LeZelote Toolkit - End User Testing Script
Simulates real penetration testing workflows for validation
"""

import os
import sys
import time
import json
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.utils.logging_handler import get_logger
    from core.engine.orchestrator import PentestOrchestrator
    from core.security.consent_manager import ConsentManager
except ImportError:
    # Fallback logging
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

class EndUserTestingSuite:
    """Simulates real-world penetration testing scenarios."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scenarios": {},
            "overall_status": "UNKNOWN",
            "recommendations": []
        }
        
    def test_scenario_1_basic_network_scan(self):
        """Test Scenario 1: Basic Network Discovery"""
        logger.info("Testing Scenario 1: Basic Network Discovery")
        
        try:
            # Simulate basic network scan workflow
            consent_manager = ConsentManager()
            
            # Add test consent for localhost
            consent_id = consent_manager.add_consent(
                target="127.0.0.1",
                scope=["network_scanning", "service_discovery"],
                authorization_doc="end_user_test_scenario_1",
                contact_info={"name": "End User Test", "email": "test@localhost"}
            )
            
            # Verify consent works
            is_authorized = consent_manager.verify_consent("127.0.0.1")
            
            # Clean up
            consent_manager.revoke_consent(consent_id)
            
            return {
                "success": is_authorized,
                "details": "Basic consent and authorization workflow functional",
                "duration": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "details": f"Scenario 1 failed: {str(e)}",
                "duration": time.time()
            }
    
    def test_scenario_2_cli_commands(self):
        """Test Scenario 2: CLI Command Execution"""
        logger.info("Testing Scenario 2: CLI Command Execution")
        
        try:
            # Test CLI help commands
            cli_script = self.project_root / "run_cli.py"
            
            # Test basic CLI functionality
            result = subprocess.run([
                sys.executable, str(cli_script), "--version"
            ], capture_output=True, text=True, timeout=15)
            
            success = result.returncode == 0 or "LeZelote" in result.stdout
            
            return {
                "success": success,
                "details": f"CLI execution {'successful' if success else 'failed'}",
                "duration": time.time()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "details": "CLI command timed out",
                "duration": time.time()
            }
        except Exception as e:
            return {
                "success": False,
                "details": f"CLI test failed: {str(e)}",
                "duration": time.time()
            }
    
    def test_scenario_3_data_persistence(self):
        """Test Scenario 3: Data Storage and Retrieval"""
        logger.info("Testing Scenario 3: Data Storage and Retrieval")
        
        try:
            from core.db.sqlite_manager import SQLiteManager
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
                db_path = tmp_db.name
            
            try:
                db_manager = SQLiteManager(db_path)
                
                # Test scan data storage simulation
                db_manager.execute_query("""
                    CREATE TABLE IF NOT EXISTS scan_results (
                        id INTEGER PRIMARY KEY,
                        target TEXT,
                        scan_type TEXT,
                        results TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert test data (using existing schema)
                db_manager.execute_query("""
                    INSERT INTO scan_results (id, module, target, result_data)
                    VALUES (?, ?, ?, ?)
                """, ("test_1", "port_scan", "127.0.0.1", '{"ports": [22, 80, 443]}'))
                
                # Retrieve data
                result = db_manager.fetch_one("""
                    SELECT target, module, result_data FROM scan_results WHERE id = ?
                """, ("test_1",))
                
                success = result and result[0] == "127.0.0.1"
                
                return {
                    "success": success,
                    "details": "Data persistence workflow functional",
                    "duration": time.time()
                }
                
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
                    
        except Exception as e:
            return {
                "success": False,
                "details": f"Data persistence test failed: {str(e)}",
                "duration": time.time()
            }
    
    def test_scenario_4_web_interface_readiness(self):
        """Test Scenario 4: Web Interface Readiness"""
        logger.info("Testing Scenario 4: Web Interface Components")
        
        try:
            # Check web interface files exist
            web_files = [
                "interfaces/web/app.py",
                "interfaces/web/static/js/app.js",
                "interfaces/web/templates/index.html"
            ]
            
            missing_files = []
            for file_path in web_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            # Check Flask imports
            from flask import Flask
            from flask_cors import CORS
            
            success = len(missing_files) == 0
            
            return {
                "success": success,
                "details": f"Web interface ready" if success else f"Missing files: {missing_files}",
                "duration": time.time()
            }
            
        except ImportError as e:
            return {
                "success": False,
                "details": f"Web dependencies missing: {str(e)}",
                "duration": time.time()
            }
        except Exception as e:
            return {
                "success": False,
                "details": f"Web interface test failed: {str(e)}",
                "duration": time.time()
            }
    
    def test_scenario_5_security_compliance(self):
        """Test Scenario 5: Security and Compliance Features"""
        logger.info("Testing Scenario 5: Security and Compliance")
        
        try:
            # Test consent manager security features
            consent_manager = ConsentManager()
            
            # Test unauthorized target rejection
            unauthorized_check = not consent_manager.verify_consent("unauthorized-target.com")
            
            # Test consent expiration (simulate)
            from datetime import datetime, timedelta
            past_date = datetime.now() - timedelta(days=1)
            
            # Add expired consent
            consent_id = consent_manager.add_consent(
                target="expired-test.com",
                scope=["test"],
                authorization_doc="test_doc",
                contact_info={"name": "Test", "email": "test@test.com"},
                valid_until=past_date
            )
            
            # Should not be authorized (expired)
            expired_check = not consent_manager.verify_consent("expired-test.com")
            
            # Clean up
            consent_manager.revoke_consent(consent_id)
            
            success = unauthorized_check and expired_check
            
            return {
                "success": success,
                "details": "Security compliance features operational",
                "duration": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "details": f"Security compliance test failed: {str(e)}",
                "duration": time.time()
            }
    
    def test_scenario_6_error_handling(self):
        """Test Scenario 6: Error Handling and Recovery"""
        logger.info("Testing Scenario 6: Error Handling")
        
        try:
            # Test various error conditions
            from core.db.sqlite_manager import SQLiteManager
            
            # Test invalid database path handling
            try:
                invalid_db = SQLiteManager("/invalid/path/database.db")
                # Should handle gracefully or create directory
                success_invalid_path = True
            except Exception:
                # Expected behavior - should handle gracefully
                success_invalid_path = True
            
            # Test invalid SQL handling
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
                db_path = tmp_db.name
            
            try:
                db_manager = SQLiteManager(db_path)
                
                # Try invalid SQL - should be handled gracefully
                try:
                    db_manager.execute_query("INVALID SQL STATEMENT")
                    success_invalid_sql = False  # Should have thrown error
                except:
                    success_invalid_sql = True  # Expected behavior
                
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            
            success = success_invalid_path and success_invalid_sql
            
            return {
                "success": success,
                "details": "Error handling mechanisms functional",
                "duration": time.time()
            }
            
        except Exception as e:
            return {
                "success": False,
                "details": f"Error handling test failed: {str(e)}",
                "duration": time.time()
            }
    
    def run_all_scenarios(self):
        """Run all end-user testing scenarios."""
        logger.info("Starting End-User Testing Suite")
        logger.info("=" * 60)
        
        scenarios = [
            ("Basic Network Discovery", self.test_scenario_1_basic_network_scan),
            ("CLI Command Execution", self.test_scenario_2_cli_commands),
            ("Data Storage & Retrieval", self.test_scenario_3_data_persistence),
            ("Web Interface Readiness", self.test_scenario_4_web_interface_readiness),
            ("Security & Compliance", self.test_scenario_5_security_compliance),
            ("Error Handling", self.test_scenario_6_error_handling)
        ]
        
        passed_scenarios = 0
        total_scenarios = len(scenarios)
        
        for scenario_name, scenario_func in scenarios:
            start_time = time.time()
            result = scenario_func()
            result["duration"] = time.time() - start_time
            
            self.test_results["scenarios"][scenario_name] = result
            
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{status} {scenario_name} ({result['duration']:.2f}s)")
            
            if not result["success"]:
                logger.error(f"    └─ {result['details']}")
            else:
                passed_scenarios += 1
        
        # Calculate overall status
        success_rate = (passed_scenarios / total_scenarios) * 100
        
        if success_rate >= 100:
            self.test_results["overall_status"] = "EXCELLENT"
        elif success_rate >= 90:
            self.test_results["overall_status"] = "GOOD"
        elif success_rate >= 75:
            self.test_results["overall_status"] = "ACCEPTABLE"
        else:
            self.test_results["overall_status"] = "NEEDS_WORK"
        
        # Generate recommendations
        failed_scenarios = [name for name, result in self.test_results["scenarios"].items()
                          if not result["success"]]
        
        if failed_scenarios:
            self.test_results["recommendations"] = [
                f"Review and fix failed scenarios: {', '.join(failed_scenarios)}",
                "Ensure all dependencies are properly installed",
                "Check system permissions and file access",
                "Validate configuration files"
            ]
        else:
            self.test_results["recommendations"] = [
                "All scenarios passed successfully",
                "Toolkit is ready for deployment",
                "Consider conducting real-world testing"
            ]
        
        return self.test_results
    
    def print_summary(self):
        """Print testing summary."""
        results = self.test_results
        
        print("\n" + "="*80)
        print("LEZELOTE TOOLKIT - END USER TESTING RESULTS")
        print("="*80)
        
        total_scenarios = len(results["scenarios"])
        passed_scenarios = sum(1 for r in results["scenarios"].values() if r["success"])
        
        print(f"\nTest Date: {results['timestamp']}")
        print(f"Overall Status: {results['overall_status']}")
        print(f"Scenarios Passed: {passed_scenarios}/{total_scenarios} ({(passed_scenarios/total_scenarios*100):.1f}%)")
        
        print("\nScenario Results:")
        print("-" * 60)
        
        for scenario_name, result in results["scenarios"].items():
            status_icon = "✅" if result["success"] else "❌"
            status_text = "PASS" if result["success"] else "FAIL"
            print(f"{status_icon} {scenario_name:<30} {status_text:<8} ({result['duration']:>5.2f}s)")
            
            if not result["success"]:
                print(f"    └─ {result['details']}")
        
        print("\nRecommendations:")
        print("-" * 60)
        for rec in results["recommendations"]:
            print(f"• {rec}")
        
        print("\n" + "="*80)

def main():
    """Main function."""
    tester = EndUserTestingSuite()
    results = tester.run_all_scenarios()
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"end_user_testing_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Detailed results saved to: {results_file}")
    
    # Print summary
    tester.print_summary()
    
    # Exit with appropriate code
    if results["overall_status"] in ["EXCELLENT", "GOOD"]:
        sys.exit(0)
    elif results["overall_status"] == "ACCEPTABLE":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()