#!/usr/bin/env python3
"""
LeZelote-Toolkit - System Health Check
====================================

This script provides comprehensive system health monitoring for the
Pentest-USB Toolkit, including:
- System resource monitoring
- Service availability checks
- Database integrity verification
- Tool availability verification
- Configuration validation
- Performance benchmarking

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import json
import psutil
import subprocess
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
import argparse
import platform

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging, get_logger
from core.utils.network_utils import NetworkUtils, check_network_connectivity, validate_ip_address
from core.db.sqlite_manager import SQLiteManager

class SystemHealthChecker:
    """Comprehensive system health and status checker."""
    
    def __init__(self):
        """Initialize the system health checker."""
        self.logger = setup_logging(__name__)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        self.health_report = {
            'timestamp': time.time(),
            'system_info': {},
            'resources': {},
            'services': {},
            'databases': {},
            'tools': {},
            'configuration': {},
            'network': {},
            'security': {},
            'performance': {},
            'recommendations': [],
            'overall_status': 'unknown',
            'score': 0
        }
        
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'response_time_warning': 5.0,
            'response_time_critical': 10.0
        }
    
    def run_full_check(self) -> Dict[str, Any]:
        """Run comprehensive system health check."""
        self.logger.info("Starting comprehensive system health check...")
        
        # System information
        self._check_system_info()
        
        # Resource monitoring
        self._check_system_resources()
        
        # Service availability
        self._check_services()
        
        # Database health
        self._check_databases()
        
        # Tool availability
        self._check_tool_availability()
        
        # Configuration validation
        self._check_configuration()
        
        # Network connectivity
        self._check_network()
        
        # Security status
        self._check_security()
        
        # Performance benchmarks
        self._check_performance()
        
        # Calculate overall score and status
        self._calculate_overall_status()
        
        # Generate recommendations
        self._generate_recommendations()
        
        self.logger.info(f"Health check completed - Status: {self.health_report['overall_status']}")
        return self.health_report
    
    def _check_system_info(self):
        """Collect basic system information."""
        self.logger.info("Checking system information...")
        
        try:
            self.health_report['system_info'] = {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'hostname': platform.node(),
                'python_version': sys.version.split()[0],
                'toolkit_root': self.project_root,
                'current_user': os.getenv('USER') or os.getenv('USERNAME', 'unknown'),
                'uptime_seconds': self._get_system_uptime(),
                'boot_time': psutil.boot_time()
            }
            
            # Check if running as root (security consideration)
            self.health_report['system_info']['is_root'] = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
            
        except Exception as e:
            self.logger.error(f"Error collecting system info: {e}")
            self.health_report['system_info']['error'] = str(e)
    
    def _check_system_resources(self):
        """Monitor system resources (CPU, Memory, Disk)."""
        self.logger.info("Checking system resources...")
        
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory Usage
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk Usage
            disk_usage = psutil.disk_usage(self.project_root)
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            self.health_report['resources'] = {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None,
                    'status': self._get_resource_status(cpu_percent, 'cpu')
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'usage_percent': memory.percent,
                    'used_gb': round(memory.used / (1024**3), 2),
                    'status': self._get_resource_status(memory.percent, 'memory')
                },
                'swap': {
                    'total_gb': round(swap.total / (1024**3), 2),
                    'used_gb': round(swap.used / (1024**3), 2),
                    'usage_percent': swap.percent,
                    'status': self._get_resource_status(swap.percent, 'memory')
                },
                'disk': {
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'usage_percent': (disk_usage.used / disk_usage.total) * 100,
                    'status': self._get_resource_status((disk_usage.used / disk_usage.total) * 100, 'disk')
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_received': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_received': network_io.packets_recv
                },
                'processes': {
                    'count': process_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
            self.health_report['resources']['error'] = str(e)
    
    def _check_services(self):
        """Check availability of critical services."""
        self.logger.info("Checking service availability...")
        
        services = {
            'python_environment': self._check_python_environment,
            'toolkit_core': self._check_toolkit_core,
            'database_service': self._check_database_service,
            'web_interface': self._check_web_interface,
            'cli_interface': self._check_cli_interface
        }
        
        self.health_report['services'] = {}
        
        for service_name, check_func in services.items():
            try:
                start_time = time.time()
                status = check_func()
                response_time = time.time() - start_time
                
                self.health_report['services'][service_name] = {
                    'status': status,
                    'response_time_seconds': round(response_time, 3),
                    'response_status': self._get_response_status(response_time)
                }
                
            except Exception as e:
                self.health_report['services'][service_name] = {
                    'status': 'error',
                    'error': str(e),
                    'response_time_seconds': None,
                    'response_status': 'critical'
                }
    
    def _check_databases(self):
        """Check database integrity and accessibility."""
        self.logger.info("Checking database health...")
        
        self.health_report['databases'] = {}
        
        # Find all database files
        db_files = []
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_files.append(os.path.join(root, file))
        
        for db_path in db_files:
            db_name = os.path.basename(db_path)
            
            try:
                # Check if file exists and is readable
                if not os.path.exists(db_path):
                    self.health_report['databases'][db_name] = {
                        'status': 'missing',
                        'path': db_path
                    }
                    continue
                
                # Check file size
                db_size = os.path.getsize(db_path)
                
                # Try to connect and perform basic operations
                with sqlite3.connect(db_path, timeout=5) as conn:
                    cursor = conn.cursor()
                    
                    # Check database integrity
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    
                    # Get table count
                    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    
                    # Check if database is locked
                    cursor.execute("BEGIN IMMEDIATE")
                    cursor.execute("ROLLBACK")
                    
                    self.health_report['databases'][db_name] = {
                        'status': 'healthy' if integrity_result == 'ok' else 'corrupted',
                        'path': db_path,
                        'size_mb': round(db_size / (1024**2), 2),
                        'table_count': table_count,
                        'integrity_check': integrity_result,
                        'accessible': True
                    }
            
            except sqlite3.OperationalError as e:
                self.health_report['databases'][db_name] = {
                    'status': 'locked' if 'locked' in str(e).lower() else 'error',
                    'path': db_path,
                    'error': str(e),
                    'accessible': False
                }
            
            except Exception as e:
                self.health_report['databases'][db_name] = {
                    'status': 'error',
                    'path': db_path,
                    'error': str(e),
                    'accessible': False
                }
    
    def _check_tool_availability(self):
        """Check availability of critical tools."""
        self.logger.info("Checking tool availability...")
        
        # Critical Python packages
        python_packages = [
            'requests', 'psutil', 'sqlite3', 'json', 'yaml',
            'cryptography', 'flask', 'pandas', 'numpy'
        ]
        
        # System tools (if available)
        system_tools = ['nmap', 'curl', 'wget', 'git', 'docker']
        
        self.health_report['tools'] = {
            'python_packages': {},
            'system_tools': {},
            'toolkit_modules': {}
        }
        
        # Check Python packages
        for package in python_packages:
            try:
                __import__(package)
                self.health_report['tools']['python_packages'][package] = {
                    'status': 'available',
                    'version': self._get_package_version(package)
                }
            except ImportError:
                self.health_report['tools']['python_packages'][package] = {
                    'status': 'missing',
                    'version': None
                }
        
        # Check system tools
        for tool in system_tools:
            try:
                result = subprocess.run(['which', tool], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Try to get version
                    version = self._get_tool_version(tool)
                    self.health_report['tools']['system_tools'][tool] = {
                        'status': 'available',
                        'path': result.stdout.strip(),
                        'version': version
                    }
                else:
                    self.health_report['tools']['system_tools'][tool] = {
                        'status': 'not_found',
                        'path': None,
                        'version': None
                    }
            except Exception as e:
                self.health_report['tools']['system_tools'][tool] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Check toolkit modules
        toolkit_modules = ['core', 'modules', 'interfaces']
        for module in toolkit_modules:
            try:
                module_path = os.path.join(self.project_root, module)
                if os.path.exists(module_path) and os.path.isdir(module_path):
                    # Count Python files in module
                    py_files = list(Path(module_path).rglob('*.py'))
                    self.health_report['tools']['toolkit_modules'][module] = {
                        'status': 'available',
                        'path': module_path,
                        'python_files_count': len(py_files)
                    }
                else:
                    self.health_report['tools']['toolkit_modules'][module] = {
                        'status': 'missing',
                        'path': module_path
                    }
            except Exception as e:
                self.health_report['tools']['toolkit_modules'][module] = {
                    'status': 'error',
                    'error': str(e)
                }
    
    def _check_configuration(self):
        """Validate configuration files."""
        self.logger.info("Checking configuration...")
        
        config_dir = os.path.join(self.project_root, 'config')
        
        self.health_report['configuration'] = {
            'config_directory': {
                'exists': os.path.exists(config_dir),
                'path': config_dir
            },
            'config_files': {},
            'validation_errors': []
        }
        
        if os.path.exists(config_dir):
            # Check for expected config files
            expected_configs = [
                'main_config.yaml',
                'logging.yaml',
                'security_settings.yaml',
                'tool_profiles.yaml'
            ]
            
            for config_file in expected_configs:
                config_path = os.path.join(config_dir, config_file)
                
                if os.path.exists(config_path):
                    try:
                        # Try to parse YAML files
                        if config_file.endswith('.yaml'):
                            import yaml
                            with open(config_path, 'r') as f:
                                yaml.safe_load(f)
                        
                        self.health_report['configuration']['config_files'][config_file] = {
                            'status': 'valid',
                            'path': config_path,
                            'size_kb': round(os.path.getsize(config_path) / 1024, 2)
                        }
                    
                    except Exception as e:
                        self.health_report['configuration']['config_files'][config_file] = {
                            'status': 'invalid',
                            'path': config_path,
                            'error': str(e)
                        }
                        self.health_report['configuration']['validation_errors'].append(f"{config_file}: {e}")
                
                else:
                    self.health_report['configuration']['config_files'][config_file] = {
                        'status': 'missing',
                        'path': config_path
                    }
    
    def _check_network(self):
        """Check network connectivity and DNS resolution."""
        self.logger.info("Checking network connectivity...")
        
        # Test external connectivity
        test_hosts = [
            ('google.com', 80),
            ('github.com', 443),
            ('8.8.8.8', 53)  # Google DNS
        ]
        
        self.health_report['network'] = {
            'connectivity_tests': {},
            'dns_resolution': {},
            'local_network': {}
        }
        
        # Connectivity tests
        for host, port in test_hosts:
            try:
                start_time = time.time()
                is_connected = check_network_connectivity(host, port, timeout=5)
                response_time = time.time() - start_time
                
                self.health_report['network']['connectivity_tests'][f"{host}:{port}"] = {
                    'status': 'connected' if is_connected else 'failed',
                    'response_time_seconds': round(response_time, 3)
                }
            
            except Exception as e:
                self.health_report['network']['connectivity_tests'][f"{host}:{port}"] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # DNS resolution tests
        dns_hosts = ['google.com', 'github.com', 'python.org']
        for host in dns_hosts:
            try:
                import socket
                start_time = time.time()
                ip = socket.gethostbyname(host)
                response_time = time.time() - start_time
                
                self.health_report['network']['dns_resolution'][host] = {
                    'status': 'resolved',
                    'ip_address': ip,
                    'response_time_seconds': round(response_time, 3)
                }
            
            except Exception as e:
                self.health_report['network']['dns_resolution'][host] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Local network info
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            self.health_report['network']['local_network'] = {
                'hostname': hostname,
                'local_ip': local_ip,
                'is_valid_ip': validate_ip_address(local_ip)
            }
        
        except Exception as e:
            self.health_report['network']['local_network'] = {
                'error': str(e)
            }
    
    def _check_security(self):
        """Check security-related settings and status."""
        self.logger.info("Checking security status...")
        
        self.health_report['security'] = {
            'permissions': {},
            'file_integrity': {},
            'process_security': {}
        }
        
        # Check file permissions on critical directories
        critical_dirs = ['config', 'core', 'scripts']
        for dir_name in critical_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                stat_info = os.stat(dir_path)
                permissions = oct(stat_info.st_mode)[-3:]
                
                self.health_report['security']['permissions'][dir_name] = {
                    'path': dir_path,
                    'permissions': permissions,
                    'owner_readable': stat_info.st_mode & 0o400 != 0,
                    'owner_writable': stat_info.st_mode & 0o200 != 0,
                    'world_readable': stat_info.st_mode & 0o004 != 0
                }
        
        # Check for sensitive files with wrong permissions
        sensitive_patterns = ['*.key', '*.pem', '*password*', '*secret*']
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if any(file.lower().endswith(pattern.replace('*', '')) for pattern in sensitive_patterns):
                    file_path = os.path.join(root, file)
                    stat_info = os.stat(file_path)
                    
                    if stat_info.st_mode & 0o077:  # Others have access
                        self.health_report['security']['file_integrity'][file] = {
                            'path': file_path,
                            'issue': 'overly_permissive',
                            'permissions': oct(stat_info.st_mode)[-3:]
                        }
        
        # Basic process security check
        try:
            current_process = psutil.Process()
            self.health_report['security']['process_security'] = {
                'process_id': current_process.pid,
                'parent_pid': current_process.ppid(),
                'username': current_process.username(),
                'memory_percent': round(current_process.memory_percent(), 2),
                'cpu_percent': round(current_process.cpu_percent(), 2)
            }
        except Exception as e:
            self.health_report['security']['process_security'] = {
                'error': str(e)
            }
    
    def _check_performance(self):
        """Run basic performance benchmarks."""
        self.logger.info("Running performance benchmarks...")
        
        self.health_report['performance'] = {}
        
        # CPU benchmark (simple calculation)
        try:
            start_time = time.time()
            # Simple CPU-intensive task
            result = sum(i * i for i in range(100000))
            cpu_bench_time = time.time() - start_time
            
            self.health_report['performance']['cpu_benchmark'] = {
                'calculation_time_seconds': round(cpu_bench_time, 4),
                'operations_per_second': round(100000 / cpu_bench_time, 2),
                'status': 'fast' if cpu_bench_time < 0.1 else 'slow' if cpu_bench_time > 1.0 else 'normal'
            }
        except Exception as e:
            self.health_report['performance']['cpu_benchmark'] = {'error': str(e)}
        
        # Memory access benchmark
        try:
            start_time = time.time()
            # Simple memory access task
            data = [i for i in range(10000)]
            data.sort()
            memory_bench_time = time.time() - start_time
            
            self.health_report['performance']['memory_benchmark'] = {
                'access_time_seconds': round(memory_bench_time, 4),
                'status': 'fast' if memory_bench_time < 0.01 else 'slow' if memory_bench_time > 0.1 else 'normal'
            }
        except Exception as e:
            self.health_report['performance']['memory_benchmark'] = {'error': str(e)}
        
        # Disk I/O benchmark
        try:
            test_file = os.path.join(self.project_root, 'temp_benchmark_file')
            test_data = b'0' * 1024 * 1024  # 1MB of data
            
            # Write test
            start_time = time.time()
            with open(test_file, 'wb') as f:
                f.write(test_data)
            write_time = time.time() - start_time
            
            # Read test
            start_time = time.time()
            with open(test_file, 'rb') as f:
                f.read()
            read_time = time.time() - start_time
            
            # Clean up
            os.remove(test_file)
            
            self.health_report['performance']['disk_benchmark'] = {
                'write_time_seconds': round(write_time, 4),
                'read_time_seconds': round(read_time, 4),
                'write_speed_mbps': round(1 / write_time, 2),
                'read_speed_mbps': round(1 / read_time, 2),
                'status': 'fast' if (write_time + read_time) < 0.1 else 'slow' if (write_time + read_time) > 1.0 else 'normal'
            }
        except Exception as e:
            self.health_report['performance']['disk_benchmark'] = {'error': str(e)}
    
    def _calculate_overall_status(self):
        """Calculate overall system health status and score."""
        score = 100
        status_weights = {
            'critical': -30,
            'warning': -15,
            'error': -25,
            'healthy': 0,
            'good': 0,
            'available': 0
        }
        
        # Analyze each component
        components = [
            self.health_report['resources'],
            self.health_report['services'],
            self.health_report['databases'],
            self.health_report['tools'],
            self.health_report['configuration'],
            self.health_report['network'],
            self.health_report['security']
        ]
        
        for component in components:
            score += self._analyze_component_health(component, status_weights)
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Determine overall status
        if score >= 90:
            overall_status = 'excellent'
        elif score >= 75:
            overall_status = 'good'
        elif score >= 60:
            overall_status = 'fair'
        elif score >= 40:
            overall_status = 'poor'
        else:
            overall_status = 'critical'
        
        self.health_report['score'] = score
        self.health_report['overall_status'] = overall_status
    
    def _analyze_component_health(self, component: Dict, weights: Dict) -> int:
        """Analyze health of a component and return score adjustment."""
        adjustment = 0
        
        def analyze_recursive(obj):
            nonlocal adjustment
            if isinstance(obj, dict):
                if 'status' in obj:
                    status = obj['status']
                    if status in weights:
                        adjustment += weights[status]
                else:
                    for value in obj.values():
                        analyze_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    analyze_recursive(item)
        
        analyze_recursive(component)
        return adjustment
    
    def _generate_recommendations(self):
        """Generate recommendations based on health check results."""
        recommendations = []
        
        # Resource recommendations
        resources = self.health_report['resources']
        if 'cpu' in resources and resources['cpu'].get('status') in ['warning', 'critical']:
            recommendations.append({
                'category': 'performance',
                'priority': 'high',
                'issue': f"High CPU usage: {resources['cpu']['usage_percent']}%",
                'recommendation': "Consider closing unnecessary applications or upgrading hardware"
            })
        
        if 'memory' in resources and resources['memory'].get('status') in ['warning', 'critical']:
            recommendations.append({
                'category': 'performance',
                'priority': 'high',
                'issue': f"High memory usage: {resources['memory']['usage_percent']}%",
                'recommendation': "Free up memory by closing applications or increase system RAM"
            })
        
        if 'disk' in resources and resources['disk'].get('status') in ['warning', 'critical']:
            recommendations.append({
                'category': 'storage',
                'priority': 'high',
                'issue': f"Low disk space: {resources['disk']['usage_percent']:.1f}% used",
                'recommendation': "Clean up old files or expand storage capacity"
            })
        
        # Service recommendations
        services = self.health_report['services']
        for service_name, service_info in services.items():
            if service_info.get('status') == 'error':
                recommendations.append({
                    'category': 'services',
                    'priority': 'critical',
                    'issue': f"Service '{service_name}' is not working",
                    'recommendation': f"Check service configuration and dependencies for {service_name}"
                })
        
        # Database recommendations
        databases = self.health_report['databases']
        for db_name, db_info in databases.items():
            if db_info.get('status') == 'corrupted':
                recommendations.append({
                    'category': 'data',
                    'priority': 'critical',
                    'issue': f"Database '{db_name}' is corrupted",
                    'recommendation': f"Restore database from backup or run repair tools for {db_name}"
                })
            elif db_info.get('status') == 'locked':
                recommendations.append({
                    'category': 'data',
                    'priority': 'medium',
                    'issue': f"Database '{db_name}' is locked",
                    'recommendation': f"Check for running processes using {db_name} and restart if necessary"
                })
        
        # Security recommendations
        security = self.health_report['security']
        if 'file_integrity' in security and security['file_integrity']:
            for file_name, file_info in security['file_integrity'].items():
                if file_info.get('issue') == 'overly_permissive':
                    recommendations.append({
                        'category': 'security',
                        'priority': 'high',
                        'issue': f"Sensitive file '{file_name}' has overly permissive permissions",
                        'recommendation': f"Restrict permissions for {file_name} using chmod 600"
                    })
        
        # Configuration recommendations
        config = self.health_report['configuration']
        if 'config_files' in config:
            for config_name, config_info in config['config_files'].items():
                if config_info.get('status') == 'missing':
                    recommendations.append({
                        'category': 'configuration',
                        'priority': 'medium',
                        'issue': f"Configuration file '{config_name}' is missing",
                        'recommendation': f"Create or restore {config_name} from template"
                    })
        
        self.health_report['recommendations'] = recommendations
    
    # Helper methods
    def _get_resource_status(self, usage_percent: float, resource_type: str) -> str:
        """Get status based on resource usage percentage."""
        critical_threshold = self.thresholds.get(f'{resource_type}_critical', 95.0)
        warning_threshold = self.thresholds.get(f'{resource_type}_warning', 80.0)
        
        if usage_percent >= critical_threshold:
            return 'critical'
        elif usage_percent >= warning_threshold:
            return 'warning'
        else:
            return 'healthy'
    
    def _get_response_status(self, response_time: float) -> str:
        """Get status based on response time."""
        if response_time >= self.thresholds['response_time_critical']:
            return 'critical'
        elif response_time >= self.thresholds['response_time_warning']:
            return 'warning'
        else:
            return 'good'
    
    def _get_system_uptime(self) -> Optional[float]:
        """Get system uptime in seconds."""
        try:
            return time.time() - psutil.boot_time()
        except:
            return None
    
    def _get_package_version(self, package_name: str) -> Optional[str]:
        """Get version of a Python package."""
        try:
            import importlib.metadata
            return importlib.metadata.version(package_name)
        except:
            try:
                module = __import__(package_name)
                return getattr(module, '__version__', 'unknown')
            except:
                return None
    
    def _get_tool_version(self, tool_name: str) -> Optional[str]:
        """Get version of a system tool."""
        version_args = {
            'nmap': ['--version'],
            'curl': ['--version'],
            'wget': ['--version'],
            'git': ['--version'],
            'docker': ['--version']
        }
        
        try:
            args = version_args.get(tool_name, ['--version'])
            result = subprocess.run([tool_name] + args, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract version from output (first line, first version-like string)
                first_line = result.stdout.split('\n')[0]
                import re
                version_match = re.search(r'(\d+\.[\d\.]+)', first_line)
                return version_match.group(1) if version_match else 'unknown'
        except:
            pass
        return None
    
    # Service check methods
    def _check_python_environment(self) -> str:
        """Check Python environment status."""
        try:
            import sys
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                return 'healthy'
            else:
                return 'warning'
        except:
            return 'error'
    
    def _check_toolkit_core(self) -> str:
        """Check toolkit core modules."""
        try:
            core_path = os.path.join(self.project_root, 'core')
            if os.path.exists(core_path):
                # Check if __init__.py exists and is importable
                init_file = os.path.join(core_path, '__init__.py')
                if os.path.exists(init_file):
                    return 'healthy'
                else:
                    return 'warning'
            else:
                return 'error'
        except:
            return 'error'
    
    def _check_database_service(self) -> str:
        """Check database service status."""
        try:
            db_path = os.path.join(self.project_root, 'core', 'db', 'knowledge_base.db')
            if os.path.exists(db_path):
                # Try to connect
                with sqlite3.connect(db_path, timeout=1) as conn:
                    conn.execute('SELECT 1')
                return 'healthy'
            else:
                return 'warning'
        except:
            return 'error'
    
    def _check_web_interface(self) -> str:
        """Check web interface availability."""
        try:
            web_path = os.path.join(self.project_root, 'interfaces', 'web')
            if os.path.exists(web_path):
                app_file = os.path.join(web_path, 'app.py')
                if os.path.exists(app_file):
                    return 'healthy'
                else:
                    return 'warning'
            else:
                return 'error'
        except:
            return 'error'
    
    def _check_cli_interface(self) -> str:
        """Check CLI interface availability."""
        try:
            cli_file = os.path.join(self.project_root, 'run_cli.py')
            if os.path.exists(cli_file):
                return 'healthy'
            else:
                return 'error'
        except:
            return 'error'

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit System Health Checker')
    parser.add_argument('--output', choices=['json', 'summary', 'detailed'], default='summary',
                       help='Output format')
    parser.add_argument('--component', choices=['resources', 'services', 'databases', 'tools', 
                                              'configuration', 'network', 'security', 'performance'],
                       help='Check specific component only')
    parser.add_argument('--save-report', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    try:
        checker = SystemHealthChecker()
        
        if args.component:
            # Run specific component check
            checker._check_system_info()  # Always check system info
            
            component_methods = {
                'resources': checker._check_system_resources,
                'services': checker._check_services,
                'databases': checker._check_databases,
                'tools': checker._check_tool_availability,
                'configuration': checker._check_configuration,
                'network': checker._check_network,
                'security': checker._check_security,
                'performance': checker._check_performance
            }
            
            if args.component in component_methods:
                component_methods[args.component]()
                checker._calculate_overall_status()
                checker._generate_recommendations()
        else:
            # Run full health check
            report = checker.run_full_check()
        
        # Output results
        if args.output == 'json':
            print(json.dumps(checker.health_report, indent=2))
        elif args.output == 'summary':
            _print_summary(checker.health_report)
        else:  # detailed
            _print_detailed_report(checker.health_report)
        
        # Save report if requested
        if args.save_report:
            with open(args.save_report, 'w') as f:
                json.dump(checker.health_report, f, indent=2)
            print(f"\nDetailed report saved to: {args.save_report}")
        
        # Exit with error code if system is not healthy
        if checker.health_report['overall_status'] in ['poor', 'critical']:
            sys.exit(1)
    
    except Exception as e:
        print(f"Error during system health check: {e}", file=sys.stderr)
        sys.exit(1)

def _print_summary(report: Dict):
    """Print summary of health check results."""
    print(f"\n=== SYSTEM HEALTH SUMMARY ===")
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Health Score: {report['score']}/100")
    print(f"Timestamp: {report['timestamp']}")
    
    # Key metrics
    if 'resources' in report and 'cpu' in report['resources']:
        print(f"\nResources:")
        print(f"  CPU Usage: {report['resources']['cpu']['usage_percent']}%")
        print(f"  Memory Usage: {report['resources']['memory']['usage_percent']}%")
        print(f"  Disk Usage: {report['resources']['disk']['usage_percent']:.1f}%")
    
    # Service status
    if 'services' in report:
        healthy_services = sum(1 for s in report['services'].values() if s.get('status') == 'healthy')
        total_services = len(report['services'])
        print(f"  Services: {healthy_services}/{total_services} healthy")
    
    # Recommendations
    if report.get('recommendations'):
        critical_recs = [r for r in report['recommendations'] if r.get('priority') == 'critical']
        high_recs = [r for r in report['recommendations'] if r.get('priority') == 'high']
        
        if critical_recs or high_recs:
            print(f"\nImportant Recommendations:")
            for rec in critical_recs[:3]:  # Show up to 3 critical
                print(f"  CRITICAL: {rec['issue']}")
            for rec in high_recs[:2]:  # Show up to 2 high priority
                print(f"  HIGH: {rec['issue']}")

def _print_detailed_report(report: Dict):
    """Print detailed health check results."""
    print(f"\n=== DETAILED SYSTEM HEALTH REPORT ===")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Health Score: {report['score']}/100")
    
    # System Information
    if 'system_info' in report:
        print(f"\n--- SYSTEM INFORMATION ---")
        for key, value in report['system_info'].items():
            print(f"{key}: {value}")
    
    # Resources
    if 'resources' in report:
        print(f"\n--- SYSTEM RESOURCES ---")
        for component, data in report['resources'].items():
            print(f"{component.upper()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"  {key}: {value}")
    
    # Services
    if 'services' in report:
        print(f"\n--- SERVICES ---")
        for service, data in report['services'].items():
            status = data.get('status', 'unknown')
            print(f"{service}: {status.upper()}")
    
    # All recommendations
    if report.get('recommendations'):
        print(f"\n--- RECOMMENDATIONS ---")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. [{rec['priority'].upper()}] {rec['issue']}")
            print(f"   Solution: {rec['recommendation']}")

if __name__ == '__main__':
    main()