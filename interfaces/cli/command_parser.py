#!/usr/bin/env python3
"""
Command Parser for Pentest-USB Toolkit CLI
==========================================

Advanced command parsing with argument validation, help system,
and command history management.
"""

import re
import shlex
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box


@dataclass
class CommandArgument:
    """Represents a command argument with validation rules."""
    name: str
    description: str
    required: bool = False
    arg_type: str = "string"  # string, int, float, bool, path, ip, url
    choices: Optional[List[str]] = None
    default: Optional[Any] = None
    validator: Optional[callable] = None
    

@dataclass
class Command:
    """Represents a CLI command with arguments and metadata."""
    name: str
    description: str
    usage: str
    arguments: List[CommandArgument] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    category: str = "general"
    

class CommandParser:
    """Advanced command parser with validation and help system."""
    
    def __init__(self):
        """Initialize the command parser."""
        self.console = Console()
        self.commands: Dict[str, Command] = {}
        
        # Register built-in commands
        self._register_builtin_commands()
        
    def _register_builtin_commands(self):
        """Register all built-in commands with their arguments."""
        
        # Help command
        help_cmd = Command(
            name="help",
            description="Show help information for commands",
            usage="help [command]",
            arguments=[
                CommandArgument("command", "Command to show help for", required=False)
            ],
            aliases=["h", "?"],
            examples=["help", "help scan", "help exploit"],
            category="general"
        )
        self.register_command(help_cmd)
        
        # Scan command
        scan_cmd = Command(
            name="scan",
            description="Start network or web scanning",
            usage="scan <target> [options]",
            arguments=[
                CommandArgument("target", "Target IP, domain, or network range", required=True, arg_type="string"),
                CommandArgument("--type", "Scan type", choices=["quick", "full", "stealth", "aggressive"], default="quick"),
                CommandArgument("--ports", "Port range to scan", default="1-1000"),
                CommandArgument("--output", "Output file path", arg_type="path"),
                CommandArgument("--threads", "Number of threads", arg_type="int", default=10),
                CommandArgument("--timeout", "Connection timeout in seconds", arg_type="int", default=5)
            ],
            aliases=["s"],
            examples=[
                "scan 192.168.1.1",
                "scan example.com --type full --ports 1-65535",
                "scan 192.168.1.0/24 --output scan_results.json"
            ],
            category="reconnaissance"
        )
        self.register_command(scan_cmd)
        
        # Exploit command
        exploit_cmd = Command(
            name="exploit",
            description="Execute exploitation modules",
            usage="exploit <vulnerability> [options]",
            arguments=[
                CommandArgument("vulnerability", "Vulnerability type or CVE", required=True),
                CommandArgument("--target", "Target host or URL", required=True),
                CommandArgument("--payload", "Payload to use", choices=["reverse_shell", "bind_shell", "meterpreter"]),
                CommandArgument("--lhost", "Local host for reverse connections", arg_type="ip"),
                CommandArgument("--lport", "Local port for reverse connections", arg_type="int", default=4444),
                CommandArgument("--verify", "Verify exploit success", arg_type="bool", default=True)
            ],
            aliases=["exp"],
            examples=[
                "exploit sql_injection --target http://example.com/login",
                "exploit CVE-2021-44228 --target 192.168.1.100 --payload reverse_shell",
                "exploit rce --target http://vulnerable.com --lhost 192.168.1.50"
            ],
            category="exploitation"
        )
        self.register_command(exploit_cmd)
        
        # Report command
        report_cmd = Command(
            name="report",
            description="Generate security assessment reports",
            usage="report [options]",
            arguments=[
                CommandArgument("--format", "Report format", choices=["pdf", "html", "docx", "json"], default="pdf"),
                CommandArgument("--template", "Report template", choices=["default", "executive", "technical", "compliance"]),
                CommandArgument("--output", "Output file path", arg_type="path"),
                CommandArgument("--project", "Project ID or name"),
                CommandArgument("--include", "Sections to include", choices=["summary", "vulnerabilities", "recommendations", "all"], default="all")
            ],
            aliases=["rep"],
            examples=[
                "report --format pdf --template executive",
                "report --format html --output custom_report.html",
                "report --project pentest_2024 --include vulnerabilities"
            ],
            category="reporting"
        )
        self.register_command(report_cmd)
        
        # Project command
        project_cmd = Command(
            name="project",
            description="Manage scan projects and sessions",
            usage="project <action> [options]",
            arguments=[
                CommandArgument("action", "Project action", required=True, choices=["list", "new", "load", "delete", "export"]),
                CommandArgument("name", "Project name", required=False),
                CommandArgument("--target", "Project target"),
                CommandArgument("--description", "Project description"),
                CommandArgument("--template", "Project template")
            ],
            aliases=["proj"],
            examples=[
                "project list",
                "project new MyProject --target 192.168.1.0/24",
                "project load MyProject",
                "project export MyProject --format json"
            ],
            category="project"
        )
        self.register_command(project_cmd)
        
        # Config command
        config_cmd = Command(
            name="config",
            description="Manage toolkit configuration",
            usage="config <action> [key] [value]",
            arguments=[
                CommandArgument("action", "Config action", required=True, choices=["show", "set", "get", "reset"]),
                CommandArgument("key", "Configuration key", required=False),
                CommandArgument("value", "Configuration value", required=False)
            ],
            aliases=["cfg"],
            examples=[
                "config show",
                "config set scan.timeout 10",
                "config get api.shodan.key",
                "config reset scan.threads"
            ],
            category="configuration"
        )
        self.register_command(config_cmd)
        
        # Dashboard command
        dashboard_cmd = Command(
            name="dashboard",
            description="Launch real-time monitoring dashboard",
            usage="dashboard [options]",
            arguments=[
                CommandArgument("--refresh", "Refresh interval in seconds", arg_type="int", default=2),
                CommandArgument("--fullscreen", "Launch in fullscreen mode", arg_type="bool", default=False)
            ],
            aliases=["dash"],
            examples=[
                "dashboard",
                "dashboard --refresh 1 --fullscreen true"
            ],
            category="general"
        )
        self.register_command(dashboard_cmd)
        
    def register_command(self, command: Command):
        """Register a new command."""
        self.commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self.commands[alias] = command
            
    def parse(self, command_line: str) -> Optional[Dict[str, Any]]:
        """Parse command line into structured command data."""
        if not command_line.strip():
            return None
            
        try:
            # Split command line respecting quotes
            parts = shlex.split(command_line)
        except ValueError as e:
            self.console.print(f"[red]Command parsing error: {e}[/]")
            return None
            
        if not parts:
            return None
            
        cmd_name = parts[0].lower()
        args = parts[1:]
        
        # Find command (including aliases)
        command = self.commands.get(cmd_name)
        if not command:
            self.console.print(f"[red]Unknown command: {cmd_name}[/]")
            self.console.print("Type 'help' for available commands.")
            return None
            
        # Parse arguments
        parsed_args = self._parse_arguments(command, args)
        if parsed_args is None:
            return None
            
        return {
            'command': command.name,
            'args': parsed_args.get('positional', []),
            'options': parsed_args.get('options', {}),
            'raw_args': args
        }
        
    def _parse_arguments(self, command: Command, args: List[str]) -> Optional[Dict[str, Any]]:
        """Parse command arguments according to command definition."""
        positional_args = []
        options = {}
        i = 0
        
        while i < len(args):
            arg = args[i]
            
            if arg.startswith('--'):
                # Long option
                option_name = arg[2:]
                
                # Find argument definition
                arg_def = None
                for cmd_arg in command.arguments:
                    if cmd_arg.name == option_name or cmd_arg.name == f"--{option_name}":
                        arg_def = cmd_arg
                        break
                        
                if not arg_def:
                    self.console.print(f"[red]Unknown option: {arg}[/]")
                    return None
                    
                # Get option value
                if arg_def.arg_type == "bool":
                    options[option_name] = True
                    i += 1
                else:
                    if i + 1 >= len(args):
                        self.console.print(f"[red]Option {arg} requires a value[/]")
                        return None
                    value = args[i + 1]
                    
                    # Validate value
                    validated_value = self._validate_argument_value(arg_def, value)
                    if validated_value is None:
                        return None
                    options[option_name] = validated_value
                    i += 2
                    
            elif arg.startswith('-') and len(arg) == 2:
                # Short option (not implemented for simplicity)
                self.console.print(f"[red]Short options not supported: {arg}[/]")
                return None
            else:
                # Positional argument
                positional_args.append(arg)
                i += 1
                
        # Validate required positional arguments
        required_positional = [arg for arg in command.arguments if arg.required and not arg.name.startswith('--')]
        
        if len(positional_args) < len(required_positional):
            missing_args = required_positional[len(positional_args):]
            self.console.print(f"[red]Missing required arguments: {', '.join(arg.name for arg in missing_args)}[/]")
            return None
            
        # Set default values for missing options
        for arg_def in command.arguments:
            if arg_def.name.startswith('--'):
                option_name = arg_def.name[2:]
                if option_name not in options and arg_def.default is not None:
                    options[option_name] = arg_def.default
                    
        return {
            'positional': positional_args,
            'options': options
        }
        
    def _validate_argument_value(self, arg_def: CommandArgument, value: str) -> Optional[Any]:
        """Validate argument value according to type and constraints."""
        
        # Type conversion
        try:
            if arg_def.arg_type == "int":
                converted_value = int(value)
            elif arg_def.arg_type == "float":
                converted_value = float(value)
            elif arg_def.arg_type == "bool":
                converted_value = value.lower() in ("true", "1", "yes", "on")
            elif arg_def.arg_type == "path":
                converted_value = Path(value)
            else:
                converted_value = value
        except ValueError:
            self.console.print(f"[red]Invalid {arg_def.arg_type} value for {arg_def.name}: {value}[/]")
            return None
            
        # Choices validation
        if arg_def.choices and converted_value not in arg_def.choices:
            self.console.print(f"[red]Invalid choice for {arg_def.name}: {value}[/]")
            self.console.print(f"[yellow]Valid choices: {', '.join(arg_def.choices)}[/]")
            return None
            
        # Custom validator
        if arg_def.validator and not arg_def.validator(converted_value):
            self.console.print(f"[red]Validation failed for {arg_def.name}: {value}[/]")
            return None
            
        # Type-specific validation
        if arg_def.arg_type == "ip":
            if not self._validate_ip_address(str(converted_value)):
                self.console.print(f"[red]Invalid IP address: {value}[/]")
                return None
        elif arg_def.arg_type == "url":
            if not self._validate_url(str(converted_value)):
                self.console.print(f"[red]Invalid URL: {value}[/]")
                return None
                
        return converted_value
        
    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format."""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
            
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        return bool(url_pattern.match(url))
        
    def show_command_help(self, command_name: str):
        """Show detailed help for a specific command."""
        command = self.commands.get(command_name.lower())
        
        if not command:
            self.console.print(f"[red]Unknown command: {command_name}[/]")
            self.show_general_help()
            return
            
        # Command header
        help_panel = []
        help_panel.append(f"[bold cyan]{command.name}[/] - {command.description}")
        help_panel.append("")
        
        # Usage
        help_panel.append(f"[bold yellow]Usage:[/] {command.usage}")
        help_panel.append("")
        
        # Arguments
        if command.arguments:
            help_panel.append("[bold yellow]Arguments:[/]")
            
            args_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
            args_table.add_column("Argument", style="green")
            args_table.add_column("Description", style="white")
            args_table.add_column("Details", style="dim")
            
            for arg in command.arguments:
                details = []
                if arg.required:
                    details.append("required")
                if arg.default is not None:
                    details.append(f"default: {arg.default}")
                if arg.choices:
                    details.append(f"choices: {', '.join(arg.choices)}")
                    
                args_table.add_row(
                    arg.name,
                    arg.description,
                    " | ".join(details) if details else ""
                )
                
            help_panel.append("")
            
        # Examples
        if command.examples:
            help_panel.append("[bold yellow]Examples:[/]")
            for example in command.examples:
                help_panel.append(f"  [dim]$[/] [green]{example}[/]")
            help_panel.append("")
            
        # Aliases
        if command.aliases:
            help_panel.append(f"[bold yellow]Aliases:[/] {', '.join(command.aliases)}")
            help_panel.append("")
            
        help_content = "\n".join(help_panel)
        
        if command.arguments:
            # Create layout with table
            from rich.columns import Columns
            
            content = Text()
            content.append_text(Text.from_markup("\n".join(help_panel[:-1])))
            
            panel = Panel(
                Columns([content, args_table], equal=False, expand=True),
                title=f"Help: {command.name}",
                border_style="blue"
            )
        else:
            panel = Panel(
                help_content,
                title=f"Help: {command.name}",
                border_style="blue"
            )
            
        self.console.print(panel)
        
    def show_general_help(self):
        """Show general help with all available commands."""
        # Group commands by category
        categories = {}
        for cmd_name, command in self.commands.items():
            if cmd_name == command.name:  # Skip aliases
                category = command.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(command)
                
        help_text = ["[bold cyan]Available Commands[/]", ""]
        
        for category, commands in sorted(categories.items()):
            help_text.append(f"[bold yellow]{category.title()}:[/]")
            
            for command in sorted(commands, key=lambda x: x.name):
                aliases_str = f" ({', '.join(command.aliases)})" if command.aliases else ""
                help_text.append(f"  [green]{command.name}[/]{aliases_str} - {command.description}")
                
            help_text.append("")
            
        help_text.append("[dim]Use 'help <command>' for detailed command help.[/]")
        
        self.console.print(Panel(
            "\n".join(help_text),
            title="Help",
            border_style="blue"
        ))
        
    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions for auto-completion."""
        suggestions = []
        partial_lower = partial_command.lower()
        
        for cmd_name, command in self.commands.items():
            if cmd_name.startswith(partial_lower):
                suggestions.append(cmd_name)
                
        return sorted(suggestions)


# Example usage and testing
if __name__ == "__main__":
    parser = CommandParser()
    console = Console()
    
    # Test command parsing
    test_commands = [
        "help",
        "help scan",
        "scan 192.168.1.1 --type full --ports 1-1000",
        "exploit sql_injection --target http://example.com --payload reverse_shell",
        "report --format pdf --template executive",
        "project new TestProject --target 192.168.1.0/24"
    ]
    
    for cmd in test_commands:
        console.print(f"\n[bold]Testing:[/] {cmd}")
        result = parser.parse(cmd)
        if result:
            console.print(f"[green]Parsed:[/] {result}")
        else:
            console.print("[red]Parsing failed[/]")