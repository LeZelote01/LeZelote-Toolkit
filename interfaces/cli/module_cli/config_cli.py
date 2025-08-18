#!/usr/bin/env python3
"""
Configuration CLI Module for Pentest-USB Toolkit
================================================

Command-line interface for toolkit configuration management,
settings, preferences, and system administration.
"""

import sys
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from interfaces.cli.utils import CLIUtils
from core.utils.config_manager import ConfigManager
from core.utils.logging_handler import LoggingHandler
from data.wordlists.wordlist_manager import WordlistManager


class ConfigCLI:
    """Command-line interface for configuration management."""
    
    def __init__(self):
        """Initialize configuration CLI."""
        self.console = Console()
        self.utils = CLIUtils()
        
        # Initialize configuration components
        self.config_manager = ConfigManager()
        self.logger = LoggingHandler().get_logger("ConfigCLI")
        self.wordlist_manager = WordlistManager()
        
        # Current configuration state
        self.current_config = self.config_manager.load_config()
        
    def run(self, args: List[str] = None):
        """Main entry point for configuration CLI."""
        try:
            self._show_banner()
            
            if args and len(args) > 0:
                # Direct command mode
                self._handle_direct_command(args)
            else:
                # Interactive mode
                self._interactive_mode()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Configuration module interrupted.[/]")
        except Exception as e:
            self.console.print(f"[red]Error in configuration module: {e}[/]")
            
    def _show_banner(self):
        """Show configuration module banner."""
        banner = """
[bold blue]⚙️ CONFIGURATION MODULE[/]
[dim]System Settings • User Preferences • Tool Configuration • Database Management[/]
"""
        self.console.print(Panel(banner, border_style="blue"))
        
    def _handle_direct_command(self, args: List[str]):
        """Handle direct command execution."""
        if not args:
            return
            
        command = args[0].lower()
        
        if command in ['show', 'display', 'list']:
            category = args[1] if len(args) > 1 else None
            self._show_configuration(category)
        elif command in ['set', 'update']:
            if len(args) >= 3:
                key = args[1]
                value = args[2]
                self._set_configuration(key, value)
            else:
                self.console.print("[red]Usage: config set <key> <value>[/]")
        elif command in ['get']:
            if len(args) >= 2:
                key = args[1]
                self._get_configuration(key)
            else:
                self.console.print("[red]Usage: config get <key>[/]")
        elif command in ['reset']:
            category = args[1] if len(args) > 1 else None
            self._reset_configuration(category)
        elif command in ['backup']:
            self._backup_configuration()
        elif command in ['restore']:
            backup_file = args[1] if len(args) > 1 else None
            self._restore_configuration(backup_file)
        elif command in ['wordlists', 'wordlist']:
            self._wordlist_management()
        elif command in ['database', 'db']:
            self._database_configuration()
        elif command in ['logging', 'logs']:
            self._logging_configuration()
        elif command in ['network']:
            self._network_configuration()
        elif command in ['export']:
            format_type = args[1] if len(args) > 1 else "json"
            self._export_configuration(format_type)
        else:
            self.console.print(f"[red]Unknown configuration command: {command}[/]")
            self._show_help()
            
    def _interactive_mode(self):
        """Run interactive configuration mode."""
        while True:
            self._show_menu()
            
            choice = Prompt.ask(
                "\n[bold cyan]Select configuration option[/]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "0"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self._show_configuration()
            elif choice == "2":
                self._general_settings()
            elif choice == "3":
                self._module_settings()
            elif choice == "4":
                self._network_configuration()
            elif choice == "5":
                self._database_configuration()
            elif choice == "6":
                self._logging_configuration()
            elif choice == "7":
                self._wordlist_management()
            elif choice == "8":
                self._tool_settings()
            elif choice == "9":
                self._backup_restore_menu()
            elif choice == "10":
                self._advanced_settings()
            elif choice == "11":
                self._import_export_menu()
                
    def _show_menu(self):
        """Display configuration menu options."""
        table = Table(title="[bold blue]Configuration Options[/]", box=box.ROUNDED)
        table.add_column("Option", style="bold yellow", justify="center")
        table.add_column("Category", style="bold green")
        table.add_column("Description", style="white")
        
        table.add_row("1", "View Configuration", "Display current configuration settings")
        table.add_row("2", "General Settings", "Basic toolkit configuration")
        table.add_row("3", "Module Settings", "Configure individual modules")
        table.add_row("4", "Network Configuration", "Network and proxy settings")
        table.add_row("5", "Database Configuration", "Database connection and settings")
        table.add_row("6", "Logging Configuration", "Log levels and output settings")
        table.add_row("7", "Wordlist Management", "Manage wordlists and dictionaries")
        table.add_row("8", "Tool Settings", "External tool configuration")
        table.add_row("9", "Backup & Restore", "Configuration backup and restore")
        table.add_row("10", "Advanced Settings", "Advanced configuration options")
        table.add_row("11", "Import/Export", "Import/export configuration")
        table.add_row("0", "Back", "Return to main menu")
        
        self.console.print(table)
        
    def _show_configuration(self, category: str = None):
        """Display configuration settings."""
        if category:
            self.console.print(f"\n[cyan]{category.title()} Configuration:[/]")
            category_config = self.current_config.get(category, {})
            
            if not category_config:
                self.console.print(f"[yellow]No configuration found for category: {category}[/]")
                return
                
            config_table = Table()
            config_table.add_column("Setting", style="cyan")
            config_table.add_column("Value", style="white")
            config_table.add_column("Description", style="dim")
            
            for key, value in category_config.items():
                # Get description from config schema if available
                description = self.config_manager.get_setting_description(category, key)
                config_table.add_row(key, str(value), description)
                
            self.console.print(config_table)
        else:
            # Show all configuration categories
            self.console.print("\n[bold blue]Current Configuration Overview:[/]")
            
            overview_table = Table()
            overview_table.add_column("Category", style="green")
            overview_table.add_column("Settings", style="yellow")
            overview_table.add_column("Status", style="bold")
            
            for category_name, category_data in self.current_config.items():
                if isinstance(category_data, dict):
                    setting_count = len(category_data)
                    status = "[green]Configured[/]" if setting_count > 0 else "[yellow]Default[/]"
                    overview_table.add_row(category_name, str(setting_count), status)
                    
            self.console.print(overview_table)
            
            # Show key settings summary
            self._show_key_settings_summary()
            
    def _show_key_settings_summary(self):
        """Display summary of key configuration settings."""
        key_settings_table = Table(title="Key Settings Summary")
        key_settings_table.add_column("Setting", style="cyan")
        key_settings_table.add_column("Value", style="white")
        
        # Extract key settings
        key_settings = [
            ("Toolkit Version", self.current_config.get("general", {}).get("version", "Unknown")),
            ("Log Level", self.current_config.get("logging", {}).get("level", "INFO")),
            ("Database Type", self.current_config.get("database", {}).get("type", "sqlite")),
            ("Default Threads", self.current_config.get("general", {}).get("default_threads", "10")),
            ("Network Timeout", self.current_config.get("network", {}).get("timeout", "30")),
            ("Auto Save Results", str(self.current_config.get("general", {}).get("auto_save", True)))
        ]
        
        for setting_name, setting_value in key_settings:
            key_settings_table.add_row(setting_name, str(setting_value))
            
        self.console.print(key_settings_table)
        
    def _get_configuration(self, key: str):
        """Get a specific configuration value."""
        if '.' in key:
            # Nested key (e.g., "database.host")
            parts = key.split('.')
            value = self.current_config
            
            try:
                for part in parts:
                    value = value[part]
                self.console.print(f"[cyan]{key}:[/] {value}")
            except KeyError:
                self.console.print(f"[red]Configuration key not found: {key}[/]")
        else:
            # Top-level key
            if key in self.current_config:
                self.console.print(f"[cyan]{key}:[/] {self.current_config[key]}")
            else:
                self.console.print(f"[red]Configuration key not found: {key}[/]")
                
    def _set_configuration(self, key: str, value: str):
        """Set a configuration value."""
        # Convert string value to appropriate type
        converted_value = self._convert_value(value)
        
        if '.' in key:
            # Nested key
            parts = key.split('.')
            config_section = self.current_config
            
            # Navigate to the parent section
            for part in parts[:-1]:
                if part not in config_section:
                    config_section[part] = {}
                config_section = config_section[part]
                
            # Set the value
            config_section[parts[-1]] = converted_value
        else:
            # Top-level key
            self.current_config[key] = converted_value
            
        # Save configuration
        try:
            self.config_manager.save_config(self.current_config)
            self.console.print(f"[green]Configuration updated: {key} = {converted_value}[/]")
        except Exception as e:
            self.console.print(f"[red]Failed to save configuration: {e}[/]")
            
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate Python type."""
        # Try to convert to appropriate type
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"
        elif value.isdigit():
            return int(value)
        elif value.replace(".", "").isdigit():
            return float(value)
        elif value.startswith("[") and value.endswith("]"):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        elif value.startswith("{") and value.endswith("}"):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            return value
            
    def _reset_configuration(self, category: str = None):
        """Reset configuration to defaults."""
        if category:
            if Confirm.ask(f"[red]Reset {category} configuration to defaults?[/]"):
                default_config = self.config_manager.get_default_config()
                if category in default_config:
                    self.current_config[category] = default_config[category].copy()
                    self.config_manager.save_config(self.current_config)
                    self.console.print(f"[green]{category} configuration reset to defaults.[/]")
                else:
                    self.console.print(f"[red]No default configuration found for: {category}[/]")
        else:
            if Confirm.ask("[red]Reset ALL configuration to defaults? This cannot be undone![/]"):
                self.current_config = self.config_manager.get_default_config()
                self.config_manager.save_config(self.current_config)
                self.console.print("[green]All configuration reset to defaults.[/]")
                
    def _general_settings(self):
        """Configure general toolkit settings."""
        self.console.print("\n[bold green]General Settings Configuration[/]")
        
        general_config = self.current_config.get("general", {})
        
        settings = [
            ("default_threads", "Default number of threads", "int", general_config.get("default_threads", 10)),
            ("timeout", "Default timeout (seconds)", "int", general_config.get("timeout", 30)),
            ("auto_save", "Auto-save results", "bool", general_config.get("auto_save", True)),
            ("max_results", "Maximum results per scan", "int", general_config.get("max_results", 1000)),
            ("temp_directory", "Temporary files directory", "str", general_config.get("temp_directory", "/tmp")),
            ("output_directory", "Default output directory", "str", general_config.get("output_directory", "./output")),
            ("verbose_mode", "Enable verbose output", "bool", general_config.get("verbose_mode", False))
        ]
        
        updated_settings = {}
        
        for setting_key, description, setting_type, current_value in settings:
            if Confirm.ask(f"[cyan]Configure {description}? (current: {current_value})[/]"):
                if setting_type == "bool":
                    new_value = Confirm.ask(f"[cyan]{description}[/]", default=current_value)
                elif setting_type == "int":
                    new_value = IntPrompt.ask(f"[cyan]{description}[/]", default=current_value)
                else:
                    new_value = Prompt.ask(f"[cyan]{description}[/]", default=str(current_value))
                    
                updated_settings[setting_key] = new_value
                
        if updated_settings:
            if "general" not in self.current_config:
                self.current_config["general"] = {}
            self.current_config["general"].update(updated_settings)
            
            self.config_manager.save_config(self.current_config)
            self.console.print(f"[green]Updated {len(updated_settings)} general settings.[/]")
            
    def _module_settings(self):
        """Configure individual module settings."""
        self.console.print("\n[bold green]Module Settings Configuration[/]")
        
        modules = {
            "1": ("reconnaissance", "Reconnaissance Module"),
            "2": ("vulnerability", "Vulnerability Assessment Module"),
            "3": ("exploitation", "Exploitation Module"),
            "4": ("post_exploitation", "Post-Exploitation Module"),
            "5": ("reporting", "Reporting Module")
        }
        
        self.console.print("\n[bold yellow]Available Modules:[/]")
        for key, (module_id, desc) in modules.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        module_choice = Prompt.ask(
            "[cyan]Select module to configure[/]",
            choices=list(modules.keys()),
            default="1"
        )
        
        module_name = modules[module_choice][0]
        self._configure_specific_module(module_name)
        
    def _configure_specific_module(self, module_name: str):
        """Configure settings for a specific module."""
        self.console.print(f"\n[cyan]Configuring {module_name.title()} Module:[/]")
        
        module_config = self.current_config.get("modules", {}).get(module_name, {})
        
        # Module-specific settings based on module type
        if module_name == "reconnaissance":
            settings = [
                ("default_scan_type", "Default scan type", ["quick", "comprehensive", "stealth"], 
                 module_config.get("default_scan_type", "quick")),
                ("max_threads", "Maximum threads", "int", module_config.get("max_threads", 50)),
                ("dns_timeout", "DNS timeout (seconds)", "int", module_config.get("dns_timeout", 5)),
                ("port_range", "Default port range", "str", module_config.get("port_range", "1-1000"))
            ]
        elif module_name == "vulnerability":
            settings = [
                ("scan_intensity", "Scan intensity", ["low", "medium", "high"], 
                 module_config.get("scan_intensity", "medium")),
                ("false_positive_reduction", "Enable false positive reduction", "bool", 
                 module_config.get("false_positive_reduction", True)),
                ("max_scan_time", "Maximum scan time (minutes)", "int", 
                 module_config.get("max_scan_time", 60))
            ]
        elif module_name == "exploitation":
            settings = [
                ("auto_exploit", "Enable automatic exploitation", "bool", 
                 module_config.get("auto_exploit", False)),
                ("payload_timeout", "Payload timeout (seconds)", "int", 
                 module_config.get("payload_timeout", 30)),
                ("max_attempts", "Maximum exploitation attempts", "int", 
                 module_config.get("max_attempts", 3))
            ]
        else:
            # Generic settings
            settings = [
                ("enabled", "Module enabled", "bool", module_config.get("enabled", True)),
                ("timeout", "Module timeout (seconds)", "int", module_config.get("timeout", 300))
            ]
            
        updated_settings = {}
        
        for setting_key, description, setting_type, current_value in settings:
            if isinstance(setting_type, list):  # Choice setting
                if Confirm.ask(f"[cyan]Configure {description}? (current: {current_value})[/]"):
                    new_value = Prompt.ask(f"[cyan]{description}[/]", choices=setting_type, default=current_value)
                    updated_settings[setting_key] = new_value
            elif setting_type == "bool":
                if Confirm.ask(f"[cyan]Configure {description}? (current: {current_value})[/]"):
                    new_value = Confirm.ask(f"[cyan]{description}[/]", default=current_value)
                    updated_settings[setting_key] = new_value
            elif setting_type == "int":
                if Confirm.ask(f"[cyan]Configure {description}? (current: {current_value})[/]"):
                    new_value = IntPrompt.ask(f"[cyan]{description}[/]", default=current_value)
                    updated_settings[setting_key] = new_value
            else:  # String setting
                if Confirm.ask(f"[cyan]Configure {description}? (current: {current_value})[/]"):
                    new_value = Prompt.ask(f"[cyan]{description}[/]", default=str(current_value))
                    updated_settings[setting_key] = new_value
                    
        if updated_settings:
            if "modules" not in self.current_config:
                self.current_config["modules"] = {}
            if module_name not in self.current_config["modules"]:
                self.current_config["modules"][module_name] = {}
                
            self.current_config["modules"][module_name].update(updated_settings)
            self.config_manager.save_config(self.current_config)
            self.console.print(f"[green]Updated {len(updated_settings)} {module_name} settings.[/]")
            
    def _network_configuration(self):
        """Configure network and proxy settings."""
        self.console.print("\n[bold green]Network Configuration[/]")
        
        network_config = self.current_config.get("network", {})
        
        # Proxy configuration
        if Confirm.ask("[cyan]Configure proxy settings?[/]"):
            proxy_config = network_config.get("proxy", {})
            
            proxy_config["enabled"] = Confirm.ask("[cyan]Enable proxy?[/]", default=proxy_config.get("enabled", False))
            
            if proxy_config["enabled"]:
                proxy_config["type"] = Prompt.ask(
                    "[cyan]Proxy type[/]",
                    choices=["http", "https", "socks4", "socks5"],
                    default=proxy_config.get("type", "http")
                )
                proxy_config["host"] = Prompt.ask("[cyan]Proxy host[/]", default=proxy_config.get("host", "127.0.0.1"))
                proxy_config["port"] = IntPrompt.ask("[cyan]Proxy port[/]", default=proxy_config.get("port", 8080))
                
                if Confirm.ask("[cyan]Proxy requires authentication?[/]", default=False):
                    proxy_config["username"] = Prompt.ask("[cyan]Username[/]")
                    proxy_config["password"] = Prompt.ask("[cyan]Password[/]", password=True)
                    
            network_config["proxy"] = proxy_config
            
        # Timeout settings
        if Confirm.ask("[cyan]Configure timeout settings?[/]"):
            network_config["connect_timeout"] = IntPrompt.ask(
                "[cyan]Connection timeout (seconds)[/]",
                default=network_config.get("connect_timeout", 10)
            )
            network_config["read_timeout"] = IntPrompt.ask(
                "[cyan]Read timeout (seconds)[/]",
                default=network_config.get("read_timeout", 30)
            )
            
        # SSL/TLS settings
        if Confirm.ask("[cyan]Configure SSL/TLS settings?[/]"):
            ssl_config = network_config.get("ssl", {})
            ssl_config["verify_certificates"] = Confirm.ask(
                "[cyan]Verify SSL certificates?[/]",
                default=ssl_config.get("verify_certificates", True)
            )
            ssl_config["ca_bundle"] = Prompt.ask(
                "[cyan]Custom CA bundle path (optional)[/]",
                default=ssl_config.get("ca_bundle", "")
            )
            network_config["ssl"] = ssl_config
            
        # User agent settings
        if Confirm.ask("[cyan]Configure user agent?[/]"):
            network_config["user_agent"] = Prompt.ask(
                "[cyan]User agent string[/]",
                default=network_config.get("user_agent", "PentestUSB-Toolkit/1.0")
            )
            
        # Save network configuration
        self.current_config["network"] = network_config
        self.config_manager.save_config(self.current_config)
        self.console.print("[green]Network configuration updated.[/]")
        
    def _database_configuration(self):
        """Configure database settings."""
        self.console.print("\n[bold green]Database Configuration[/]")
        
        db_config = self.current_config.get("database", {})
        
        # Database type
        db_type = Prompt.ask(
            "[cyan]Database type[/]",
            choices=["sqlite", "mysql", "postgresql", "mongodb"],
            default=db_config.get("type", "sqlite")
        )
        
        db_config["type"] = db_type
        
        if db_type == "sqlite":
            db_config["file"] = Prompt.ask(
                "[cyan]SQLite database file[/]",
                default=db_config.get("file", "./data/pentest_toolkit.db")
            )
        else:
            # Network database configuration
            db_config["host"] = Prompt.ask("[cyan]Database host[/]", default=db_config.get("host", "localhost"))
            db_config["port"] = IntPrompt.ask(f"[cyan]{db_type.upper()} port[/]", default=db_config.get("port", 3306 if db_type == "mysql" else 5432))
            db_config["database"] = Prompt.ask("[cyan]Database name[/]", default=db_config.get("database", "pentest_toolkit"))
            db_config["username"] = Prompt.ask("[cyan]Username[/]", default=db_config.get("username", ""))
            
            if Confirm.ask("[cyan]Update password?[/]"):
                db_config["password"] = Prompt.ask("[cyan]Password[/]", password=True)
                
        # Connection pool settings
        if Confirm.ask("[cyan]Configure connection pool?[/]"):
            pool_config = db_config.get("pool", {})
            pool_config["max_connections"] = IntPrompt.ask(
                "[cyan]Maximum connections[/]",
                default=pool_config.get("max_connections", 10)
            )
            pool_config["timeout"] = IntPrompt.ask(
                "[cyan]Connection timeout (seconds)[/]",
                default=pool_config.get("timeout", 30)
            )
            db_config["pool"] = pool_config
            
        # Save database configuration
        self.current_config["database"] = db_config
        self.config_manager.save_config(self.current_config)
        self.console.print("[green]Database configuration updated.[/]")
        
        # Test database connection
        if Confirm.ask("[cyan]Test database connection?[/]"):
            self._test_database_connection(db_config)
            
    def _test_database_connection(self, db_config: Dict[str, Any]):
        """Test database connection with current configuration."""
        self.console.print("\n[yellow]Testing database connection...[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Connecting to database...", total=None)
            
            try:
                # Test connection using config manager
                success = self.config_manager.test_database_connection(db_config)
                
                if success:
                    progress.update(task, description="Database connection successful")
                    self.console.print("[green]✅ Database connection successful![/]")
                else:
                    progress.update(task, description="Database connection failed")
                    self.console.print("[red]❌ Database connection failed![/]")
                    
            except Exception as e:
                progress.update(task, description="Database connection error")
                self.console.print(f"[red]❌ Database connection error: {e}[/]")
                
    def _logging_configuration(self):
        """Configure logging settings."""
        self.console.print("\n[bold green]Logging Configuration[/]")
        
        logging_config = self.current_config.get("logging", {})
        
        # Log level
        logging_config["level"] = Prompt.ask(
            "[cyan]Log level[/]",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default=logging_config.get("level", "INFO")
        )
        
        # Log file settings
        if Confirm.ask("[cyan]Configure log file output?[/]"):
            file_config = logging_config.get("file", {})
            file_config["enabled"] = Confirm.ask("[cyan]Enable file logging?[/]", default=file_config.get("enabled", True))
            
            if file_config["enabled"]:
                file_config["path"] = Prompt.ask(
                    "[cyan]Log file path[/]",
                    default=file_config.get("path", "./logs/pentest_toolkit.log")
                )
                file_config["max_size"] = Prompt.ask(
                    "[cyan]Max log file size (MB)[/]",
                    default=str(file_config.get("max_size", "10"))
                )
                file_config["backup_count"] = IntPrompt.ask(
                    "[cyan]Number of backup files[/]",
                    default=file_config.get("backup_count", 5)
                )
                
            logging_config["file"] = file_config
            
        # Console logging
        if Confirm.ask("[cyan]Configure console output?[/]"):
            console_config = logging_config.get("console", {})
            console_config["enabled"] = Confirm.ask("[cyan]Enable console logging?[/]", default=console_config.get("enabled", True))
            console_config["format"] = Prompt.ask(
                "[cyan]Log format[/]",
                default=console_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            logging_config["console"] = console_config
            
        # Module-specific logging
        if Confirm.ask("[cyan]Configure module-specific logging levels?[/]"):
            modules_config = logging_config.get("modules", {})
            
            modules = ["reconnaissance", "vulnerability", "exploitation", "post_exploitation", "reporting"]
            
            for module in modules:
                if Confirm.ask(f"[cyan]Set log level for {module}?[/]"):
                    modules_config[module] = Prompt.ask(
                        f"[cyan]{module.title()} log level[/]",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default=modules_config.get(module, "INFO")
                    )
                    
            logging_config["modules"] = modules_config
            
        # Save logging configuration
        self.current_config["logging"] = logging_config
        self.config_manager.save_config(self.current_config)
        self.console.print("[green]Logging configuration updated.[/]")
        
    def _wordlist_management(self):
        """Manage wordlists and dictionaries."""
        self.console.print("\n[bold green]Wordlist Management[/]")
        
        wordlist_actions = {
            "1": ("list", "List available wordlists"),
            "2": ("add", "Add new wordlist"),
            "3": ("update", "Update existing wordlist"),
            "4": ("remove", "Remove wordlist"),
            "5": ("download", "Download wordlist from URL"),
            "6": ("verify", "Verify wordlist integrity")
        }
        
        self.console.print("\n[bold yellow]Wordlist Actions:[/]")
        for key, (action_id, desc) in wordlist_actions.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        action_choice = Prompt.ask(
            "[cyan]Select action[/]",
            choices=list(wordlist_actions.keys()),
            default="1"
        )
        
        action = wordlist_actions[action_choice][0]
        
        if action == "list":
            self._list_wordlists()
        elif action == "add":
            self._add_wordlist()
        elif action == "update":
            self._update_wordlist()
        elif action == "remove":
            self._remove_wordlist()
        elif action == "download":
            self._download_wordlist()
        elif action == "verify":
            self._verify_wordlists()
            
    def _list_wordlists(self):
        """List available wordlists."""
        wordlists = self.wordlist_manager.list_wordlists()
        
        if not wordlists:
            self.console.print("[yellow]No wordlists found.[/]")
            return
            
        wordlists_table = Table(title="Available Wordlists")
        wordlists_table.add_column("Name", style="cyan")
        wordlists_table.add_column("Category", style="green")
        wordlists_table.add_column("Size", style="yellow")
        wordlists_table.add_column("Description", style="white")
        
        for wordlist in wordlists:
            wordlists_table.add_row(
                wordlist.get("name", "N/A"),
                wordlist.get("category", "N/A"),
                str(wordlist.get("size", "N/A")),
                wordlist.get("description", "N/A")[:50]
            )
            
        self.console.print(wordlists_table)
        
    def _add_wordlist(self):
        """Add a new wordlist."""
        self.console.print("\n[cyan]Adding New Wordlist:[/]")
        
        wordlist_info = {
            "name": Prompt.ask("[cyan]Wordlist name"),
            "category": Prompt.ask("[cyan]Category", choices=["passwords", "usernames", "dns", "web", "other"], default="other"),
            "path": Prompt.ask("[cyan]File path"),
            "description": Prompt.ask("[cyan]Description (optional)", default="")
        }
        
        try:
            self.wordlist_manager.add_wordlist(wordlist_info)
            self.console.print(f"[green]Wordlist '{wordlist_info['name']}' added successfully.[/]")
        except Exception as e:
            self.console.print(f"[red]Failed to add wordlist: {e}[/]")
            
    def _update_wordlist(self):
        """Update an existing wordlist."""
        self._list_wordlists()
        wordlist_name = Prompt.ask("[cyan]Enter wordlist name to update")
        
        try:
            current_info = self.wordlist_manager.get_wordlist_info(wordlist_name)
            if not current_info:
                self.console.print("[red]Wordlist not found.[/]")
                return
                
            # Allow updating specific fields
            updated_info = {}
            
            if Confirm.ask(f"[cyan]Update category? (current: {current_info.get('category')})[/]"):
                updated_info["category"] = Prompt.ask("[cyan]New category", choices=["passwords", "usernames", "dns", "web", "other"])
                
            if Confirm.ask(f"[cyan]Update path? (current: {current_info.get('path')})[/]"):
                updated_info["path"] = Prompt.ask("[cyan]New file path")
                
            if Confirm.ask(f"[cyan]Update description? (current: {current_info.get('description')})[/]"):
                updated_info["description"] = Prompt.ask("[cyan]New description")
                
            if updated_info:
                self.wordlist_manager.update_wordlist(wordlist_name, updated_info)
                self.console.print(f"[green]Wordlist '{wordlist_name}' updated successfully.[/]")
            else:
                self.console.print("[yellow]No changes made.[/]")
                
        except Exception as e:
            self.console.print(f"[red]Failed to update wordlist: {e}[/]")
            
    def _remove_wordlist(self):
        """Remove a wordlist."""
        self._list_wordlists()
        wordlist_name = Prompt.ask("[cyan]Enter wordlist name to remove")
        
        if Confirm.ask(f"[red]Remove wordlist '{wordlist_name}'?[/]"):
            try:
                self.wordlist_manager.remove_wordlist(wordlist_name)
                self.console.print(f"[green]Wordlist '{wordlist_name}' removed successfully.[/]")
            except Exception as e:
                self.console.print(f"[red]Failed to remove wordlist: {e}[/]")
                
    def _download_wordlist(self):
        """Download wordlist from URL."""
        self.console.print("\n[cyan]Download Wordlist from URL:[/]")
        
        url = Prompt.ask("[cyan]Wordlist URL")
        name = Prompt.ask("[cyan]Wordlist name")
        category = Prompt.ask("[cyan]Category", choices=["passwords", "usernames", "dns", "web", "other"], default="other")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Downloading wordlist...", total=None)
            
            try:
                self.wordlist_manager.download_wordlist(url, name, category)
                progress.update(task, description="Download completed")
                self.console.print(f"[green]Wordlist '{name}' downloaded successfully.[/]")
            except Exception as e:
                progress.update(task, description="Download failed")
                self.console.print(f"[red]Failed to download wordlist: {e}[/]")
                
    def _verify_wordlists(self):
        """Verify wordlist integrity."""
        self.console.print("\n[yellow]Verifying wordlist integrity...[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Verifying wordlists...", total=None)
            
            try:
                verification_results = self.wordlist_manager.verify_wordlists()
                progress.update(task, description="Verification completed")
                
                # Display results
                results_table = Table(title="Wordlist Verification Results")
                results_table.add_column("Wordlist", style="cyan")
                results_table.add_column("Status", style="bold")
                results_table.add_column("Issues", style="yellow")
                
                for wordlist, result in verification_results.items():
                    status = "[green]OK[/]" if result["valid"] else "[red]ERROR[/]"
                    issues = ", ".join(result.get("issues", []))
                    results_table.add_row(wordlist, status, issues)
                    
                self.console.print(results_table)
                
            except Exception as e:
                progress.update(task, description="Verification failed")
                self.console.print(f"[red]Wordlist verification failed: {e}[/]")
                
    def _tool_settings(self):
        """Configure external tool settings."""
        self.console.print("\n[bold green]External Tool Configuration[/]")
        
        tools_config = self.current_config.get("tools", {})
        
        # Common tools
        tools = [
            ("nmap", "Nmap Network Scanner", "/usr/bin/nmap"),
            ("nikto", "Nikto Web Scanner", "/usr/bin/nikto"),
            ("sqlmap", "SQLMap", "/usr/bin/sqlmap"),
            ("hydra", "Hydra", "/usr/bin/hydra"),
            ("dirb", "Dirb", "/usr/bin/dirb"),
            ("gobuster", "Gobuster", "/usr/bin/gobuster"),
            ("john", "John the Ripper", "/usr/bin/john"),
            ("hashcat", "Hashcat", "/usr/bin/hashcat")
        ]
        
        for tool_name, tool_desc, default_path in tools:
            if Confirm.ask(f"[cyan]Configure {tool_desc}?[/]"):
                tool_config = tools_config.get(tool_name, {})
                tool_config["path"] = Prompt.ask(f"[cyan]{tool_name} path[/]", default=tool_config.get("path", default_path))
                tool_config["enabled"] = Confirm.ask(f"[cyan]Enable {tool_name}?[/]", default=tool_config.get("enabled", True))
                
                # Tool-specific options
                if tool_name == "nmap":
                    tool_config["default_options"] = Prompt.ask(
                        "[cyan]Default nmap options[/]",
                        default=tool_config.get("default_options", "-sV -sC")
                    )
                elif tool_name == "sqlmap":
                    tool_config["default_options"] = Prompt.ask(
                        "[cyan]Default sqlmap options[/]",
                        default=tool_config.get("default_options", "--batch --random-agent")
                    )
                    
                tools_config[tool_name] = tool_config
                
        # Save tools configuration
        self.current_config["tools"] = tools_config
        self.config_manager.save_config(self.current_config)
        self.console.print("[green]Tool configuration updated.[/]")
        
    def _backup_restore_menu(self):
        """Backup and restore configuration menu."""
        self.console.print("\n[bold green]Backup & Restore Configuration[/]")
        
        backup_actions = {
            "1": ("backup", "Create configuration backup"),
            "2": ("restore", "Restore from backup"),
            "3": ("list", "List available backups"),
            "4": ("auto", "Configure automatic backups")
        }
        
        self.console.print("\n[bold yellow]Backup Actions:[/]")
        for key, (action_id, desc) in backup_actions.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        action_choice = Prompt.ask(
            "[cyan]Select action[/]",
            choices=list(backup_actions.keys()),
            default="1"
        )
        
        action = backup_actions[action_choice][0]
        
        if action == "backup":
            self._backup_configuration()
        elif action == "restore":
            self._restore_configuration()
        elif action == "list":
            self._list_configuration_backups()
        elif action == "auto":
            self._configure_auto_backup()
            
    def _backup_configuration(self):
        """Create configuration backup."""
        backup_name = Prompt.ask(
            "[cyan]Backup name[/]",
            default=f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        try:
            backup_file = self.config_manager.create_backup(backup_name)
            self.console.print(f"[green]Configuration backed up to: {backup_file}[/]")
        except Exception as e:
            self.console.print(f"[red]Backup failed: {e}[/]")
            
    def _restore_configuration(self, backup_file: str = None):
        """Restore configuration from backup."""
        if not backup_file:
            # List available backups
            backups = self.config_manager.list_backups()
            
            if not backups:
                self.console.print("[yellow]No backups found.[/]")
                return
                
            self.console.print("\n[cyan]Available Backups:[/]")
            for i, backup in enumerate(backups, 1):
                self.console.print(f"[yellow]{i}[/] - {backup}")
                
            backup_choice = IntPrompt.ask(f"[cyan]Select backup[/] (1-{len(backups)})")
            backup_file = backups[backup_choice - 1]
            
        if Confirm.ask(f"[red]Restore configuration from '{backup_file}'? This will overwrite current settings![/]"):
            try:
                self.config_manager.restore_backup(backup_file)
                self.current_config = self.config_manager.load_config()
                self.console.print(f"[green]Configuration restored from: {backup_file}[/]")
            except Exception as e:
                self.console.print(f"[red]Restore failed: {e}[/]")
                
    def _list_configuration_backups(self):
        """List available configuration backups."""
        try:
            backups = self.config_manager.list_backups()
            
            if not backups:
                self.console.print("[yellow]No backups found.[/]")
                return
                
            backups_table = Table(title="Configuration Backups")
            backups_table.add_column("Name", style="cyan")
            backups_table.add_column("Date", style="yellow")
            backups_table.add_column("Size", style="green")
            
            for backup in backups:
                # Get backup info
                backup_info = self.config_manager.get_backup_info(backup)
                backups_table.add_row(
                    backup,
                    backup_info.get("date", "Unknown"),
                    backup_info.get("size", "Unknown")
                )
                
            self.console.print(backups_table)
            
        except Exception as e:
            self.console.print(f"[red]Failed to list backups: {e}[/]")
            
    def _configure_auto_backup(self):
        """Configure automatic backup settings."""
        auto_backup_config = self.current_config.get("backup", {})
        
        auto_backup_config["enabled"] = Confirm.ask("[cyan]Enable automatic backups?[/]", default=auto_backup_config.get("enabled", False))
        
        if auto_backup_config["enabled"]:
            auto_backup_config["interval"] = Prompt.ask(
                "[cyan]Backup interval[/]",
                choices=["daily", "weekly", "monthly"],
                default=auto_backup_config.get("interval", "weekly")
            )
            auto_backup_config["keep_count"] = IntPrompt.ask(
                "[cyan]Number of backups to keep[/]",
                default=auto_backup_config.get("keep_count", 5)
            )
            
        self.current_config["backup"] = auto_backup_config
        self.config_manager.save_config(self.current_config)
        self.console.print("[green]Auto-backup configuration updated.[/]")
        
    def _advanced_settings(self):
        """Configure advanced settings."""
        self.console.print("\n[bold green]Advanced Configuration Settings[/]")
        
        advanced_config = self.current_config.get("advanced", {})
        
        # Performance settings
        if Confirm.ask("[cyan]Configure performance settings?[/]"):
            perf_config = advanced_config.get("performance", {})
            perf_config["max_memory_usage"] = Prompt.ask(
                "[cyan]Maximum memory usage (MB)[/]",
                default=str(perf_config.get("max_memory_usage", "1024"))
            )
            perf_config["cpu_limit"] = IntPrompt.ask(
                "[cyan]CPU usage limit (%)[/]",
                default=perf_config.get("cpu_limit", 80)
            )
            advanced_config["performance"] = perf_config
            
        # Security settings
        if Confirm.ask("[cyan]Configure security settings?[/]"):
            security_config = advanced_config.get("security", {})
            security_config["encryption_key_rotation"] = Confirm.ask(
                "[cyan]Enable encryption key rotation?[/]",
                default=security_config.get("encryption_key_rotation", True)
            )
            security_config["audit_logging"] = Confirm.ask(
                "[cyan]Enable audit logging?[/]",
                default=security_config.get("audit_logging", True)
            )
            advanced_config["security"] = security_config
            
        # API settings
        if Confirm.ask("[cyan]Configure API settings?[/]"):
            api_config = advanced_config.get("api", {})
            api_config["rate_limit"] = IntPrompt.ask(
                "[cyan]API rate limit (requests/minute)[/]",
                default=api_config.get("rate_limit", 100)
            )
            api_config["enable_cors"] = Confirm.ask(
                "[cyan]Enable CORS?[/]",
                default=api_config.get("enable_cors", False)
            )
            advanced_config["api"] = api_config
            
        self.current_config["advanced"] = advanced_config
        self.config_manager.save_config(self.current_config)
        self.console.print("[green]Advanced settings updated.[/]")
        
    def _import_export_menu(self):
        """Import/export configuration menu."""
        self.console.print("\n[bold green]Import/Export Configuration[/]")
        
        ie_actions = {
            "1": ("export", "Export configuration"),
            "2": ("import", "Import configuration"),
            "3": ("template", "Export configuration template")
        }
        
        self.console.print("\n[bold yellow]Import/Export Actions:[/]")
        for key, (action_id, desc) in ie_actions.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        action_choice = Prompt.ask(
            "[cyan]Select action[/]",
            choices=list(ie_actions.keys()),
            default="1"
        )
        
        action = ie_actions[action_choice][0]
        
        if action == "export":
            format_type = Prompt.ask("[cyan]Export format[/]", choices=["json", "yaml", "ini"], default="json")
            self._export_configuration(format_type)
        elif action == "import":
            self._import_configuration()
        elif action == "template":
            self._export_configuration_template()
            
    def _export_configuration(self, format_type: str = "json"):
        """Export configuration to file."""
        filename = Prompt.ask(
            "[cyan]Export filename[/]",
            default=f"pentest_toolkit_config.{format_type}"
        )
        
        try:
            export_file = self.config_manager.export_config(self.current_config, filename, format_type)
            self.console.print(f"[green]Configuration exported to: {export_file}[/]")
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/]")
            
    def _import_configuration(self):
        """Import configuration from file."""
        config_file = Prompt.ask("[cyan]Configuration file path")
        
        if not Path(config_file).exists():
            self.console.print(f"[red]Configuration file not found: {config_file}[/]")
            return
            
        if Confirm.ask("[red]Import configuration? This will overwrite current settings![/]"):
            try:
                imported_config = self.config_manager.import_config(config_file)
                self.current_config = imported_config
                self.config_manager.save_config(self.current_config)
                self.console.print(f"[green]Configuration imported from: {config_file}[/]")
            except Exception as e:
                self.console.print(f"[red]Import failed: {e}[/]")
                
    def _export_configuration_template(self):
        """Export configuration template with default values and comments."""
        template_file = Prompt.ask(
            "[cyan]Template filename[/]",
            default="pentest_toolkit_template.json"
        )
        
        try:
            template_config = self.config_manager.get_config_template()
            export_file = self.config_manager.export_config(template_config, template_file, "json")
            self.console.print(f"[green]Configuration template exported to: {export_file}[/]")
        except Exception as e:
            self.console.print(f"[red]Template export failed: {e}[/]")
            
    def _show_help(self):
        """Display help information."""
        help_text = """
[bold blue]Configuration Module Help[/]

[bold yellow]Available Commands:[/]
  config show [category]       - Display configuration settings
  config set <key> <value>     - Set a configuration value
  config get <key>             - Get a configuration value
  config reset [category]      - Reset configuration to defaults
  config backup                - Create configuration backup
  config restore [file]        - Restore from backup
  config export [format]       - Export configuration to file
  config wordlists             - Manage wordlists and dictionaries
  config database              - Configure database settings
  config logging               - Configure logging settings
  config network               - Configure network settings

[bold yellow]Interactive Mode:[/]
  Run 'config' without arguments to enter interactive mode

[bold yellow]Examples:[/]
  config show general
  config set general.timeout 60
  config get database.type
  config backup
  config export json

[bold yellow]Configuration Categories:[/]
  general      - Basic toolkit settings
  modules      - Module-specific configuration
  network      - Network and proxy settings
  database     - Database connection settings
  logging      - Log levels and output settings
  tools        - External tool configuration
  advanced     - Advanced configuration options
"""
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))


if __name__ == "__main__":
    import sys
    config_cli = ConfigCLI()
    config_cli.run(sys.argv[1:] if len(sys.argv) > 1 else [])