#!/usr/bin/env python3
"""
Menu System for Pentest-USB Toolkit CLI
=======================================

Hierarchical navigation system with interactive menus,
auto-completion, and context-aware help.
"""

import sys
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import box
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory


@dataclass
class MenuItem:
    """Represents a menu item with action and metadata."""
    key: str
    title: str
    description: str
    action: Optional[Callable] = None
    submenu: Optional['Menu'] = None
    enabled: bool = True
    requires_confirmation: bool = False
    
    
class Menu:
    """Represents a hierarchical menu with items and submenus."""
    
    def __init__(self, title: str, description: str = ""):
        """Initialize menu with title and description."""
        self.title = title
        self.description = description
        self.items: Dict[str, MenuItem] = {}
        self.parent: Optional['Menu'] = None
        
    def add_item(self, item: MenuItem):
        """Add menu item to this menu."""
        self.items[item.key] = item
        if item.submenu:
            item.submenu.parent = self
            
    def add_separator(self):
        """Add a visual separator to the menu."""
        separator_key = f"sep_{len(self.items)}"
        self.items[separator_key] = MenuItem(
            key=separator_key,
            title="─" * 40,
            description="",
            enabled=False
        )
        
    def get_item(self, key: str) -> Optional[MenuItem]:
        """Get menu item by key."""
        return self.items.get(key)
        
    def get_enabled_items(self) -> Dict[str, MenuItem]:
        """Get only enabled menu items."""
        return {k: v for k, v in self.items.items() if v.enabled}
        

