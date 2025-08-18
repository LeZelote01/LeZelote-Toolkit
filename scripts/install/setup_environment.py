#!/usr/bin/env python3
# =============================================================================
# LeZelote-Toolkit - Environment Setup Script
# =============================================================================
# Description: Configure environment variables and system settings
# Author: LeZelote Team
# Version: 1.0.0
# License: MIT
# =============================================================================

import os
import sys
import json
import yaml
import platform
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/environment_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnvironmentSetup:
    """Manages environment setup for LeZelote-Toolkit"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.system_info = self.get_system_info()
        
    def get_system_info(self) -> Dict[str, str]:
        """Get system information"""
        return {
            'system': platform.system().lower(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'home': str(Path.home()),
            'shell': os.getenv('SHELL', 'unknown')
        }
    
    def print_banner(self):
        """Print setup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LeZelote-Toolkit Environment Setup                        ║
║                              Version 1.0.0                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def log_system_info(self):
        """Log system information"""
        logger.info("System Information:")
        for key, value in self.system_info.items():
            logger.info(f"  {key}: {value}")
    
    def create_environment_config(self) -> Dict[str, str]:
        """Create environment configuration"""
        logger.info("Creating environment configuration...")
        
        env_config = {
            # Project paths
            'LEZELOTE_HOME': str(self.project_root),
            'LEZELOTE_CONFIG_DIR': str(self.config_dir),
            'LEZELOTE_TOOLS_DIR': str(self.project_root / "tools"),
            'LEZELOTE_DATA_DIR': str(self.project_root / "data"),
            'LEZELOTE_LOGS_DIR': str(self.project_root / "logs"),
            'LEZELOTE_OUTPUTS_DIR': str(self.project_root / "outputs"),
            'LEZELOTE_REPORTS_DIR': str(self.project_root / "reports"),
            
            # Python environment
            'LEZELOTE_PYTHON_PATH': str(self.project_root / ".venv" / "bin" / "python"),
            'LEZELOTE_VENV_PATH': str(self.project_root / ".venv"),
            
            # Tool configurations
            'LEZELOTE_NMAP_PATH': self.find_tool_path('nmap'),
            'LEZELOTE_SQLMAP_PATH': self.find_tool_path('sqlmap'),
            'LEZELOTE_BURP_PATH': self.find_tool_path('burpsuite'),
            'LEZELOTE_MSF_PATH': self.find_tool_path('msfconsole'),
            'LEZELOTE_NIKTO_PATH': self.find_tool_path('nikto'),
            'LEZELOTE_JOHN_PATH': self.find_tool_path('john'),
            'LEZELOTE_HASHCAT_PATH': self.find_tool_path('hashcat'),
            'LEZELOTE_AIRCRACK_PATH': self.find_tool_path('aircrack-ng'),
            
            # Default settings
            'LEZELOTE_LOG_LEVEL': 'INFO',
            'LEZELOTE_STEALTH_MODE': 'false',
            'LEZELOTE_AUTO_UPDATE': 'true',
            'LEZELOTE_CONFIRM_ACTIONS': 'true',
            
            # Network settings
            'LEZELOTE_PROXY_HOST': '',
            'LEZELOTE_PROXY_PORT': '',
            'LEZELOTE_USER_AGENT': 'LeZelote-Toolkit/1.0',
            
            # Security settings
            'LEZELOTE_ENCRYPTION_KEY': self.generate_encryption_key(),
            'LEZELOTE_SESSION_TIMEOUT': '3600',  # 1 hour
            
            # Performance settings
            'LEZELOTE_MAX_THREADS': str(os.cpu_count() or 4),
            'LEZELOTE_MEMORY_LIMIT': '2048',  # MB
            'LEZELOTE_DISK_CACHE_SIZE': '1024',  # MB
        }
        
        # Adjust paths for Windows
        if self.system_info['system'] == 'windows':
            env_config['LEZELOTE_PYTHON_PATH'] = str(self.project_root / ".venv" / "Scripts" / "python.exe")
        
        logger.info(f"Created environment configuration with {len(env_config)} variables")
        return env_config
    
    def find_tool_path(self, tool_name: str) -> str:
        """Find path to a tool executable"""
        try:
            import shutil
            path = shutil.which(tool_name)
            return path or ""
        except Exception:
            return ""
    
    def generate_encryption_key(self) -> str:
        """Generate a random encryption key"""
        import secrets
        return secrets.token_hex(32)
    
    def create_env_files(self, env_config: Dict[str, str]) -> None:
        """Create environment files"""
        logger.info("Creating environment files...")
        
        # Create .env file for the project
        env_file = self.project_root / ".env"
        with open(env_file, 'w') as f:
            f.write("# LeZelote-Toolkit Environment Configuration\n")
            f.write("# Generated automatically - do not edit manually\n\n")
            
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"Created .env file: {env_file}")
        
        # Create shell-specific environment files
        self.create_bash_env(env_config)
        self.create_powershell_env(env_config)
        self.create_python_env(env_config)
    
    def create_bash_env(self, env_config: Dict[str, str]) -> None:
        """Create Bash environment file"""
        bash_env_file = self.project_root / ".env.sh"
        
        with open(bash_env_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# LeZelote-Toolkit Environment Configuration for Bash\n")
            f.write("# Source this file to set up environment variables\n\n")
            
            for key, value in env_config.items():
                # Escape special characters for shell
                escaped_value = value.replace('"', '\\"').replace('$', '\\$')
                f.write(f'export {key}="{escaped_value}"\n')
        
        # Make executable
        bash_env_file.chmod(0o755)
        logger.info(f"Created Bash environment file: {bash_env_file}")
    
    def create_powershell_env(self, env_config: Dict[str, str]) -> None:
        """Create PowerShell environment file"""
        ps_env_file = self.project_root / ".env.ps1"
        
        with open(ps_env_file, 'w') as f:
            f.write("# LeZelote-Toolkit Environment Configuration for PowerShell\n")
            f.write("# Source this file to set up environment variables\n\n")
            
            for key, value in env_config.items():
                # Escape special characters for PowerShell
                escaped_value = value.replace('"', '`"').replace('$', '`$')
                f.write(f'$env:{key} = "{escaped_value}"\n')
        
        logger.info(f"Created PowerShell environment file: {ps_env_file}")
    
    def create_python_env(self, env_config: Dict[str, str]) -> None:
        """Create Python environment file"""
        py_env_file = self.project_root / "env_config.py"
        
        with open(py_env_file, 'w') as f:
            f.write('"""LeZelote-Toolkit Environment Configuration for Python"""\n\n')
            f.write("import os\n\n")
            f.write("# Environment variables\n")
            f.write("ENV_CONFIG = {\n")
            
            for key, value in env_config.items():
                # Escape for Python string
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                f.write(f'    "{key}": "{escaped_value}",\n')
            
            f.write("}\n\n")
            f.write("def load_environment():\n")
            f.write("    \"\"\"Load environment variables into os.environ\"\"\"\n")
            f.write("    for key, value in ENV_CONFIG.items():\n")
            f.write("        if value:  # Only set non-empty values\n")
            f.write("            os.environ[key] = value\n\n")
            f.write("def get_env(key: str, default: str = '') -> str:\n")
            f.write("    \"\"\"Get environment variable with fallback to ENV_CONFIG\"\"\"\n")
            f.write("    return os.environ.get(key, ENV_CONFIG.get(key, default))\n")
        
        logger.info(f"Created Python environment file: {py_env_file}")
    
    def setup_path_extensions(self) -> None:
        """Setup PATH extensions for tools"""
        logger.info("Setting up PATH extensions...")
        
        path_extensions = []
        
        # Add project tools to PATH
        tools_bin = self.project_root / "tools" / "binaries" / self.system_info['system']
        if tools_bin.exists():
            path_extensions.append(str(tools_bin))
        
        # Add Python scripts to PATH
        scripts_dir = self.project_root / "tools" / "python_scripts"
        if scripts_dir.exists():
            path_extensions.append(str(scripts_dir))
        
        # Add wrapper scripts to PATH
        wrappers_dir = self.project_root / "tools" / "wrappers"
        if wrappers_dir.exists():
            path_extensions.append(str(wrappers_dir))
        
        if path_extensions:
            # Create PATH setup script
            path_script = self.project_root / "setup_path.sh"
            with open(path_script, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("# LeZelote-Toolkit PATH Setup\n\n")
                f.write("# Add LeZelote tools to PATH\n")
                for path_ext in path_extensions:
                    f.write(f'export PATH="$PATH:{path_ext}"\n')
            
            path_script.chmod(0o755)
            logger.info(f"Created PATH setup script: {path_script}")
    
    def create_user_profile(self) -> None:
        """Create user profile configuration"""
        logger.info("Creating user profile...")
        
        user_profile_dir = Path.home() / ".lezelote"
        user_profile_dir.mkdir(exist_ok=True)
        
        user_profile = {
            'user': {
                'name': self.system_info['user'],
                'home': self.system_info['home'],
                'shell': self.system_info['shell']
            },
            'project': {
                'root': str(self.project_root),
                'version': '1.0.0',
                'installed_date': self.get_current_timestamp()
            },
            'preferences': {
                'theme': 'dark',
                'log_level': 'INFO',
                'auto_update': True,
                'stealth_mode': False,
                'confirm_destructive_actions': True
            },
            'history': {
                'last_used': self.get_current_timestamp(),
                'sessions': [],
                'projects': []
            }
        }
        
        profile_file = user_profile_dir / "profile.yaml"
        with open(profile_file, 'w') as f:
            yaml.dump(user_profile, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created user profile: {profile_file}")
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def setup_logging_configuration(self) -> None:
        """Setup logging configuration"""
        logger.info("Setting up logging configuration...")
        
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'detailed': {
                    'format': '%(asctime)s | %(name)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'detailed',
                    'filename': str(self.project_root / "logs" / "lezelote.log"),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'detailed',
                    'filename': str(self.project_root / "logs" / "errors.log"),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 3
                }
            },
            'loggers': {
                'lezelote': {
                    'level': 'DEBUG',
                    'handlers': ['console', 'file', 'error_file'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }
        
        logging_config_file = self.config_dir / "logging_config.yaml"
        with open(logging_config_file, 'w') as f:
            yaml.dump(logging_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created logging configuration: {logging_config_file}")
    
    def setup_database_paths(self) -> None:
        """Setup database paths and initialization"""
        logger.info("Setting up database paths...")
        
        db_dir = self.project_root / "data" / "databases"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create database configuration
        db_config = {
            'databases': {
                'main': {
                    'path': str(db_dir / "lezelote_main.db"),
                    'type': 'sqlite',
                    'description': 'Main application database'
                },
                'projects': {
                    'path': str(db_dir / "projects.db"),
                    'type': 'sqlite',
                    'description': 'Project and scan results database'
                },
                'vulnerabilities': {
                    'path': str(db_dir / "vulnerabilities.db"),
                    'type': 'sqlite',
                    'description': 'Vulnerability database'
                },
                'knowledge_base': {
                    'path': str(db_dir / "knowledge_base.db"),
                    'type': 'sqlite',
                    'description': 'Security knowledge base'
                }
            }
        }
        
        db_config_file = self.config_dir / "database_config.yaml"
        with open(db_config_file, 'w') as f:
            yaml.dump(db_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created database configuration: {db_config_file}")
    
    def verify_environment_setup(self) -> bool:
        """Verify environment setup"""
        logger.info("Verifying environment setup...")
        
        checks = [
            (self.project_root / ".env", "Main environment file"),
            (self.project_root / ".env.sh", "Bash environment file"),
            (self.project_root / ".env.ps1", "PowerShell environment file"),
            (self.project_root / "env_config.py", "Python environment file"),
            (Path.home() / ".lezelote" / "profile.yaml", "User profile"),
            (self.config_dir / "logging_config.yaml", "Logging configuration"),
            (self.config_dir / "database_config.yaml", "Database configuration"),
        ]
        
        passed = 0
        failed = 0
        
        for file_path, description in checks:
            if file_path.exists():
                logger.info(f"✓ {description}: {file_path}")
                passed += 1
            else:
                logger.error(f"✗ {description}: {file_path}")
                failed += 1
        
        logger.info(f"Environment verification: {passed} passed, {failed} failed")
        
        return failed == 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="LeZelote-Toolkit Environment Setup")
    parser.add_argument('--project-root', default=os.getcwd(), 
                       help='Project root directory')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing environment setup')
    
    args = parser.parse_args()
    
    # Create environment setup
    env_setup = EnvironmentSetup(args.project_root)
    env_setup.print_banner()
    env_setup.log_system_info()
    
    if args.verify_only:
        if env_setup.verify_environment_setup():
            logger.info("✅ Environment verification passed")
            sys.exit(0)
        else:
            logger.error("❌ Environment verification failed")
            sys.exit(1)
    
    try:
        # Create environment configuration
        env_config = env_setup.create_environment_config()
        
        # Create environment files
        env_setup.create_env_files(env_config)
        
        # Setup PATH extensions
        env_setup.setup_path_extensions()
        
        # Create user profile
        env_setup.create_user_profile()
        
        # Setup logging configuration
        env_setup.setup_logging_configuration()
        
        # Setup database paths
        env_setup.setup_database_paths()
        
        # Verify setup
        if env_setup.verify_environment_setup():
            logger.info("🎉 Environment setup completed successfully!")
            
            print("\n" + "="*80)
            print("Environment Setup Complete!")
            print("="*80)
            print(f"Project root: {env_setup.project_root}")
            print(f"Environment files created in: {env_setup.project_root}")
            print(f"User profile created in: {Path.home() / '.lezelote'}")
            print("\nTo activate the environment:")
            print(f"  Bash/Zsh: source {env_setup.project_root}/.env.sh")
            print(f"  PowerShell: . {env_setup.project_root}/.env.ps1")
            print(f"  Python: import env_config; env_config.load_environment()")
        else:
            logger.error("Environment setup completed with errors")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Environment setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()