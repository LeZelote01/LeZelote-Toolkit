#!/usr/bin/env python3
"""
LeZelote-Toolkit Backend Testing Suite
=====================================

Comprehensive testing suite for all backend components of the LeZelote-Toolkit.
Tests core engine, modules, database, and integration functionality.

Author: Testing Agent
Version: 1.0.0
"""

import sys
import os
import time
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test imports
try:
    # Core engine imports
    from core.engine.orchestrator import PentestOrchestrator, WorkflowState
    from core.engine.task_scheduler import TaskScheduler, Task, TaskPriority, TaskStatus
    from core.engine.parallel_executor import ParallelExecutor
    from core.engine.resource_manager import ResourceManager
    
    # Database imports
    from core.db.sqlite_manager import SQLiteManager
    
    # Utils imports
    from core.utils.logging_handler import get_logger, setup_logging
    from core.utils.error_handler import PentestError
    
    # Module imports
    from modules.reconnaissance.network_scanner import NetworkScanner
    from modules.vulnerability.web_scanner import WebScanner
    from modules.reporting.report_generator import ReportGenerator
    
    # CLI imports
    from interfaces.cli.main_cli import PentestCLI
    
    print("✅ All imports successful")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class TestCoreEngine:
    """Test suite for core engine components"""
    
    def __init__(self):
        self.logger = get_logger("TestCoreEngine")
        self.test_results = []
    
    def test_orchestrator_initialization(self):
        """Test PentestOrchestrator initialization"""
        try:
            self.logger.info("Testing PentestOrchestrator initialization...")
            
            # Test basic initialization
            orchestrator = PentestOrchestrator(target="192.168.1.100", profile="quick")
            
            # Verify initialization
            assert orchestrator.target == "192.168.1.100"
            assert orchestrator.profile == "quick"
            assert orchestrator.state == WorkflowState.INITIALIZED
            assert orchestrator.workflow_data is not None
            
            self.test_results.append(("Orchestrator Initialization", True, "Successfully initialized with target and profile"))
            return True
            
        except Exception as e:
            self.test_results.append(("Orchestrator Initialization", False, f"Failed: {str(e)}"))
            return False
    
    def test_orchestrator_project_management(self):
        """Test project management functionality"""
        try:
            self.logger.info("Testing project management...")
            
            orchestrator = PentestOrchestrator(target="example.com", profile="full")
            
            # Test project initialization
            project_config = {
                'name': 'Test Security Assessment',
                'target': 'example.com',
                'profile': 'comprehensive',
                'description': 'Comprehensive security testing of example.com',
                'tags': ['web', 'network', 'security']
            }
            
            result = orchestrator.initialize_project(project_config)
            
            # Verify project initialization
            assert result['success'] == True
            assert 'project_id' in result
            assert result['target'] == 'example.com'
            assert result['profile'] == 'comprehensive'
            
            project_id = result['project_id']
            
            # Test project data retrieval
            project_data = orchestrator.get_project_data(project_id)
            assert project_data['project_id'] == project_id
            assert project_data['target'] == 'example.com'
            
            # Test project state saving
            state_data = orchestrator.save_project_state(project_id)
            assert state_data['project_id'] == project_id
            assert 'workflow_data' in state_data
            
            # Test project state restoration
            restore_result = orchestrator.restore_project_state(project_id, state_data)
            assert restore_result['success'] == True
            
            self.test_results.append(("Project Management", True, "All project operations successful"))
            return True
            
        except Exception as e:
            self.test_results.append(("Project Management", False, f"Failed: {str(e)}"))
            return False
    
    def test_orchestrator_phase_execution(self):
        """Test individual phase execution"""
        try:
            self.logger.info("Testing phase execution...")
            
            orchestrator = PentestOrchestrator(target="testsite.local", profile="quick")
            
            # Test reconnaissance phase
            recon_result = orchestrator.execute_phase('reconnaissance')
            assert recon_result['success'] == True
            assert recon_result['phase'] == 'reconnaissance'
            assert 'data' in recon_result
            
            # Test vulnerability assessment phase
            vuln_result = orchestrator.execute_phase('vulnerability')
            assert vuln_result['success'] == True
            assert vuln_result['phase'] == 'vulnerability'
            
            # Test reporting phase
            report_result = orchestrator.execute_phase('reporting')
            assert report_result['success'] == True
            assert report_result['phase'] == 'reporting'
            
            self.test_results.append(("Phase Execution", True, "All phases executed successfully"))
            return True
            
        except Exception as e:
            self.test_results.append(("Phase Execution", False, f"Failed: {str(e)}"))
            return False
    
    def test_task_scheduler(self):
        """Test TaskScheduler functionality"""
        try:
            self.logger.info("Testing TaskScheduler...")
            
            # Create test configuration
            config = {
                'global': {
                    'max_concurrent_tasks': 2
                }
            }
            
            scheduler = TaskScheduler(config)
            
            # Create test tasks
            def test_task(value):
                time.sleep(0.1)
                return value * 2
            
            task1 = Task(
                id="task1",
                name="Test Task 1",
                func=test_task,
                args=(5,),
                priority=TaskPriority.HIGH
            )
            
            task2 = Task(
                id="task2", 
                name="Test Task 2",
                func=test_task,
                args=(10,),
                priority=TaskPriority.NORMAL
            )
            
            # Add tasks to scheduler
            scheduler.add_task(task1)
            scheduler.add_task(task2)
            
            # Start scheduler
            scheduler.start_scheduler()
            
            # Wait for completion
            completed = scheduler.wait_for_completion(timeout=5)
            assert completed == True
            
            # Check results
            result1 = scheduler.get_task_result("task1")
            result2 = scheduler.get_task_result("task2")
            
            assert result1 == 10  # 5 * 2
            assert result2 == 20  # 10 * 2
            
            # Stop scheduler
            scheduler.stop_scheduler()
            
            self.test_results.append(("Task Scheduler", True, "Task scheduling and execution successful"))
            return True
            
        except Exception as e:
            self.test_results.append(("Task Scheduler", False, f"Failed: {str(e)}"))
            return False
    
    def run_all_tests(self):
        """Run all core engine tests"""
        self.logger.info("Starting Core Engine tests...")
        
        tests = [
            self.test_orchestrator_initialization,
            self.test_orchestrator_project_management,
            self.test_orchestrator_phase_execution,
            self.test_task_scheduler
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        self.logger.info(f"Core Engine tests completed: {passed}/{len(tests)} passed")
        return self.test_results


class TestDatabaseManager:
    """Test suite for database management"""
    
    def __init__(self):
        self.logger = get_logger("TestDatabaseManager")
        self.test_results = []
        self.temp_db_path = None
    
    def test_database_initialization(self):
        """Test database initialization"""
        try:
            self.logger.info("Testing database initialization...")
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                self.temp_db_path = tmp.name
            
            db_manager = SQLiteManager(self.temp_db_path)
            
            # Test database initialization
            result = db_manager.initialize_database()
            assert result == True
            
            # Test basic query execution
            projects = db_manager.execute_query("SELECT * FROM projects")
            assert isinstance(projects, list)
            
            self.test_results.append(("Database Initialization", True, "Database created and initialized successfully"))
            return True
            
        except Exception as e:
            self.test_results.append(("Database Initialization", False, f"Failed: {str(e)}"))
            return False
    
    def test_database_operations(self):
        """Test CRUD operations"""
        try:
            self.logger.info("Testing database CRUD operations...")
            
            db_manager = SQLiteManager(self.temp_db_path)
            
            # Test INSERT
            insert_result = db_manager.execute_update(
                "INSERT INTO projects (id, name, target, profile) VALUES (?, ?, ?, ?)",
                ("test_project_001", "Test Project", "192.168.1.100", "comprehensive")
            )
            assert insert_result == 1
            
            # Test SELECT
            projects = db_manager.execute_query("SELECT * FROM projects WHERE id = ?", ("test_project_001",))
            assert len(projects) == 1
            assert projects[0]['name'] == "Test Project"
            
            # Test UPDATE
            update_result = db_manager.execute_update(
                "UPDATE projects SET status = ? WHERE id = ?",
                ("completed", "test_project_001")
            )
            assert update_result == 1
            
            # Test DELETE
            delete_result = db_manager.execute_update(
                "DELETE FROM projects WHERE id = ?",
                ("test_project_001",)
            )
            assert delete_result == 1
            
            self.test_results.append(("Database CRUD Operations", True, "All CRUD operations successful"))
            return True
            
        except Exception as e:
            self.test_results.append(("Database CRUD Operations", False, f"Failed: {str(e)}"))
            return False
    
    def test_database_migration(self):
        """Test database migration"""
        try:
            self.logger.info("Testing database migration...")
            
            db_manager = SQLiteManager(self.temp_db_path)
            
            # Test migration
            migration_result = db_manager.migrate_database()
            assert migration_result['success'] == True
            assert 'current_version' in migration_result
            
            self.test_results.append(("Database Migration", True, "Migration completed successfully"))
            return True
            
        except Exception as e:
            self.test_results.append(("Database Migration", False, f"Failed: {str(e)}"))
            return False
    
    def cleanup(self):
        """Clean up temporary database"""
        if self.temp_db_path and os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)
    
    def run_all_tests(self):
        """Run all database tests"""
        self.logger.info("Starting Database tests...")
        
        tests = [
            self.test_database_initialization,
            self.test_database_operations,
            self.test_database_migration
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        self.cleanup()
        self.logger.info(f"Database tests completed: {passed}/{len(tests)} passed")
        return self.test_results


class TestModules:
    """Test suite for functional modules"""
    
    def __init__(self):
        self.logger = get_logger("TestModules")
        self.test_results = []
    
    def test_network_scanner(self):
        """Test NetworkScanner module"""
        try:
            self.logger.info("Testing NetworkScanner module...")
            
            scanner = NetworkScanner()
            
            # Test quick scan (mock target)
            with patch.object(scanner.nmap_api, 'scan') as mock_scan:
                mock_scan.return_value = {
                    'hosts': [
                        {
                            'status': {'state': 'up'},
                            'addresses': [{'addrtype': 'ipv4', 'addr': '192.168.1.100'}],
                            'hostnames': [{'name': 'test-host.local'}],
                            'ports': [
                                {
                                    'portid': '80',
                                    'protocol': 'tcp',
                                    'state': {'state': 'open'},
                                    'service': {'name': 'http', 'version': '2.4'}
                                }
                            ]
                        }
                    ],
                    'scan_info': {'command': 'nmap -sV 192.168.1.100'}
                }
                
                result = scanner.quick_scan("192.168.1.100")
                
                assert result['status'] == 'completed'
                assert result['target'] == '192.168.1.100'
                assert 'results' in result
                assert 'summary' in result
            
            self.test_results.append(("Network Scanner", True, "Network scanning functionality working"))
            return True
            
        except Exception as e:
            self.test_results.append(("Network Scanner", False, f"Failed: {str(e)}"))
            return False
    
    def test_web_scanner(self):
        """Test WebScanner module"""
        try:
            self.logger.info("Testing WebScanner module...")
            
            scanner = WebScanner()
            
            # Test web scan with mocked ZAP API
            with patch.object(scanner.zap_api, 'is_running') as mock_running, \
                 patch.object(scanner.zap_api, 'spider_scan') as mock_spider, \
                 patch.object(scanner.zap_api, 'get_alerts') as mock_alerts:
                
                mock_running.return_value = True
                mock_spider.return_value = {'urls': ['http://example.com', 'http://example.com/login']}
                mock_alerts.return_value = [
                    {
                        'id': '1',
                        'name': 'SQL Injection',
                        'risk': 'High',
                        'confidence': 'Medium',
                        'url': 'http://example.com/login',
                        'param': 'username',
                        'description': 'SQL injection vulnerability detected',
                        'solution': 'Use parameterized queries'
                    }
                ]
                
                result = scanner.quick_scan("http://example.com")
                
                assert result['status'] == 'completed'
                assert result['target'] == 'http://example.com'
                assert 'results' in result
                assert 'summary' in result
            
            self.test_results.append(("Web Scanner", True, "Web scanning functionality working"))
            return True
            
        except Exception as e:
            self.test_results.append(("Web Scanner", False, f"Failed: {str(e)}"))
            return False
    
    def test_report_generator(self):
        """Test ReportGenerator module"""
        try:
            self.logger.info("Testing ReportGenerator module...")
            
            generator = ReportGenerator()
            
            # Create test scan data
            test_data = {
                'target': 'example.com',
                'phases': {
                    'reconnaissance': {
                        'results': {'hosts_discovered': 5},
                        'status': 'completed'
                    },
                    'vulnerability': {
                        'results': {
                            'vulnerabilities': [
                                {
                                    'name': 'SQL Injection',
                                    'severity': 'high',
                                    'description': 'SQL injection found in login form',
                                    'solution': 'Use parameterized queries',
                                    'url': 'http://example.com/login'
                                }
                            ]
                        },
                        'status': 'completed'
                    }
                }
            }
            
            # Test HTML report generation
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, "test_report.html")
                
                result = generator.generate_report(test_data, "full", "html", output_path)
                
                assert result['status'] == 'success'
                assert result['format'] == 'html'
                assert os.path.exists(result['output_path'])
                assert result['file_size'] > 0
            
            # Test JSON report generation
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, "test_report.json")
                
                result = generator.generate_report(test_data, "technical", "json", output_path)
                
                assert result['status'] == 'success'
                assert result['format'] == 'json'
                assert os.path.exists(result['output_path'])
            
            self.test_results.append(("Report Generator", True, "Report generation functionality working"))
            return True
            
        except Exception as e:
            self.test_results.append(("Report Generator", False, f"Failed: {str(e)}"))
            return False
    
    def run_all_tests(self):
        """Run all module tests"""
        self.logger.info("Starting Module tests...")
        
        tests = [
            self.test_network_scanner,
            self.test_web_scanner,
            self.test_report_generator
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        self.logger.info(f"Module tests completed: {passed}/{len(tests)} passed")
        return self.test_results


class TestLoggingSystem:
    """Test suite for logging system"""
    
    def __init__(self):
        self.test_results = []
    
    def test_logger_creation(self):
        """Test logger creation and configuration"""
        try:
            # Test logger creation
            logger = get_logger("test_logger")
            assert logger is not None
            assert logger.name == "test_logger"
            
            # Test logging functionality
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            
            self.test_results.append(("Logger Creation", True, "Logger created and functional"))
            return True
            
        except Exception as e:
            self.test_results.append(("Logger Creation", False, f"Failed: {str(e)}"))
            return False
    
    def test_logging_setup(self):
        """Test logging setup with custom configuration"""
        try:
            import logging
            
            # Test custom logging setup
            test_logger = logging.getLogger("custom_test_logger")
            setup_logging(test_logger, log_level="DEBUG")
            
            assert test_logger.level == logging.DEBUG
            assert len(test_logger.handlers) > 0
            
            self.test_results.append(("Logging Setup", True, "Custom logging setup successful"))
            return True
            
        except Exception as e:
            self.test_results.append(("Logging Setup", False, f"Failed: {str(e)}"))
            return False
    
    def run_all_tests(self):
        """Run all logging tests"""
        tests = [
            self.test_logger_creation,
            self.test_logging_setup
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        return self.test_results


class TestCLIInterface:
    """Test suite for CLI interface"""
    
    def __init__(self):
        self.logger = get_logger("TestCLIInterface")
        self.test_results = []
    
    def test_cli_initialization(self):
        """Test CLI initialization"""
        try:
            self.logger.info("Testing CLI initialization...")
            
            cli = PentestCLI()
            
            # Verify CLI components
            assert cli.console is not None
            assert cli.dashboard is not None
            assert cli.menu_system is not None
            assert cli.command_parser is not None
            assert cli.utils is not None
            
            self.test_results.append(("CLI Initialization", True, "CLI components initialized successfully"))
            return True
            
        except Exception as e:
            self.test_results.append(("CLI Initialization", False, f"Failed: {str(e)}"))
            return False
    
    def test_command_parsing(self):
        """Test command parsing functionality"""
        try:
            self.logger.info("Testing command parsing...")
            
            cli = PentestCLI()
            
            # Test help command parsing
            with patch('builtins.print'):  # Suppress output
                cli.execute_command("help")
            
            # Test menu command
            with patch('builtins.print'):
                cli.execute_command("menu")
            
            self.test_results.append(("Command Parsing", True, "Command parsing functional"))
            return True
            
        except Exception as e:
            self.test_results.append(("Command Parsing", False, f"Failed: {str(e)}"))
            return False
    
    def run_all_tests(self):
        """Run all CLI tests"""
        self.logger.info("Starting CLI tests...")
        
        tests = [
            self.test_cli_initialization,
            self.test_command_parsing
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        self.logger.info(f"CLI tests completed: {passed}/{len(tests)} passed")
        return self.test_results


class TestIntegration:
    """Integration tests for the complete system"""
    
    def __init__(self):
        self.logger = get_logger("TestIntegration")
        self.test_results = []
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        try:
            self.logger.info("Testing end-to-end workflow...")
            
            # Initialize orchestrator
            orchestrator = PentestOrchestrator(target="integration-test.local", profile="quick")
            
            # Initialize project
            project_config = {
                'name': 'Integration Test Project',
                'target': 'integration-test.local',
                'profile': 'quick',
                'description': 'End-to-end integration test'
            }
            
            project_result = orchestrator.initialize_project(project_config)
            assert project_result['success'] == True
            
            project_id = project_result['project_id']
            
            # Execute reconnaissance phase
            recon_result = orchestrator.execute_phase('reconnaissance', project_id)
            assert recon_result['success'] == True
            
            # Execute vulnerability assessment
            vuln_result = orchestrator.execute_phase('vulnerability', project_id)
            assert vuln_result['success'] == True
            
            # Generate report
            report_result = orchestrator.execute_phase('reporting', project_id)
            assert report_result['success'] == True
            
            # Verify project data
            project_data = orchestrator.get_project_data(project_id)
            assert 'phases' in project_data
            
            self.test_results.append(("End-to-End Workflow", True, "Complete workflow executed successfully"))
            return True
            
        except Exception as e:
            self.test_results.append(("End-to-End Workflow", False, f"Failed: {str(e)}"))
            return False
    
    def test_module_integration(self):
        """Test integration between different modules"""
        try:
            self.logger.info("Testing module integration...")
            
            # Test scanner to report generator integration
            scanner = NetworkScanner()
            generator = ReportGenerator()
            
            # Mock scan results
            with patch.object(scanner.nmap_api, 'scan') as mock_scan:
                mock_scan.return_value = {
                    'hosts': [
                        {
                            'status': {'state': 'up'},
                            'addresses': [{'addrtype': 'ipv4', 'addr': '192.168.1.100'}],
                            'ports': [
                                {
                                    'portid': '22',
                                    'protocol': 'tcp',
                                    'state': {'state': 'open'},
                                    'service': {'name': 'ssh'}
                                }
                            ]
                        }
                    ]
                }
                
                scan_result = scanner.comprehensive_scan("192.168.1.100")
                
                # Generate report from scan results
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = os.path.join(temp_dir, "integration_report.html")
                    
                    report_data = {
                        'reconnaissance': scan_result,
                        'target': '192.168.1.100'
                    }
                    
                    report_result = generator.generate_report(report_data, "technical", "html", output_path)
                    assert report_result['status'] == 'success'
            
            self.test_results.append(("Module Integration", True, "Modules integrate successfully"))
            return True
            
        except Exception as e:
            self.test_results.append(("Module Integration", False, f"Failed: {str(e)}"))
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        self.logger.info("Starting Integration tests...")
        
        tests = [
            self.test_end_to_end_workflow,
            self.test_module_integration
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        self.logger.info(f"Integration tests completed: {passed}/{len(tests)} passed")
        return self.test_results


def main():
    """Main test execution function"""
    print("🚀 Starting LeZelote-Toolkit Backend Testing Suite")
    print("=" * 60)
    
    # Initialize test suites
    test_suites = [
        ("Core Engine", TestCoreEngine()),
        ("Database Manager", TestDatabaseManager()),
        ("Modules", TestModules()),
        ("Logging System", TestLoggingSystem()),
        ("CLI Interface", TestCLIInterface()),
        ("Integration", TestIntegration())
    ]
    
    all_results = []
    total_tests = 0
    total_passed = 0
    
    # Run all test suites
    for suite_name, suite in test_suites:
        print(f"\n📋 Running {suite_name} Tests...")
        print("-" * 40)
        
        results = suite.run_all_tests()
        all_results.extend(results)
        
        suite_passed = sum(1 for _, passed, _ in results if passed)
        suite_total = len(results)
        
        total_tests += suite_total
        total_passed += suite_passed
        
        print(f"✅ {suite_name}: {suite_passed}/{suite_total} tests passed")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TESTING SUMMARY")
    print("=" * 60)
    
    for test_name, passed, message in all_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name:<30} | {message}")
    
    print("-" * 60)
    print(f"🎯 OVERALL RESULT: {total_passed}/{total_tests} tests passed ({(total_passed/total_tests)*100:.1f}%)")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! LeZelote-Toolkit backend is fully functional.")
        return True
    else:
        failed_tests = total_tests - total_passed
        print(f"⚠️  {failed_tests} tests failed. Review the failures above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)