class MenuSystem:
    """Main menu system managing navigation and interaction."""
    
    def __init__(self):
        """Initialize the menu system."""
        self.console = Console()
        self.current_menu: Optional[Menu] = None
        self.menu_stack: List[Menu] = []
        self.history = InMemoryHistory()
        
        # Build menu structure
        self._build_menu_structure()
        
    def _build_menu_structure(self):
        """Build the complete menu hierarchy."""
        # Main menu
        self.main_menu = Menu("Main Menu", "Pentest-USB Toolkit Main Menu")
        
        # Reconnaissance submenu
        recon_menu = Menu("Reconnaissance", "Network scanning and information gathering")
        recon_menu.add_item(MenuItem("1", "Network Discovery", "Discover hosts and services", self._network_discovery))
        recon_menu.add_item(MenuItem("2", "Port Scanning", "Scan for open ports and services", self._port_scanning))
        recon_menu.add_item(MenuItem("3", "Domain Enumeration", "Enumerate subdomains and DNS", self._domain_enumeration))
        recon_menu.add_item(MenuItem("4", "OSINT Gathering", "Open source intelligence collection", self._osint_gathering))
        recon_menu.add_item(MenuItem("5", "Cloud Discovery", "Discover cloud assets and services", self._cloud_discovery))
        recon_menu.add_item(MenuItem("6", "Wireless Scanning", "Scan for wireless networks", self._wireless_scanning))
        recon_menu.add_separator()
        recon_menu.add_item(MenuItem("0", "Back to Main Menu", "Return to main menu"))
        
        # Vulnerability Assessment submenu
        vuln_menu = Menu("Vulnerability Assessment", "Security vulnerability scanning")
        vuln_menu.add_item(MenuItem("1", "Web Application Scan", "Scan web applications for vulnerabilities", self._web_vuln_scan))
        vuln_menu.add_item(MenuItem("2", "Network Vulnerability Scan", "Network-based vulnerability assessment", self._network_vuln_scan))
        vuln_menu.add_item(MenuItem("3", "Cloud Security Audit", "Audit cloud configurations", self._cloud_security_audit))
        vuln_menu.add_item(MenuItem("4", "Static Code Analysis", "Analyze source code for vulnerabilities", self._static_code_analysis))
        vuln_menu.add_item(MenuItem("5", "Mobile App Security", "Mobile application security testing", self._mobile_app_security))
        vuln_menu.add_separator()
        vuln_menu.add_item(MenuItem("0", "Back to Main Menu", "Return to main menu"))
        
        # Exploitation submenu
        exploit_menu = Menu("Exploitation", "Execute exploits and gain system access")
        exploit_menu.add_item(MenuItem("1", "Web Exploitation", "Exploit web application vulnerabilities", self._web_exploitation))
        exploit_menu.add_item(MenuItem("2", "Network Exploitation", "Exploit network services", self._network_exploitation))
        exploit_menu.add_item(MenuItem("3", "Binary Exploitation", "Exploit binary vulnerabilities", self._binary_exploitation))
        exploit_menu.add_item(MenuItem("4", "Social Engineering", "Social engineering campaigns", self._social_engineering))
        exploit_menu.add_item(MenuItem("5", "Wireless Attacks", "Attack wireless networks", self._wireless_attacks))
        exploit_menu.add_separator()
        exploit_menu.add_item(MenuItem("0", "Back to Main Menu", "Return to main menu"))
        
        # Post-Exploitation submenu
        postexploit_menu = Menu("Post-Exploitation", "Privilege escalation and persistence")
        postexploit_menu.add_item(MenuItem("1", "Credential Access", "Harvest credentials and secrets", self._credential_access))
        postexploit_menu.add_item(MenuItem("2", "Lateral Movement", "Move laterally through network", self._lateral_movement))
        postexploit_menu.add_item(MenuItem("3", "Persistence", "Establish persistent access", self._persistence))
        postexploit_menu.add_item(MenuItem("4", "Data Exfiltration", "Exfiltrate sensitive data", self._data_exfiltration))
        postexploit_menu.add_item(MenuItem("5", "Evidence Cleanup", "Clean up attack traces", self._evidence_cleanup))
        postexploit_menu.add_separator()
        postexploit_menu.add_item(MenuItem("0", "Back to Main Menu", "Return to main menu"))
        
        # Reporting submenu
        reporting_menu = Menu("Reporting", "Generate comprehensive security reports")
        reporting_menu.add_item(MenuItem("1", "Executive Summary", "Generate executive summary report", self._executive_summary))
        reporting_menu.add_item(MenuItem("2", "Technical Report", "Generate detailed technical report", self._technical_report))
        reporting_menu.add_item(MenuItem("3", "Vulnerability Report", "Generate vulnerability-focused report", self._vulnerability_report))
        reporting_menu.add_item(MenuItem("4", "Compliance Report", "Generate compliance assessment report", self._compliance_report))
        reporting_menu.add_item(MenuItem("5", "Custom Report", "Create custom report template", self._custom_report))
        reporting_menu.add_separator()
        reporting_menu.add_item(MenuItem("0", "Back to Main Menu", "Return to main menu"))
        
        # Configuration submenu
        config_menu = Menu("Configuration", "System configuration and preferences")
        config_menu.add_item(MenuItem("1", "Tool Configuration", "Configure integrated tools", self._tool_configuration))
        config_menu.add_item(MenuItem("2", "Scan Profiles", "Manage scan profiles", self._scan_profiles))
        config_menu.add_item(MenuItem("3", "Report Templates", "Manage report templates", self._report_templates))
        config_menu.add_item(MenuItem("4", "API Keys", "Configure API keys and credentials", self._api_keys))
        config_menu.add_item(MenuItem("5", "User Preferences", "Set user preferences", self._user_preferences))
        config_menu.add_separator()
        config_menu.add_item(MenuItem("0", "Back to Main Menu", "Return to main menu"))
        
        # Add main menu items with submenus
        self.main_menu.add_item(MenuItem("1", "Reconnaissance", "Network scanning and OSINT", submenu=recon_menu))
        self.main_menu.add_item(MenuItem("2", "Vulnerability Assessment", "Scan for security vulnerabilities", submenu=vuln_menu))
        self.main_menu.add_item(MenuItem("3", "Exploitation", "Execute exploits and gain access", submenu=exploit_menu))
        self.main_menu.add_item(MenuItem("4", "Post-Exploitation", "Privilege escalation and persistence", submenu=postexploit_menu))
        self.main_menu.add_item(MenuItem("5", "Reporting", "Generate comprehensive reports", submenu=reporting_menu))
        self.main_menu.add_separator()
        self.main_menu.add_item(MenuItem("6", "Configuration", "Tool settings and preferences", submenu=config_menu))
        self.main_menu.add_item(MenuItem("7", "Project Management", "Manage scan projects", self._project_management))
        self.main_menu.add_item(MenuItem("8", "Help & Documentation", "View help and docs", self._help_documentation))
        self.main_menu.add_separator()
        self.main_menu.add_item(MenuItem("0", "Exit", "Exit the application", requires_confirmation=True))
        
        # Set current menu to main menu
        self.current_menu = self.main_menu
        
    def display_menu(self, menu: Optional[Menu] = None) -> None:
        """Display the current or specified menu."""
        if menu is None:
            menu = self.current_menu
            
        if not menu:
            return
            
        # Create menu table
        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 2))
        table.add_column("Key", style="bold yellow", width=6)
        table.add_column("Option", style="bold green")
        table.add_column("Description", style="dim white")
        
        # Add menu items
        for key, item in menu.items.items():
            if not item.enabled and "sep_" not in key:
                continue
                
            if "sep_" in key:
                table.add_row("", item.title, "")
            else:
                table.add_row(f"[{key}]", item.title, item.description)
                
        # Create panel with menu
        panel = Panel(
            table,
            title=f"[bold cyan]{menu.title}[/]",
            subtitle=f"[dim]{menu.description}[/]" if menu.description else None,
            border_style="cyan"
        )
        
        self.console.print(panel)
        
    def navigate(self, choice: str) -> bool:
        """Navigate menu based on user choice. Returns False if should exit."""
        if not self.current_menu:
            return False
            
        # Handle back navigation
        if choice == "0" and self.current_menu != self.main_menu:
            self.go_back()
            return True
        elif choice == "0" and self.current_menu == self.main_menu:
            return False  # Exit application
            
        item = self.current_menu.get_item(choice)
        
        if not item:
            self.console.print(f"[red]Invalid choice: {choice}[/]")
            return True
            
        if not item.enabled:
            self.console.print(f"[yellow]Option not available: {item.title}[/]")
            return True
            
        # Handle confirmation requirement
        if item.requires_confirmation:
            from rich.prompt import Confirm
            if not Confirm.ask(f"[yellow]Confirm: {item.title}?[/]"):
                return True
                
        # Execute action or navigate to submenu
        if item.submenu:
            self.menu_stack.append(self.current_menu)
            self.current_menu = item.submenu
        elif item.action:
            try:
                item.action()
            except Exception as e:
                self.console.print(f"[red]Error executing {item.title}: {e}[/]")
        else:
            self.console.print(f"[yellow]Action not implemented: {item.title}[/]")
            
        return True
        
    def go_back(self) -> None:
        """Go back to previous menu."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
        else:
            self.current_menu = self.main_menu
            
    def get_current_path(self) -> str:
        """Get current menu path as breadcrumb string."""
        path = []
        
        # Build path from stack
        for menu in self.menu_stack + [self.current_menu]:
            if menu:
                path.append(menu.title)
                
        return " > ".join(path)
        
    def get_completion_choices(self) -> List[str]:
        """Get available choices for auto-completion."""
        if not self.current_menu:
            return []
            
        choices = []
        for key, item in self.current_menu.get_enabled_items().items():
            if "sep_" not in key:
                choices.append(key)
                choices.append(item.title.lower())
                
        return choices
        
    def prompt_with_completion(self, prompt_text: str) -> str:
        """Prompt user with auto-completion support."""
        choices = self.get_completion_choices()
        completer = WordCompleter(choices, ignore_case=True)
        
        try:
            return prompt(
                prompt_text,
                completer=completer,
                history=self.history,
                complete_style='column'
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return ""
            
    # Menu action implementations (placeholder functions)
    def _network_discovery(self):
        """Launch network discovery module."""
        self.console.print("[green]Launching Network Discovery...[/]")
        # TODO: Integrate with reconnaissance module
        
    def _port_scanning(self):
        """Launch port scanning module."""
        self.console.print("[green]Launching Port Scanner...[/]")
        # TODO: Integrate with reconnaissance module
        
    def _domain_enumeration(self):
        """Launch domain enumeration module."""
        self.console.print("[green]Launching Domain Enumeration...[/]")
        # TODO: Integrate with reconnaissance module
        
    def _osint_gathering(self):
        """Launch OSINT gathering module."""
        self.console.print("[green]Launching OSINT Gathering...[/]")
        # TODO: Integrate with reconnaissance module
        
    def _cloud_discovery(self):
        """Launch cloud discovery module."""
        self.console.print("[green]Launching Cloud Discovery...[/]")
        # TODO: Integrate with reconnaissance module
        
    def _wireless_scanning(self):
        """Launch wireless scanning module."""
        self.console.print("[green]Launching Wireless Scanner...[/]")
        # TODO: Integrate with reconnaissance module
        
    def _web_vuln_scan(self):
        """Launch web vulnerability scanner."""
        self.console.print("[green]Launching Web Vulnerability Scanner...[/]")
        # TODO: Integrate with vulnerability module
        
    def _network_vuln_scan(self):
        """Launch network vulnerability scanner."""
        self.console.print("[green]Launching Network Vulnerability Scanner...[/]")
        # TODO: Integrate with vulnerability module
        
    def _cloud_security_audit(self):
        """Launch cloud security audit."""
        self.console.print("[green]Launching Cloud Security Audit...[/]")
        # TODO: Integrate with vulnerability module
        
    def _static_code_analysis(self):
        """Launch static code analysis."""
        self.console.print("[green]Launching Static Code Analysis...[/]")
        # TODO: Integrate with vulnerability module
        
    def _mobile_app_security(self):
        """Launch mobile app security testing."""
        self.console.print("[green]Launching Mobile App Security Testing...[/]")
        # TODO: Integrate with vulnerability module
        
    def _web_exploitation(self):
        """Launch web exploitation module."""
        self.console.print("[green]Launching Web Exploitation...[/]")
        # TODO: Integrate with exploitation module
        
    def _network_exploitation(self):
        """Launch network exploitation module."""
        self.console.print("[green]Launching Network Exploitation...[/]")
        # TODO: Integrate with exploitation module
        
    def _binary_exploitation(self):
        """Launch binary exploitation module."""
        self.console.print("[green]Launching Binary Exploitation...[/]")
        # TODO: Integrate with exploitation module
        
    def _social_engineering(self):
        """Launch social engineering campaigns."""
        self.console.print("[green]Launching Social Engineering...[/]")
        # TODO: Integrate with exploitation module
        
    def _wireless_attacks(self):
        """Launch wireless attacks module."""
        self.console.print("[green]Launching Wireless Attacks...[/]")
        # TODO: Integrate with exploitation module
        
    def _credential_access(self):
        """Launch credential access module."""
        self.console.print("[green]Launching Credential Access...[/]")
        # TODO: Integrate with post-exploitation module
        
    def _lateral_movement(self):
        """Launch lateral movement module."""
        self.console.print("[green]Launching Lateral Movement...[/]")
        # TODO: Integrate with post-exploitation module
        
    def _persistence(self):
        """Launch persistence module."""
        self.console.print("[green]Launching Persistence...[/]")
        # TODO: Integrate with post-exploitation module
        
    def _data_exfiltration(self):
        """Launch data exfiltration module."""
        self.console.print("[green]Launching Data Exfiltration...[/]")
        # TODO: Integrate with post-exploitation module
        
    def _evidence_cleanup(self):
        """Launch evidence cleanup module."""
        self.console.print("[green]Launching Evidence Cleanup...[/]")
        # TODO: Integrate with post-exploitation module
        
    def _executive_summary(self):
        """Generate executive summary report."""
        self.console.print("[green]Generating Executive Summary...[/]")
        # TODO: Integrate with reporting module
        
    def _technical_report(self):
        """Generate technical report."""
        self.console.print("[green]Generating Technical Report...[/]")
        # TODO: Integrate with reporting module
        
    def _vulnerability_report(self):
        """Generate vulnerability report."""
        self.console.print("[green]Generating Vulnerability Report...[/]")
        # TODO: Integrate with reporting module
        
    def _compliance_report(self):
        """Generate compliance report."""
        self.console.print("[green]Generating Compliance Report...[/]")
        # TODO: Integrate with reporting module
        
    def _custom_report(self):
        """Generate custom report."""
        self.console.print("[green]Creating Custom Report...[/]")
        # TODO: Integrate with reporting module
        
    def _tool_configuration(self):
        """Configure integrated tools."""
        self.console.print("[blue]Tool Configuration not yet implemented[/]")
        
    def _scan_profiles(self):
        """Manage scan profiles."""
        self.console.print("[blue]Scan Profiles management not yet implemented[/]")
        
    def _report_templates(self):
        """Manage report templates."""
        self.console.print("[blue]Report Templates management not yet implemented[/]")
        
    def _api_keys(self):
        """Configure API keys."""
        self.console.print("[blue]API Keys configuration not yet implemented[/]")
        
    def _user_preferences(self):
        """Set user preferences."""
        self.console.print("[blue]User Preferences not yet implemented[/]")
        
    def _project_management(self):
        """Launch project management."""
        self.console.print("[blue]Project Management not yet implemented[/]")
        
    def _help_documentation(self):
        """Show help and documentation."""
        help_text = """
