#!/usr/bin/env python3
"""
Main CLI Interface for Pentest-USB Toolkit
==========================================

Entry point for the command-line interface with interactive menu system,
real-time dashboard, and comprehensive command management.

Usage:
    python main_cli.py
    ./launch.sh
"""

import sys
import os
import argparse
import signal
import threading
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Core imports
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
import click

# Local imports
from .dashboard import Dashboard
from .menu_system import MenuSystem
from .command_parser import CommandParser
from .utils import CLIUtils
from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import get_logger

class PentestCLI:
    """Main CLI application class for Pentest-USB Toolkit."""
    
    def __init__(self):
        """Initialize the CLI application."""
        self.console = Console()
        self.dashboard = Dashboard()
        self.menu_system = MenuSystem()
        self.command_parser = CommandParser()
        self.utils = CLIUtils()
        self.logger = get_logger("CLI")
        
        # Application state
        self.running = True
        self.current_project = None
        self.orchestrator = None
        self.live_dashboard = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.console.print("\n[yellow]Received shutdown signal. Cleaning up...[/]")
        self.shutdown()
        
    def startup_banner(self):
        """Display the startup banner and version information."""
        banner = """
[bold red]
   ██████╗ ███████╗███╗   ██╗████████╗███████╗███████╗████████╗      ██╗   ██╗███████╗██████╗ 
   ██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝      ██║   ██║██╔════╝██╔══██╗
   ██████╔╝█████╗  ██╔██╗ ██║   ██║   █████╗  ███████╗   ██║   █████╗██║   ██║███████╗██████╔╝
   ██╔═══╝ ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ╚════██║   ██║   ╚════╝██║   ██║╚════██║██╔══██╗
   ██║     ███████╗██║ ╚████║   ██║   ███████╗███████║   ██║         ╚██████╔╝███████║██████╔╝
   ╚═╝     ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝   ╚═╝          ╚═════╝ ╚══════╝╚═════╝ 
[/]
[bold cyan]                           PENETRATION TESTING USB TOOLKIT[/]
[dim]                                    Version 1.0.0[/]
[dim]                              Portable Security Framework[/]
"""
        
        self.console.print(Panel(
            banner,
            title="[bold green]LeZelote Toolkit[/]",
            border_style="green",
            box=box.DOUBLE_EDGE
        ))
        
        # System information
        self.console.print(self.utils.get_system_info())
        
    def show_main_menu(self):
        """Display the main menu options."""
        menu_options = [
            ("1", "Reconnaissance", "Network scanning and OSINT gathering"),
            ("2", "Vulnerability Assessment", "Scan for security vulnerabilities"),
            ("3", "Exploitation", "Execute exploits and gain access"),
            ("4", "Post-Exploitation", "Privilege escalation and persistence"),
            ("5", "Reporting", "Generate comprehensive reports"),
            ("6", "Project Management", "Manage scan projects and sessions"),
            ("7", "Configuration", "Tool settings and preferences"),
            ("8", "Dashboard", "Real-time monitoring dashboard"),
            ("9", "Help & Documentation", "View help and documentation"),
            ("0", "Exit", "Exit the application")
        ]
        
        table = Table(title="[bold cyan]Main Menu[/]", box=box.ROUNDED)
        table.add_column("Option", style="bold yellow", justify="center")
        table.add_column("Module", style="bold green")
        table.add_column("Description", style="dim")
        
        for option, module, desc in menu_options:
            table.add_row(option, module, desc)
            
        self.console.print(table)
        
    def interactive_shell(self):
        """Run the interactive command shell."""
        self.console.print("\n[bold green]Interactive Mode Started[/]")
        self.console.print("[dim]Type 'help' for available commands, 'exit' to quit[/]\n")
        
        while self.running:
            try:
                # Get user input
                command = Prompt.ask(
                    "[bold cyan]pentest-usb[/]",
                    default="help"
                ).strip()
                
                if not command or command.lower() in ['exit', 'quit', 'q']:
                    break
                    
                # Parse and execute command
                self.execute_command(command)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit properly.[/]")
            except Exception as e:
                self.logger.error(f"Command execution error: {e}")
                self.console.print(f"[red]Error: {e}[/]")
                
    def execute_command(self, command: str):
        """Execute a parsed command."""
        try:
            # Parse command
            parsed = self.command_parser.parse(command)
            
            if not parsed:
                return
                
            cmd_type = parsed.get('command')
            
            # Route commands to appropriate handlers
            if cmd_type == 'help':
                self.show_help(parsed.get('args', []))
            elif cmd_type == 'menu':
                self.show_main_menu()
            elif cmd_type == 'dashboard':
                self.show_dashboard()
            elif cmd_type == 'scan':
                self.handle_scan_command(parsed)
            elif cmd_type == 'exploit':
                self.handle_exploit_command(parsed)
            elif cmd_type == 'report':
                self.handle_report_command(parsed)
            elif cmd_type == 'project':
                self.handle_project_command(parsed)
            elif cmd_type == 'config':
                self.handle_config_command(parsed)
            elif cmd_type in ['recon', 'reconnaissance']:
                self.launch_module('reconnaissance', parsed.get('args', []))
            elif cmd_type in ['vuln', 'vulnerability']:
                self.launch_module('vulnerability', parsed.get('args', []))
            elif cmd_type in ['postexploit', 'post-exploit']:
                self.launch_module('post_exploit', parsed.get('args', []))
            else:
                self.console.print(f"[red]Unknown command: {cmd_type}[/]")
                self.console.print("Type 'help' for available commands.")
                
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            self.console.print(f"[red]Command failed: {e}[/]")
            
    def show_help(self, args: List[str]):
        """Show help information for commands."""
        if not args:
            # Show general help
            help_text = """
[bold cyan]Pentest-USB Toolkit - Command Reference[/]

[bold yellow]General Commands:[/]
  help [command]     - Show this help or help for specific command
  menu              - Show main menu
  dashboard         - Launch real-time dashboard
  exit/quit         - Exit the application

[bold yellow]Core Operations:[/]
  scan <target>     - Start network/web scanning
  exploit <vuln>    - Execute exploitation modules
  report <format>   - Generate security reports
  
[bold yellow]Module Commands:[/]
  recon [options]   - Launch reconnaissance module
  vuln [options]    - Launch vulnerability assessment
  postexploit       - Launch post-exploitation module
  
[bold yellow]Project Management:[/]
  project list      - List all projects
  project new <name> - Create new project
  project load <id> - Load existing project
  
[bold yellow]Configuration:[/]
  config show       - Show current configuration
  config set <key> <value> - Set configuration value
  
[dim]Use 'help <command>' for detailed help on specific commands.[/]
"""
            self.console.print(Panel(help_text, title="Help", border_style="blue"))
        else:
            # Show specific command help
            self.command_parser.show_command_help(args[0])
            
    def show_dashboard(self):
        """Launch the real-time dashboard."""
        self.console.print("[bold green]Launching Real-time Dashboard...[/]")
        
        try:
            # Create dashboard layout
            layout = self.dashboard.create_layout()
            
            with Live(layout, refresh_per_second=2, screen=True) as live:
                self.live_dashboard = live
                
                while True:
                    # Update dashboard data
                    self.dashboard.update_system_metrics()
                    self.dashboard.update_scan_progress()
                    self.dashboard.update_threat_levels()
                    
                    # Update the live display
                    live.update(self.dashboard.create_layout())
                    
                    time.sleep(0.5)
                    
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard closed.[/]")
        finally:
            self.live_dashboard = None
            
    def handle_scan_command(self, parsed: Dict[str, Any]):
        """Handle scan commands."""
        args = parsed.get('args', [])
        
        if not args:
            self.console.print("[red]Error: Target required for scan[/]")
            return
            
        target = args[0]
        scan_type = parsed.get('type', 'quick')
        
        self.console.print(f"[green]Starting {scan_type} scan on target: {target}[/]")
        
        # Initialize orchestrator if not exists
        if not self.orchestrator:
            self.orchestrator = PentestOrchestrator(target=target, profile=scan_type)
            
        # Start scan in background thread
        scan_thread = threading.Thread(
            target=self._run_scan,
            args=(target, scan_type)
        )
        scan_thread.daemon = True
        scan_thread.start()
        
    def _run_scan(self, target: str, scan_type: str):
        """Run scan in background thread."""
        try:
            result = self.orchestrator.run_module('reconnaissance', {'target': target})
            self.console.print(f"[green]Scan completed for {target}[/]")
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            self.console.print(f"[red]Scan failed: {e}[/]")
            
    def handle_exploit_command(self, parsed: Dict[str, Any]):
        """Handle exploitation commands."""
        self.console.print("[yellow]Launching exploitation module...[/]")
        self.launch_module('exploitation', parsed.get('args', []))
        
    def handle_report_command(self, parsed: Dict[str, Any]):
        """Handle report generation commands."""
        format_type = parsed.get('format', 'pdf')
        self.console.print(f"[green]Generating {format_type.upper()} report...[/]")
        self.launch_module('reporting', parsed.get('args', []))
        
    def handle_project_command(self, parsed: Dict[str, Any]):
        """Handle project management commands."""
        action = parsed.get('action', 'list')
        
        if action == 'list':
            self.list_projects()
        elif action == 'new':
            self.create_project(parsed.get('args', []))
        elif action == 'load':
            self.load_project(parsed.get('args', []))
        else:
            self.console.print(f"[red]Unknown project action: {action}[/]")
            
    def handle_config_command(self, parsed: Dict[str, Any]):
        """Handle configuration commands."""
        self.console.print("[blue]Configuration management not yet implemented[/]")
        
    def launch_module(self, module_name: str, args: List[str]):
        """Launch a specific module CLI."""
        try:
            if module_name == 'reconnaissance':
                from .module_cli.recon_cli import ReconCLI
                cli = ReconCLI()
                cli.run(args)
            elif module_name == 'vulnerability':
                from .module_cli.vuln_cli import VulnCLI
                cli = VulnCLI()
                cli.run(args)
            elif module_name == 'exploitation':
                from .module_cli.exploit_cli import ExploitCLI
                cli = ExploitCLI()
                cli.run(args)
            elif module_name == 'post_exploit':
                from .module_cli.post_exploit_cli import PostExploitCLI
                cli = PostExploitCLI()
                cli.run(args)
            elif module_name == 'reporting':
                from .module_cli.report_cli import ReportCLI
                cli = ReportCLI()
                cli.run(args)
            else:
                self.console.print(f"[red]Unknown module: {module_name}[/]")
                
        except ImportError as e:
            self.logger.error(f"Module import failed: {e}")
            self.console.print(f"[red]Module not available: {module_name}[/]")
        except Exception as e:
            self.logger.error(f"Module launch failed: {e}")
            self.console.print(f"[red]Module failed to start: {e}[/]")
            
    def list_projects(self):
        """List all available projects."""
        projects_table = Table(title="Projects", box=box.ROUNDED)
        projects_table.add_column("ID", style="yellow")
        projects_table.add_column("Name", style="green")
        projects_table.add_column("Target", style="cyan")
        projects_table.add_column("Created", style="dim")
        projects_table.add_column("Status", style="bold")
        
        # TODO: Implement project listing from database
        projects_table.add_row("1", "Example Project", "192.168.1.100", "2025-08-16", "[green]Active[/]")
        
        self.console.print(projects_table)
        
    def create_project(self, args: List[str]):
        """Create a new project."""
        if not args:
            project_name = Prompt.ask("[cyan]Enter project name")
        else:
            project_name = " ".join(args)
            
        target = Prompt.ask("[cyan]Enter target (IP/domain)")
        
        self.console.print(f"[green]Created project: {project_name} for target: {target}[/]")
        # TODO: Implement project creation in database
        
    def load_project(self, args: List[str]):
        """Load an existing project."""
        if not args:
            project_id = Prompt.ask("[cyan]Enter project ID")
        else:
            project_id = args[0]
            
        self.console.print(f"[green]Loading project ID: {project_id}[/]")
        # TODO: Implement project loading from database
        
    def shutdown(self):
        """Gracefully shutdown the CLI application."""
        self.running = False
        
        if self.live_dashboard:
            self.live_dashboard.stop()
            
        if self.orchestrator:
            # TODO: Stop any running scans
            pass
            
        self.console.print("[green]Pentest-USB Toolkit CLI shutdown complete.[/]")
        
    def run(self):
        """Main run loop for the CLI application."""
        try:
            # Show startup banner
            self.startup_banner()
            
            # Check for command line arguments
            if len(sys.argv) > 1:
                # Command line mode
                command = " ".join(sys.argv[1:])
                self.execute_command(command)
            else:
                # Interactive mode
                while self.running:
                    self.show_main_menu()
                    
                    choice = Prompt.ask(
                        "\n[bold cyan]Select option[/]",
                        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                        default="0"
                    )
                    
                    if choice == "0":
                        break
                    elif choice == "1":
                        self.launch_module('reconnaissance', [])
                    elif choice == "2":
                        self.launch_module('vulnerability', [])
                    elif choice == "3":
                        self.launch_module('exploitation', [])
                    elif choice == "4":
                        self.launch_module('post_exploit', [])
                    elif choice == "5":
                        self.launch_module('reporting', [])
                    elif choice == "6":
                        self.handle_project_command({'action': 'list'})
                    elif choice == "7":
                        self.handle_config_command({})
                    elif choice == "8":
                        self.show_dashboard()
                    elif choice == "9":
                        self.show_help([])
                        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user.[/]")
        except Exception as e:
            self.logger.error(f"CLI application error: {e}")
            self.console.print(f"[red]Application error: {e}[/]")
        finally:
            self.shutdown()


def main():
    """Main entry point for the CLI application."""
    cli = PentestCLI()
    cli.run()


if __name__ == "__main__":
    main()