#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Installation Verification Script
# =============================================================================
# Description: Comprehensive verification of installation and configuration
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import yaml
import platform
import subprocess
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/installation_verification.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class InstallationVerifier:
    """Comprehensive installation verification for LeZelote-Toolkit"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.system_info = self.get_system_info()
        self.verification_results = {}
        
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            'system': platform.system().lower(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
    
    def print_banner(self):
        """Print verification banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   LeZelote-Toolkit Installation Verification                 ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def log_system_info(self):
        """Log system information"""
        logger.info("System Information:")
        for key, value in self.system_info.items():
            logger.info(f"  {key}: {value}")
    
    def verify_directory_structure(self) -> bool:
        """Verify project directory structure"""
        logger.info("Verifying directory structure...")
        
        required_directories = [
            "core",
            "core/engine",
            "core/security", 
            "core/api",
            "core/utils",
            "core/db",
            "modules",
            "modules/reconnaissance",
            "modules/vulnerability",
            "modules/exploitation", 
            "modules/post_exploit",
            "modules/reporting",
            "tools",
            "tools/binaries",
            "tools/python_scripts",
            "tools/containers",
            "interfaces",
            "interfaces/cli",
            "interfaces/web",
            "runtime",
            "runtime/docker",
            "scripts",
            "scripts/install",
            "scripts/update",
            "scripts/maintenance",
            "logs",
            "outputs",
            "reports",
            "config",
            "data",
            "tests"
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for directory in required_directories:
            dir_path = self.project_root / directory
            if dir_path.exists() and dir_path.is_dir():
                existing_dirs.append(directory)
            else:
                missing_dirs.append(directory)
        
        logger.info(f"Directory check: {len(existing_dirs)}/{len(required_directories)} directories found")
        
        if missing_dirs:
            logger.warning(f"Missing directories: {', '.join(missing_dirs)}")
        
        self.verification_results['directories'] = {
            'total': len(required_directories),
            'existing': len(existing_dirs),
            'missing': missing_dirs,
            'success': len(missing_dirs) == 0
        }
        
        return len(missing_dirs) == 0
    
    def verify_core_files(self) -> bool:
        """Verify core Python files"""
        logger.info("Verifying core files...")
        
        core_files = [
            "run_cli.py",
            "core/__init__.py",
            "core/engine/orchestrator.py",
            "core/engine/task_scheduler.py",
            "core/engine/parallel_executor.py",
            "core/engine/resource_manager.py",
            "core/security/stealth_engine.py",
            "core/security/consent_manager.py",
            "core/security/evasion_tactics.py",
            "core/security/crypto_handler.py",
            "core/api/nmap_api.py",
            "core/api/metasploit_api.py",
            "core/api/zap_api.py",
            "core/utils/logging_handler.py",
            "core/utils/error_handler.py",
            "core/db/sqlite_manager.py",
            "core/db/models.py"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in core_files:
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        logger.info(f"Core files check: {len(existing_files)}/{len(core_files)} files found")
        
        if missing_files:
            logger.warning(f"Missing core files: {', '.join(missing_files)}")
        
        self.verification_results['core_files'] = {
            'total': len(core_files),
            'existing': len(existing_files),
            'missing': missing_files,
            'success': len(missing_files) == 0
        }
        
        return len(missing_files) == 0
    
    def verify_python_environment(self) -> bool:
        """Verify Python virtual environment"""
        logger.info("Verifying Python virtual environment...")
        
        venv_path = self.project_root / ".venv"
        
        if not venv_path.exists():
            logger.error("Virtual environment directory not found")
            self.verification_results['python_env'] = {
                'venv_exists': False,
                'python_executable': False,
                'pip_executable': False,
                'success': False
            }
            return False
        
        # Check Python executable
        if self.system_info['system'] == 'windows':
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        python_exists = python_exe.exists()
        pip_exists = pip_exe.exists()
        
        logger.info(f"Python executable: {'✓' if python_exists else '✗'}")
        logger.info(f"Pip executable: {'✓' if pip_exists else '✗'}")
        
        # Test Python version in venv
        python_version_ok = False
        if python_exists:
            try:
                result = subprocess.run([str(python_exe), '--version'], 
                                      capture_output=True, text=True, check=True)
                version_info = result.stdout.strip()
                logger.info(f"Virtual environment Python: {version_info}")
                
                # Check if version is 3.8+
                version_parts = version_info.split()[1].split('.')
                major, minor = int(version_parts[0]), int(version_parts[1])
                python_version_ok = major >= 3 and minor >= 8
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to check Python version: {e}")
        
        success = python_exists and pip_exists and python_version_ok
        
        self.verification_results['python_env'] = {
            'venv_exists': venv_path.exists(),
            'python_executable': python_exists,
            'pip_executable': pip_exists,
            'python_version_ok': python_version_ok,
            'success': success
        }
        
        return success
    
    def verify_python_dependencies(self) -> bool:
        """Verify Python dependencies installation"""
        logger.info("Verifying Python dependencies...")
        
        # Get venv Python executable
        if self.system_info['system'] == 'windows':
            python_exe = self.project_root / ".venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / ".venv" / "bin" / "python"
        
        if not python_exe.exists():
            logger.error("Python executable not found in virtual environment")
            self.verification_results['dependencies'] = {'success': False}
            return False
        
        # Test key dependencies
        key_dependencies = [
            'requests', 'urllib3', 'certifi', 'chardet',
            'python-nmap', 'scapy', 'netaddr', 'dnspython',
            'beautifulsoup4', 'selenium', 'lxml', 'html5lib',
            'flask', 'flask-cors', 'cryptography', 'pycryptodome',
            'sqlalchemy', 'pymongo', 'pandas', 'numpy',
            'json5', 'pyyaml', 'xmltodict', 'click',
            'colorama', 'rich', 'prompt-toolkit', 'tabulate',
            'aiohttp', 'aiofiles', 'psutil', 'pillow',
            'openpyxl', 'python-docx', 'reportlab', 'loguru'
        ]
        
        installed_deps = []
        missing_deps = []
        
        for dep in key_dependencies:
            try:
                result = subprocess.run([str(python_exe), '-c', f'import {dep.replace("-", "_")}'], 
                                      capture_output=True, text=True, check=True)
                installed_deps.append(dep)
            except subprocess.CalledProcessError:
                missing_deps.append(dep)
        
        logger.info(f"Dependencies check: {len(installed_deps)}/{len(key_dependencies)} packages available")
        
        if missing_deps:
            logger.warning(f"Missing dependencies: {', '.join(missing_deps[:10])}")
            if len(missing_deps) > 10:
                logger.warning(f"... and {len(missing_deps) - 10} more")
        
        success = len(missing_deps) == 0
        
        self.verification_results['dependencies'] = {
            'total': len(key_dependencies),
            'installed': len(installed_deps),
            'missing': missing_deps,
            'success': success
        }
        
        return success
    
    def verify_configuration_files(self) -> bool:
        """Verify configuration files"""
        logger.info("Verifying configuration files...")
        
        config_files = [
            "config/main_config.yaml",
            "config/av_evasion.yaml", 
            "config/tool_profiles.yaml",
            "config/database_config.yaml",
            "config/network_config.yaml",
            "config/api_keys.yaml",
            "config/user_preferences.yaml",
            "config/scan_profiles.yaml",
            "config/reporting_config.yaml"
        ]
        
        existing_configs = []
        missing_configs = []
        valid_configs = []
        invalid_configs = []
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            
            if config_path.exists():
                existing_configs.append(config_file)
                
                # Test YAML validity
                try:
                    with open(config_path, 'r') as f:
                        yaml.safe_load(f)
                    valid_configs.append(config_file)
                except yaml.YAMLError as e:
                    invalid_configs.append(config_file)
                    logger.warning(f"Invalid YAML in {config_file}: {e}")
            else:
                missing_configs.append(config_file)
        
        logger.info(f"Configuration files: {len(existing_configs)}/{len(config_files)} found, {len(valid_configs)} valid")
        
        if missing_configs:
            logger.warning(f"Missing config files: {', '.join(missing_configs)}")
        
        if invalid_configs:
            logger.warning(f"Invalid config files: {', '.join(invalid_configs)}")
        
        success = len(missing_configs) == 0 and len(invalid_configs) == 0
        
        self.verification_results['config_files'] = {
            'total': len(config_files),
            'existing': len(existing_configs),
            'valid': len(valid_configs),
            'missing': missing_configs,
            'invalid': invalid_configs,
            'success': success
        }
        
        return success
    
    def verify_cli_interface(self) -> bool:
        """Verify CLI interface functionality"""
        logger.info("Verifying CLI interface...")
        
        cli_script = self.project_root / "run_cli.py"
        
        if not cli_script.exists():
            logger.error("CLI script not found")
            self.verification_results['cli_interface'] = {'success': False}
            return False
        
        # Get venv Python executable
        if self.system_info['system'] == 'windows':
            python_exe = self.project_root / ".venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.project_root / ".venv" / "bin" / "python"
        
        if not python_exe.exists():
            logger.error("Python executable not found")
            self.verification_results['cli_interface'] = {'success': False}
            return False
        
        # Test CLI launch (with timeout)
        try:
            # Test help flag first
            result = subprocess.run([str(python_exe), str(cli_script), '--help'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✓ CLI help command works")
                cli_working = True
            else:
                logger.warning(f"CLI help failed: {result.stderr}")
                cli_working = False
                
        except subprocess.TimeoutExpired:
            logger.warning("CLI test timed out")
            cli_working = False
        except Exception as e:
            logger.error(f"CLI test failed: {e}")
            cli_working = False
        
        self.verification_results['cli_interface'] = {
            'script_exists': cli_script.exists(),
            'python_available': python_exe.exists(),
            'cli_working': cli_working,
            'success': cli_working
        }
        
        return cli_working
    
    def verify_system_tools(self) -> bool:
        """Verify system security tools"""
        logger.info("Verifying system security tools...")
        
        tools_to_check = [
            'nmap', 'sqlmap', 'nikto', 'dirb', 'gobuster',
            'john', 'hashcat', 'hydra', 'aircrack-ng',
            'git', 'curl', 'wget'
        ]
        
        available_tools = []
        missing_tools = []
        
        for tool in tools_to_check:
            try:
                result = subprocess.run(['which', tool] if self.system_info['system'] != 'windows' else ['where', tool], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    available_tools.append(tool)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
        
        logger.info(f"System tools: {len(available_tools)}/{len(tools_to_check)} available")
        
        if missing_tools:
            logger.warning(f"Missing tools: {', '.join(missing_tools)}")
        
        self.verification_results['system_tools'] = {
            'total': len(tools_to_check),
            'available': len(available_tools),
            'missing': missing_tools,
            'success': len(available_tools) >= len(tools_to_check) * 0.7  # 70% threshold
        }
        
        return len(available_tools) >= len(tools_to_check) * 0.7
    
    def verify_docker_environment(self) -> bool:
        """Verify Docker environment (optional)"""
        logger.info("Verifying Docker environment...")
        
        docker_available = False
        compose_available = False
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Docker found: {result.stdout.strip()}")
            docker_available = True
            
            # Check if Docker daemon is running
            subprocess.run(['docker', 'info'], 
                          capture_output=True, text=True, check=True)
            logger.info("Docker daemon is running")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Docker not available or not running")
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, check=True)
            logger.info("Docker Compose available")
            compose_available = True
        except subprocess.CalledProcessError:
            try:
                result = subprocess.run(['docker-compose', '--version'], 
                                      capture_output=True, text=True, check=True)
                logger.info("Docker Compose (legacy) available")
                compose_available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("Docker Compose not available")
        
        success = docker_available and compose_available
        
        self.verification_results['docker'] = {
            'docker_available': docker_available,
            'compose_available': compose_available,
            'success': success
        }
        
        return success  # Docker is optional, so always return True
    
    def verify_permissions(self) -> bool:
        """Verify file permissions"""
        logger.info("Verifying file permissions...")
        
        # Check script executability
        executable_scripts = [
            "launch.sh",
            "scripts/install/setup.sh",
            "scripts/install/configure_tools.sh"
        ]
        
        executable_ok = []
        non_executable = []
        
        for script_path in executable_scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                if os.access(full_path, os.X_OK):
                    executable_ok.append(script_path)
                else:
                    non_executable.append(script_path)
        
        # Check write permissions
        write_dirs = [
            "logs", "outputs", "reports", "data"
        ]
        
        writable_dirs = []
        non_writable_dirs = []
        
        for dir_path in write_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                if os.access(full_path, os.W_OK):
                    writable_dirs.append(dir_path)
                else:
                    non_writable_dirs.append(dir_path)
        
        logger.info(f"Executable scripts: {len(executable_ok)} of {len(executable_scripts)}")
        logger.info(f"Writable directories: {len(writable_dirs)} of {len(write_dirs)}")
        
        success = len(non_executable) == 0 and len(non_writable_dirs) == 0
        
        self.verification_results['permissions'] = {
            'executable_scripts': len(executable_ok),
            'non_executable': non_executable,
            'writable_dirs': len(writable_dirs),
            'non_writable_dirs': non_writable_dirs,
            'success': success
        }
        
        return success
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report"""
        logger.info("Generating verification report...")
        
        # Calculate overall score
        total_checks = len(self.verification_results)
        passed_checks = sum(1 for result in self.verification_results.values() if result.get('success', False))
        
        overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = {
            'verification_summary': {
                'timestamp': self.get_current_timestamp(),
                'project_root': str(self.project_root),
                'system_info': self.system_info,
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': total_checks - passed_checks,
                'overall_score': round(overall_score, 2),
                'status': 'PASS' if overall_score >= 80 else 'PARTIAL' if overall_score >= 60 else 'FAIL'
            },
            'detailed_results': self.verification_results
        }
        
        # Save report to file
        report_file = self.project_root / "verification_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Verification report saved: {report_file}")
        
        return report
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def print_verification_summary(self, report: Dict[str, Any]) -> None:
        """Print verification summary"""
        summary = report['verification_summary']
        
        print("\n" + "="*80)
        print("INSTALLATION VERIFICATION SUMMARY")
        print("="*80)
        print(f"Project Root: {summary['project_root']}")
        print(f"System: {summary['system_info']['system']} ({summary['system_info']['machine']})")
        print(f"Python: {summary['system_info']['python_version']}")
        print(f"Timestamp: {summary['timestamp']}")
        print()
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed_checks']}")
        print(f"Failed: {summary['failed_checks']}")
        print(f"Overall Score: {summary['overall_score']}%")
        print(f"Status: {summary['status']}")
        
        # Print status indicator
        if summary['status'] == 'PASS':
            print("\n✅ Installation verification PASSED")
        elif summary['status'] == 'PARTIAL':
            print("\n⚠️  Installation verification PARTIALLY PASSED")
        else:
            print("\n❌ Installation verification FAILED")
        
        print("="*80)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Installation Verifier")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--output', default='verification_report.json',
                       help='Output report file')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create verifier
    verifier = InstallationVerifier(args.project_root)
    verifier.print_banner()
    verifier.log_system_info()
    
    try:
        # Run all verification checks
        checks = [
            ('Directory Structure', verifier.verify_directory_structure),
            ('Core Files', verifier.verify_core_files),
            ('Python Environment', verifier.verify_python_environment),
            ('Python Dependencies', verifier.verify_python_dependencies),
            ('Configuration Files', verifier.verify_configuration_files),
            ('CLI Interface', verifier.verify_cli_interface),
            ('System Tools', verifier.verify_system_tools),
            ('Docker Environment', verifier.verify_docker_environment),
            ('File Permissions', verifier.verify_permissions)
        ]
        
        logger.info("Starting installation verification...")
        
        for check_name, check_function in checks:
            logger.info(f"Running {check_name} check...")
            try:
                result = check_function()
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"{check_name}: {status}")
            except Exception as e:
                logger.error(f"{check_name} check failed: {e}")
                verifier.verification_results[check_name.lower().replace(' ', '_')] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Generate and display report
        report = verifier.generate_verification_report()
        verifier.print_verification_summary(report)
        
        # Exit with appropriate code
        status = report['verification_summary']['status']
        if status == 'PASS':
            sys.exit(0)
        elif status == 'PARTIAL':
            sys.exit(2)  # Partial success
        else:
            sys.exit(1)  # Failure
        
    except KeyboardInterrupt:
        logger.info("Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()