[bold cyan]Pentest-USB Toolkit Help[/]

[bold yellow]Navigation:[/]
- Enter the number corresponding to your choice
- Type '0' or 'back' to go back
- Type 'exit' or 'quit' to exit the application

[bold yellow]Commands:[/]
- Use Tab for auto-completion
- Use arrow keys to navigate history
- Ctrl+C to interrupt current operation

[bold yellow]Modules:[/]
- Reconnaissance: Network scanning and information gathering
- Vulnerability Assessment: Security vulnerability scanning  
- Exploitation: Execute exploits and gain access
- Post-Exploitation: Privilege escalation and persistence
- Reporting: Generate comprehensive security reports

[bold yellow]Support:[/]
- Documentation: docs/ directory
- GitHub: https://github.com/LeZelote01/LeZelote-Toolkit
"""
        self.console.print(Panel(help_text, title="Help & Documentation", border_style="blue"))


# Example usage
if __name__ == "__main__":
    menu_system = MenuSystem()
    
    try:
        while True:
            # Clear screen and show current path
            console = Console()
            console.clear()
            console.print(f"[dim]Path: {menu_system.get_current_path()}[/]\n")
            
            # Display current menu
            menu_system.display_menu()
            
            # Get user input with completion
            choice = menu_system.prompt_with_completion("\n[bold cyan]Choose option[/]: ")
            
            if not choice:
                continue
                
            # Handle navigation
            if not menu_system.navigate(choice):
                break
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/]")