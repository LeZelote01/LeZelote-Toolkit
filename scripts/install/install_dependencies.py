#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Dependencies Installation Script
# =============================================================================
# Description: Automated installation of Python and system dependencies
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import platform
import subprocess
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/dependencies_installation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DependencyInstaller:
    """Manages installation of dependencies for LeZelote-Toolkit"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.requirements_file = self.project_root / "requirements.txt"
        self.venv_path = self.project_root / ".venv"
        self.system_info = self.get_system_info()
        
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            'system': platform.system().lower(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'platform': platform.platform()
        }
    
    def print_banner(self):
        """Print installation banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LeZelote-Toolkit Dependencies Installer                   ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def log_system_info(self):
        """Log system information"""
        logger.info("System Information:")
        for key, value in self.system_info.items():
            logger.info(f"  {key}: {value}")
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements"""
        logger.info("Checking Python version...")
        
        major, minor = sys.version_info[:2]
        required_major, required_minor = 3, 8
        
        if major < required_major or (major == required_major and minor < required_minor):
            logger.error(f"Python {required_major}.{required_minor}+ required (found: {major}.{minor})")
            return False
        
        logger.info(f"Python version check passed: {major}.{minor}")
        return True
    
    def check_pip_availability(self) -> bool:
        """Check if pip is available"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Pip available: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Pip not available: {e}")
            return False
    
    def install_pip(self) -> bool:
        """Install pip if not available"""
        logger.info("Installing pip...")
        
        try:
            # Download get-pip.py
            import urllib.request
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_script = self.project_root / "get-pip.py"
            
            urllib.request.urlretrieve(get_pip_url, get_pip_script)
            
            # Install pip
            result = subprocess.run([sys.executable, str(get_pip_script)], 
                                  check=True, capture_output=True, text=True)
            
            # Clean up
            get_pip_script.unlink()
            
            logger.info("Pip installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install pip: {e}")
            return False
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment"""
        logger.info("Creating Python virtual environment...")
        
        if self.venv_path.exists():
            logger.info("Virtual environment already exists")
            return True
        
        try:
            result = subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], 
                                  check=True, capture_output=True, text=True)
            logger.info("Virtual environment created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e.stderr}")
            return False
    
    def get_venv_python(self) -> str:
        """Get path to Python executable in virtual environment"""
        if self.system_info['system'] == 'windows':
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def get_venv_pip(self) -> str:
        """Get path to pip executable in virtual environment"""
        if self.system_info['system'] == 'windows':
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def activate_virtual_environment(self) -> Dict[str, str]:
        """Get environment variables for activated virtual environment"""
        env = os.environ.copy()
        
        if self.system_info['system'] == 'windows':
            scripts_dir = self.venv_path / "Scripts"
        else:
            scripts_dir = self.venv_path / "bin"
        
        # Prepend venv scripts directory to PATH
        env['PATH'] = str(scripts_dir) + os.pathsep + env.get('PATH', '')
        env['VIRTUAL_ENV'] = str(self.venv_path)
        
        # Remove PYTHONHOME if set
        env.pop('PYTHONHOME', None)
        
        return env
    
    def upgrade_pip_tools(self) -> bool:
        """Upgrade pip, setuptools, and wheel in virtual environment"""
        logger.info("Upgrading pip tools...")
        
        pip_executable = self.get_venv_pip()
        env = self.activate_virtual_environment()
        
        tools = ['pip', 'setuptools', 'wheel']
        
        for tool in tools:
            try:
                result = subprocess.run([pip_executable, 'install', '--upgrade', tool], 
                                      check=True, capture_output=True, text=True, env=env)
                logger.info(f"Upgraded {tool}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to upgrade {tool}: {e.stderr}")
                return False
        
        return True
    
    def parse_requirements_file(self) -> List[Dict[str, str]]:
        """Parse requirements.txt file"""
        if not self.requirements_file.exists():
            logger.error(f"Requirements file not found: {self.requirements_file}")
            return []
        
        requirements = []
        
        with open(self.requirements_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse requirement
                if '>=' in line:
                    package, version = line.split('>=', 1)
                    operator = '>='
                elif '==' in line:
                    package, version = line.split('==', 1)
                    operator = '=='
                elif '>' in line:
                    package, version = line.split('>', 1)
                    operator = '>'
                else:
                    package = line
                    version = ''
                    operator = ''
                
                requirements.append({
                    'package': package.strip(),
                    'version': version.strip(),
                    'operator': operator,
                    'line': line_num,
                    'original': line
                })
        
        logger.info(f"Parsed {len(requirements)} requirements from {self.requirements_file}")
        return requirements
    
    def install_python_dependencies(self, requirements: Optional[List[str]] = None) -> bool:
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        pip_executable = self.get_venv_pip()
        env = self.activate_virtual_environment()
        
        if requirements:
            # Install specific requirements
            for req in requirements:
                try:
                    logger.info(f"Installing {req}...")
                    result = subprocess.run([pip_executable, 'install', req], 
                                          check=True, capture_output=True, text=True, env=env)
                    logger.info(f"Successfully installed {req}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to install {req}: {e.stderr}")
                    return False
        else:
            # Install from requirements.txt
            if not self.requirements_file.exists():
                logger.error("Requirements file not found")
                return False
            
            try:
                result = subprocess.run([pip_executable, 'install', '-r', str(self.requirements_file)], 
                                      check=True, capture_output=True, text=True, env=env)
                logger.info("Successfully installed all requirements")
                
                # Log installed packages
                self.log_installed_packages()
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install requirements: {e.stderr}")
                return False
        
        return True
    
    def log_installed_packages(self):
        """Log installed packages in virtual environment"""
        logger.info("Logging installed packages...")
        
        pip_executable = self.get_venv_pip()
        env = self.activate_virtual_environment()
        
        try:
            result = subprocess.run([pip_executable, 'list'], 
                                  check=True, capture_output=True, text=True, env=env)
            
            lines = result.stdout.strip().split('\n')[2:]  # Skip header lines
            packages = []
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append(f"{parts[0]} {parts[1]}")
            
            logger.info(f"Installed {len(packages)} packages:")
            for package in packages[:10]:  # Show first 10
                logger.info(f"  {package}")
            
            if len(packages) > 10:
                logger.info(f"  ... and {len(packages) - 10} more packages")
                
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to list installed packages: {e}")
    
    def install_system_dependencies_ubuntu(self) -> bool:
        """Install system dependencies on Ubuntu/Debian"""
        logger.info("Installing system dependencies for Ubuntu/Debian...")
        
        packages = [
            'python3-dev', 'python3-venv', 'python3-pip',
            'build-essential', 'cmake', 'git', 'curl', 'wget', 'unzip',
            'libssl-dev', 'libffi-dev', 'libbz2-dev', 'libreadline-dev', 'libsqlite3-dev',
            'libpcap-dev', 'libxml2-dev', 'libxslt1-dev', 'zlib1g-dev',
            'nmap', 'masscan', 'nikto', 'dirb', 'gobuster',
            'aircrack-ng', 'john', 'hashcat', 'hydra', 'medusa'
        ]
        
        try:
            # Update package list
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            
            # Install packages
            cmd = ['sudo', 'apt-get', 'install', '-y'] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            logger.info("System dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e.stderr}")
            return False
    
    def install_system_dependencies_centos(self) -> bool:
        """Install system dependencies on CentOS/RHEL"""
        logger.info("Installing system dependencies for CentOS/RHEL...")
        
        packages = [
            'python3-devel', 'gcc', 'gcc-c++', 'make', 'cmake',
            'git', 'curl', 'wget', 'unzip',
            'openssl-devel', 'libffi-devel', 'bzip2-devel',
            'readline-devel', 'sqlite-devel',
            'libpcap-devel', 'libxml2-devel', 'libxslt-devel', 'zlib-devel',
            'nmap'
        ]
        
        try:
            # Install EPEL repository
            subprocess.run(['sudo', 'yum', 'install', '-y', 'epel-release'], check=True)
            
            # Install packages
            cmd = ['sudo', 'yum', 'install', '-y'] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            logger.info("System dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e.stderr}")
            return False
    
    def install_system_dependencies_macos(self) -> bool:
        """Install system dependencies on macOS"""
        logger.info("Installing system dependencies for macOS...")
        
        # Check if Homebrew is installed
        try:
            subprocess.run(['brew', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Installing Homebrew...")
            try:
                install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                subprocess.run(install_cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install Homebrew: {e}")
                return False
        
        packages = [
            'python3', 'cmake', 'git', 'curl', 'wget',
            'openssl', 'libffi', 'nmap', 'masscan',
            'aircrack-ng', 'john-jumbo', 'hashcat'
        ]
        
        try:
            # Update Homebrew
            subprocess.run(['brew', 'update'], check=True)
            
            # Install packages
            for package in packages:
                try:
                    subprocess.run(['brew', 'install', package], check=True, capture_output=True)
                    logger.info(f"Installed {package}")
                except subprocess.CalledProcessError:
                    logger.warning(f"Failed to install {package} (may already be installed)")
            
            logger.info("System dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install system dependencies: {e}")
            return False
    
    def install_system_dependencies(self) -> bool:
        """Install system dependencies based on operating system"""
        system = self.system_info['system']
        
        if system == 'linux':
            # Detect Linux distribution
            try:
                with open('/etc/os-release', 'r') as f:
                    content = f.read()
                
                if 'ubuntu' in content.lower() or 'debian' in content.lower():
                    return self.install_system_dependencies_ubuntu()
                elif 'centos' in content.lower() or 'rhel' in content.lower() or 'fedora' in content.lower():
                    return self.install_system_dependencies_centos()
                else:
                    logger.warning("Unknown Linux distribution, trying Ubuntu/Debian packages...")
                    return self.install_system_dependencies_ubuntu()
                    
            except FileNotFoundError:
                logger.warning("Cannot detect Linux distribution, trying Ubuntu/Debian packages...")
                return self.install_system_dependencies_ubuntu()
                
        elif system == 'darwin':
            return self.install_system_dependencies_macos()
        elif system == 'windows':
            logger.warning("System dependencies for Windows should be installed via setup.ps1 script")
            return True
        else:
            logger.error(f"Unsupported operating system: {system}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that dependencies are properly installed"""
        logger.info("Verifying installation...")
        
        # Check virtual environment
        if not self.venv_path.exists():
            logger.error("Virtual environment not found")
            return False
        
        # Check Python in virtual environment
        python_executable = self.get_venv_python()
        if not Path(python_executable).exists():
            logger.error("Python executable not found in virtual environment")
            return False
        
        # Test import of key packages
        test_packages = ['requests', 'numpy', 'pandas', 'flask', 'sqlalchemy']
        env = self.activate_virtual_environment()
        
        for package in test_packages:
            try:
                result = subprocess.run([python_executable, '-c', f'import {package}'], 
                                      check=True, capture_output=True, text=True, env=env)
                logger.info(f"✓ {package} import test passed")
            except subprocess.CalledProcessError:
                logger.error(f"✗ {package} import test failed")
                return False
        
        logger.info("Installation verification completed successfully")
        return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Dependencies Installer")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--skip-system', action='store_true',
                       help='Skip system dependencies installation')
    parser.add_argument('--requirements', nargs='*',
                       help='Specific requirements to install')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify installation, do not install')
    
    args = parser.parse_args()
    
    # Create installer
    installer = DependencyInstaller(args.project_root)
    installer.print_banner()
    installer.log_system_info()
    
    if args.verify_only:
        if installer.verify_installation():
            logger.info("✅ Installation verification passed")
            sys.exit(0)
        else:
            logger.error("❌ Installation verification failed")
            sys.exit(1)
    
    try:
        # Check Python version
        if not installer.check_python_version():
            sys.exit(1)
        
        # Check/install pip
        if not installer.check_pip_availability():
            if not installer.install_pip():
                sys.exit(1)
        
        # Create virtual environment
        if not installer.create_virtual_environment():
            sys.exit(1)
        
        # Upgrade pip tools
        if not installer.upgrade_pip_tools():
            sys.exit(1)
        
        # Install system dependencies
        if not args.skip_system:
            if not installer.install_system_dependencies():
                logger.warning("System dependencies installation failed, continuing with Python packages...")
        
        # Install Python dependencies
        if not installer.install_python_dependencies(args.requirements):
            sys.exit(1)
        
        # Verify installation
        if not installer.verify_installation():
            logger.warning("Installation verification failed, but continuing...")
        
        logger.info("🎉 Dependencies installation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()