#!/usr/bin/env python3
"""
LeZelote-Toolkit - Configuration Reset Utility
============================================

This script provides configuration reset and restoration for the
Pentest-USB Toolkit, including:
- Reset to default configurations
- Backup and restore configurations
- Selective configuration reset
- Configuration validation
- Template-based configuration generation
- Migration between configuration versions

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import shutil
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import argparse

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging

# Simple helper functions
def safe_copy_file(src: str, dst: str) -> bool:
    """Safely copy a file."""
    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

class ConfigurationResetter:
    """Configuration reset and restoration system."""
    
    def __init__(self):
        """Initialize the configuration resetter."""
        self.logger = setup_logging(__name__)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.config_dir = os.path.join(self.project_root, 'config')
        self.backup_dir = os.path.join(self.project_root, 'config', 'backups')
        
        self.reset_stats = {
            'configs_reset': 0,
            'configs_backed_up': 0,
            'configs_restored': 0,
            'configs_validated': 0,
            'errors': []
        }
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Default configuration templates
        self.config_templates = self._load_config_templates()
    
    def reset_all_configs(self, create_backup: bool = True) -> Dict:
        """Reset all configurations to defaults."""
        self.logger.info("Resetting all configurations to defaults...")
        
        if create_backup:
            self._backup_all_configs()
        
        for config_name in self.config_templates.keys():
            try:
                self.reset_config(config_name, create_backup=False)
            except Exception as e:
                error_msg = f"Failed to reset {config_name}: {e}"
                self.logger.error(error_msg)
                self.reset_stats['errors'].append(error_msg)
        
        self._generate_reset_report()
        return self.reset_stats
    
    def reset_config(self, config_name: str, create_backup: bool = True) -> bool:
        """Reset a specific configuration file."""
        self.logger.info(f"Resetting configuration: {config_name}")
        
        if config_name not in self.config_templates:
            self.logger.error(f"No template found for configuration: {config_name}")
            return False
        
        config_path = os.path.join(self.config_dir, config_name)
        
        # Create backup if requested and file exists
        if create_backup and os.path.exists(config_path):
            backup_path = self._backup_config(config_path)
            if backup_path:
                self.reset_stats['configs_backed_up'] += 1
        
        try:
            # Generate configuration from template
            config_content = self.config_templates[config_name]
            
            # Write configuration file
            if config_name.endswith('.yaml') or config_name.endswith('.yml'):
                with open(config_path, 'w') as f:
                    yaml.dump(config_content, f, default_flow_style=False, indent=2)
            elif config_name.endswith('.json'):
                with open(config_path, 'w') as f:
                    json.dump(config_content, f, indent=2)
            else:
                # Handle other formats as text
                with open(config_path, 'w') as f:
                    f.write(str(config_content))
            
            self.logger.info(f"Configuration reset successfully: {config_name}")
            self.reset_stats['configs_reset'] += 1
            return True
        
        except Exception as e:
            error_msg = f"Failed to reset configuration {config_name}: {e}"
            self.logger.error(error_msg)
            self.reset_stats['errors'].append(error_msg)
            return False
    
    def backup_all_configs(self) -> str:
        """Backup all configuration files."""
        return self._backup_all_configs()
    
    def restore_config(self, config_name: str, backup_path: str = None) -> bool:
        """Restore configuration from backup."""
        self.logger.info(f"Restoring configuration: {config_name}")
        
        if backup_path:
            source_path = backup_path
        else:
            # Find latest backup
            source_path = self._find_latest_backup(config_name)
            if not source_path:
                self.logger.error(f"No backup found for {config_name}")
                return False
        
        config_path = os.path.join(self.config_dir, config_name)
        
        try:
            if safe_copy_file(source_path, config_path):
                self.logger.info(f"Configuration restored: {config_name}")
                self.reset_stats['configs_restored'] += 1
                return True
            else:
                self.logger.error(f"Failed to restore configuration {config_name}")
                return False
        
        except Exception as e:
            error_msg = f"Error restoring configuration {config_name}: {e}"
            self.logger.error(error_msg)
            self.reset_stats['errors'].append(error_msg)
            return False
    
    def validate_all_configs(self) -> Dict[str, Dict]:
        """Validate all configuration files."""
        self.logger.info("Validating all configuration files...")
        
        validation_results = {}
        
        for config_name in self.config_templates.keys():
            config_path = os.path.join(self.config_dir, config_name)
            
            if os.path.exists(config_path):
                result = self.validate_config(config_name)
                validation_results[config_name] = result
                
                if result['valid']:
                    self.reset_stats['configs_validated'] += 1
        
        return validation_results
    
    def validate_config(self, config_name: str) -> Dict:
        """Validate a specific configuration file."""
        config_path = os.path.join(self.config_dir, config_name)
        
        result = {
            'valid': False,
            'exists': False,
            'readable': False,
            'parseable': False,
            'schema_valid': False,
            'issues': []
        }
        
        try:
            # Check if file exists
            if not os.path.exists(config_path):
                result['issues'].append("Configuration file does not exist")
                return result
            
            result['exists'] = True
            
            # Check if file is readable
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                result['readable'] = True
            except Exception as e:
                result['issues'].append(f"Cannot read file: {e}")
                return result
            
            # Check if file is parseable
            try:
                if config_name.endswith('.yaml') or config_name.endswith('.yml'):
                    parsed_content = yaml.safe_load(content)
                elif config_name.endswith('.json'):
                    parsed_content = json.loads(content)
                else:
                    parsed_content = content
                
                result['parseable'] = True
            except Exception as e:
                result['issues'].append(f"Cannot parse file: {e}")
                return result
            
            # Validate against template schema
            try:
                template = self.config_templates.get(config_name, {})
                validation_issues = self._validate_against_template(parsed_content, template, config_name)
                
                if validation_issues:
                    result['issues'].extend(validation_issues)
                else:
                    result['schema_valid'] = True
            except Exception as e:
                result['issues'].append(f"Schema validation error: {e}")
            
            # Overall validation
            result['valid'] = result['exists'] and result['readable'] and result['parseable'] and result['schema_valid']
        
        except Exception as e:
            result['issues'].append(f"Validation error: {e}")
        
        return result
    
    def migrate_config(self, config_name: str, from_version: str, to_version: str) -> bool:
        """Migrate configuration between versions."""
        self.logger.info(f"Migrating configuration {config_name} from {from_version} to {to_version}")
        
        # Create backup before migration
        config_path = os.path.join(self.config_dir, config_name)
        if os.path.exists(config_path):
            self._backup_config(config_path)
        
        try:
            # Load current configuration
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    if config_name.endswith('.yaml') or config_name.endswith('.yml'):
                        current_config = yaml.safe_load(f)
                    elif config_name.endswith('.json'):
                        current_config = json.load(f)
                    else:
                        current_config = f.read()
            else:
                current_config = {}
            
            # Apply migration transformations
            migrated_config = self._apply_migration(current_config, config_name, from_version, to_version)
            
            # Save migrated configuration
            with open(config_path, 'w') as f:
                if config_name.endswith('.yaml') or config_name.endswith('.yml'):
                    yaml.dump(migrated_config, f, default_flow_style=False, indent=2)
                elif config_name.endswith('.json'):
                    json.dump(migrated_config, f, indent=2)
                else:
                    f.write(str(migrated_config))
            
            self.logger.info(f"Configuration migration completed: {config_name}")
            return True
        
        except Exception as e:
            error_msg = f"Configuration migration failed for {config_name}: {e}"
            self.logger.error(error_msg)
            self.reset_stats['errors'].append(error_msg)
            return False
    
    def list_configs(self) -> Dict[str, Dict]:
        """List all configuration files with their status."""
        configs = {}
        
        # Check template configurations
        for config_name in self.config_templates.keys():
            config_path = os.path.join(self.config_dir, config_name)
            
            info = {
                'path': config_path,
                'exists': os.path.exists(config_path),
                'has_template': True,
                'size_bytes': 0,
                'modified': None,
                'backups_available': 0
            }
            
            if info['exists']:
                stat = os.stat(config_path)
                info['size_bytes'] = stat.st_size
                info['modified'] = time.ctime(stat.st_mtime)
            
            # Count available backups
            info['backups_available'] = len(self._list_backups(config_name))
            
            configs[config_name] = info
        
        # Check for additional config files not in templates
        if os.path.exists(self.config_dir):
            for file in os.listdir(self.config_dir):
                if file not in configs and file != 'backups' and not file.startswith('.'):
                    config_path = os.path.join(self.config_dir, file)
                    if os.path.isfile(config_path):
                        stat = os.stat(config_path)
                        configs[file] = {
                            'path': config_path,
                            'exists': True,
                            'has_template': False,
                            'size_bytes': stat.st_size,
                            'modified': time.ctime(stat.st_mtime),
                            'backups_available': len(self._list_backups(file))
                        }
        
        return configs
    
    def _load_config_templates(self) -> Dict[str, Any]:
        """Load default configuration templates."""
        return {
            'main_config.yaml': {
                'toolkit': {
                    'name': 'LeZelote Toolkit',
                    'version': '1.0.0',
                    'description': 'Portable Penetration Testing Framework'
                },
                'execution': {
                    'max_parallel_tasks': 5,
                    'timeout_seconds': 3600,
                    'retry_attempts': 3,
                    'cleanup_on_exit': True
                },
                'security': {
                    'require_consent': True,
                    'audit_logging': True,
                    'stealth_mode': False,
                    'evidence_collection': True
                },
                'performance': {
                    'memory_limit_mb': 2048,
                    'cpu_limit_percent': 80,
                    'disk_cache_mb': 512
                }
            },
            
            'logging.yaml': {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
                    },
                    'detailed': {
                        'format': '%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
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
                        'filename': 'logs/toolkit.log',
                        'maxBytes': 10485760,
                        'backupCount': 5
                    }
                },
                'loggers': {
                    '': {
                        'handlers': ['console', 'file'],
                        'level': 'DEBUG',
                        'propagate': False
                    }
                }
            },
            
            'security_settings.yaml': {
                'authentication': {
                    'enabled': True,
                    'method': 'local',
                    'session_timeout': 3600,
                    'max_login_attempts': 3
                },
                'encryption': {
                    'algorithm': 'AES-256-GCM',
                    'key_length': 256,
                    'rotate_keys': True,
                    'key_rotation_days': 30
                },
                'consent_management': {
                    'require_written_consent': True,
                    'consent_expiry_days': 90,
                    'scope_validation': True,
                    'audit_trail': True
                },
                'stealth_operations': {
                    'memory_execution': True,
                    'traffic_obfuscation': True,
                    'av_evasion': True,
                    'sandbox_detection': True
                }
            },
            
            'tool_profiles.yaml': {
                'nmap': {
                    'enabled': True,
                    'path': 'tools/binaries/{platform}/nmap',
                    'default_options': '-sV -O --script=default',
                    'timeout': 3600,
                    'rate_limit': 1000
                },
                'sqlmap': {
                    'enabled': True,
                    'path': 'tools/binaries/{platform}/sqlmap',
                    'default_options': '--batch --smart --level=3',
                    'timeout': 1800,
                    'threads': 5
                },
                'burpsuite': {
                    'enabled': False,
                    'path': 'tools/binaries/{platform}/burpsuite',
                    'api_key': '',
                    'license_type': 'professional'
                },
                'metasploit': {
                    'enabled': True,
                    'path': 'tools/binaries/{platform}/metasploit',
                    'database_host': 'localhost',
                    'database_port': 5432,
                    'auto_migrate': True
                }
            },
            
            'scan_profiles.yaml': {
                'quick_scan': {
                    'description': 'Fast reconnaissance scan',
                    'modules': ['reconnaissance'],
                    'tools': ['nmap', 'dnsrecon'],
                    'timeout': 900,
                    'intensity': 'low'
                },
                'comprehensive_scan': {
                    'description': 'Complete security assessment',
                    'modules': ['reconnaissance', 'vulnerability', 'exploitation'],
                    'tools': ['nmap', 'zap', 'sqlmap', 'nuclei'],
                    'timeout': 7200,
                    'intensity': 'high'
                },
                'web_application': {
                    'description': 'Web application security test',
                    'modules': ['reconnaissance', 'vulnerability'],
                    'tools': ['zap', 'sqlmap', 'nikto', 'wpscan'],
                    'timeout': 3600,
                    'intensity': 'medium'
                }
            },
            
            'network_config.yaml': {
                'proxy': {
                    'enabled': False,
                    'http_proxy': '',
                    'https_proxy': '',
                    'no_proxy': 'localhost,127.0.0.1'
                },
                'dns': {
                    'servers': ['8.8.8.8', '1.1.1.1'],
                    'timeout': 5,
                    'retries': 3
                },
                'timeouts': {
                    'connection': 30,
                    'read': 60,
                    'total': 300
                },
                'rate_limiting': {
                    'enabled': True,
                    'requests_per_second': 10,
                    'burst_size': 50
                }
            },
            
            'reporting_config.yaml': {
                'output_formats': ['pdf', 'html', 'json'],
                'default_format': 'pdf',
                'template_path': 'data/templates/reports',
                'include_screenshots': True,
                'include_raw_data': False,
                'branding': {
                    'logo_path': 'interfaces/web/static/img/logo.png',
                    'company_name': 'LeZelote Security',
                    'report_title': 'Penetration Test Report'
                },
                'compliance': {
                    'pci_dss': False,
                    'hipaa': False,
                    'gdpr': False,
                    'nist': False
                }
            },
            
            'database_config.yaml': {
                'sqlite': {
                    'path': 'core/db/knowledge_base.db',
                    'timeout': 30,
                    'journal_mode': 'WAL',
                    'synchronous': 'NORMAL',
                    'cache_size': -64000
                },
                'backup': {
                    'enabled': True,
                    'interval_hours': 6,
                    'retention_days': 30,
                    'compression': True
                },
                'maintenance': {
                    'auto_vacuum': 'INCREMENTAL',
                    'optimize_frequency': 'daily',
                    'integrity_check': True
                }
            }
        }
    
    def _backup_all_configs(self) -> str:
        """Backup all configuration files."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_archive = os.path.join(self.backup_dir, f"config_backup_{timestamp}")
        
        try:
            os.makedirs(backup_archive, exist_ok=True)
            
            for config_file in os.listdir(self.config_dir):
                if config_file == 'backups':
                    continue
                
                config_path = os.path.join(self.config_dir, config_file)
                if os.path.isfile(config_path):
                    backup_path = os.path.join(backup_archive, config_file)
                    safe_copy_file(config_path, backup_path)
            
            self.logger.info(f"All configurations backed up to: {backup_archive}")
            return backup_archive
        
        except Exception as e:
            self.logger.error(f"Failed to backup configurations: {e}")
            return None
    
    def _backup_config(self, config_path: str) -> str:
        """Backup a single configuration file."""
        config_name = os.path.basename(config_path)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{config_name}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            if safe_copy_file(config_path, backup_path):
                self.logger.info(f"Configuration backed up: {backup_path}")
                return backup_path
            else:
                self.logger.error(f"Failed to backup configuration: {config_path}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error backing up configuration {config_path}: {e}")
            return None
    
    def _find_latest_backup(self, config_name: str) -> Optional[str]:
        """Find the latest backup for a configuration."""
        backups = self._list_backups(config_name)
        if backups:
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return backups[0]
        return None
    
    def _list_backups(self, config_name: str) -> List[str]:
        """List all backups for a configuration."""
        backups = []
        
        if os.path.exists(self.backup_dir):
            for file in os.listdir(self.backup_dir):
                if file.startswith(config_name + '.backup_'):
                    backups.append(os.path.join(self.backup_dir, file))
        
        return backups
    
    def _validate_against_template(self, config: Any, template: Any, config_name: str) -> List[str]:
        """Validate configuration against template schema."""
        issues = []
        
        if not template:
            return issues  # No template to validate against
        
        try:
            if isinstance(template, dict) and isinstance(config, dict):
                # Check for required keys (basic validation)
                for key in template.keys():
                    if key not in config:
                        issues.append(f"Missing required key: {key}")
                    else:
                        # Recursive validation for nested dictionaries
                        if isinstance(template[key], dict) and isinstance(config[key], dict):
                            nested_issues = self._validate_against_template(config[key], template[key], f"{config_name}.{key}")
                            issues.extend(nested_issues)
            
            # Additional type checking could be added here
        
        except Exception as e:
            issues.append(f"Validation error: {e}")
        
        return issues
    
    def _apply_migration(self, config: Any, config_name: str, from_version: str, to_version: str) -> Any:
        """Apply migration transformations to configuration."""
        # This is a placeholder for migration logic
        # In a real implementation, you would define specific migration rules
        # based on version changes
        
        migration_rules = {
            ('1.0.0', '1.1.0'): self._migrate_1_0_to_1_1,
            ('1.1.0', '1.2.0'): self._migrate_1_1_to_1_2
        }
        
        migration_key = (from_version, to_version)
        if migration_key in migration_rules:
            return migration_rules[migration_key](config, config_name)
        else:
            # No specific migration defined, return as-is
            self.logger.warning(f"No migration defined for {from_version} -> {to_version}")
            return config
    
    def _migrate_1_0_to_1_1(self, config: Any, config_name: str) -> Any:
        """Migration from version 1.0.0 to 1.1.0."""
        # Example migration logic
        if isinstance(config, dict):
            # Add new fields, rename existing ones, etc.
            if 'new_field' not in config:
                config['new_field'] = 'default_value'
            
            # Rename fields
            if 'old_field' in config:
                config['new_field_name'] = config.pop('old_field')
        
        return config
    
    def _migrate_1_1_to_1_2(self, config: Any, config_name: str) -> Any:
        """Migration from version 1.1.0 to 1.2.0."""
        # Example migration logic
        return config
    
    def _generate_reset_report(self):
        """Generate reset summary report."""
        self.logger.info("Configuration Reset Summary:")
        self.logger.info(f"  Configurations reset: {self.reset_stats['configs_reset']}")
        self.logger.info(f"  Configurations backed up: {self.reset_stats['configs_backed_up']}")
        self.logger.info(f"  Configurations restored: {self.reset_stats['configs_restored']}")
        self.logger.info(f"  Configurations validated: {self.reset_stats['configs_validated']}")
        
        if self.reset_stats['errors']:
            self.logger.warning(f"  Errors encountered: {len(self.reset_stats['errors'])}")
            for error in self.reset_stats['errors']:
                self.logger.warning(f"    {error}")

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit Configuration Reset Utility')
    parser.add_argument('action', choices=['reset', 'restore', 'validate', 'backup', 'list', 'migrate'],
                       help='Action to perform')
    parser.add_argument('--config', help='Specific configuration file')
    parser.add_argument('--backup-path', help='Backup file for restore')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--from-version', help='Source version for migration')
    parser.add_argument('--to-version', help='Target version for migration')
    parser.add_argument('--save-report', help='Save detailed report to file')
    
    args = parser.parse_args()
    
    try:
        resetter = ConfigurationResetter()
        
        if args.action == 'reset':
            if args.config:
                # Reset specific configuration
                success = resetter.reset_config(args.config, not args.no_backup)
                if success:
                    print(f"Configuration reset: {args.config}")
                else:
                    print(f"Configuration reset failed: {args.config}")
                    sys.exit(1)
            else:
                # Reset all configurations
                results = resetter.reset_all_configs(not args.no_backup)
                print(f"Configuration reset completed")
                print(f"Configurations reset: {results['configs_reset']}")
        
        elif args.action == 'restore':
            if not args.config:
                print("Error: --config required for restore", file=sys.stderr)
                sys.exit(1)
            
            success = resetter.restore_config(args.config, args.backup_path)
            if success:
                print(f"Configuration restored: {args.config}")
            else:
                print(f"Configuration restore failed: {args.config}")
                sys.exit(1)
        
        elif args.action == 'validate':
            if args.config:
                result = resetter.validate_config(args.config)
                print(f"Validation result for {args.config}:")
                print(f"  Valid: {result['valid']}")
                if result['issues']:
                    for issue in result['issues']:
                        print(f"  ISSUE: {issue}")
            else:
                results = resetter.validate_all_configs()
                print("\n=== CONFIGURATION VALIDATION RESULTS ===")
                for config_name, result in results.items():
                    status = "VALID" if result['valid'] else "INVALID"
                    print(f"{config_name}: {status}")
                    if result['issues']:
                        for issue in result['issues']:
                            print(f"  - {issue}")
        
        elif args.action == 'backup':
            backup_path = resetter.backup_all_configs()
            print(f"Configurations backed up to: {backup_path}")
        
        elif args.action == 'list':
            configs = resetter.list_configs()
            print("\n=== CONFIGURATION FILES ===")
            for config_name, info in configs.items():
                status = "EXISTS" if info['exists'] else "MISSING"
                template = "HAS_TEMPLATE" if info['has_template'] else "NO_TEMPLATE"
                print(f"{config_name}: {status}, {template}")
                print(f"  Size: {info['size_bytes']} bytes")
                print(f"  Backups: {info['backups_available']}")
                if info['modified']:
                    print(f"  Modified: {info['modified']}")
        
        elif args.action == 'migrate':
            if not all([args.config, args.from_version, args.to_version]):
                print("Error: --config, --from-version, and --to-version required for migration", file=sys.stderr)
                sys.exit(1)
            
            success = resetter.migrate_config(args.config, args.from_version, args.to_version)
            if success:
                print(f"Configuration migrated: {args.config}")
            else:
                print(f"Configuration migration failed: {args.config}")
                sys.exit(1)
        
        # Save report if requested
        if args.save_report:
            import json
            with open(args.save_report, 'w') as f:
                json.dump(resetter.reset_stats, f, indent=2)
            print(f"Report saved to: {args.save_report}")
    
    except Exception as e:
        print(f"Error during configuration reset operation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()