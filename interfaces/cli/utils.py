#!/usr/bin/env python3
"""
CLI Utilities for Pentest-USB Toolkit
=====================================

Common utilities for CLI operations including input validation,
output formatting, and system information gathering.
"""

import os
import sys
import re
import ipaddress
import platform
import shutil
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import socket

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax


class CLIUtils:
    """Utility class for common CLI operations."""
    
    def __init__(self):
        """Initialize CLI utilities."""
        self.console = Console()
        
    def get_system_info(self) -> Panel:
        """Get comprehensive system information panel."""
        system_info = Table.grid(padding=1)
        system_info.add_column(style="cyan", justify="right")
        system_info.add_column(style="white")
        
        # Operating system
        system_info.add_row("OS:", f"{platform.system()} {platform.release()}")
        system_info.add_row("Architecture:", platform.machine())
        system_info.add_row("Python Version:", platform.python_version())
        
        # Network information
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            system_info.add_row("Hostname:", hostname)
            system_info.add_row("Local IP:", local_ip)
        except Exception:
            system_info.add_row("Network:", "Unable to detect")
            
        # USB/Portable mode detection
        current_path = Path.cwd()
        if self._is_portable_mode(current_path):
            system_info.add_row("Mode:", "[green]Portable USB[/]")
            system_info.add_row("USB Path:", str(current_path))
        else:
            system_info.add_row("Mode:", "[yellow]Local Installation[/]")
            
        # Disk space
        total, used, free = shutil.disk_usage(current_path)
        system_info.add_row("Disk Free:", self.format_bytes(free))
        
        return Panel(
            system_info,
            title="[bold cyan]System Information[/]",
            border_style="cyan",
            box=box.ROUNDED
        )
        
    def _is_portable_mode(self, path: Path) -> bool:
        """Detect if running in portable USB mode."""
        # Check for typical USB drive characteristics
        usb_indicators = [
            'pentest-usb',
            'portable',
            'usb',
            'removable'
        ]
        
        path_str = str(path).lower()
        return any(indicator in path_str for indicator in usb_indicators)
        
    def validate_ip_address(self, ip_str: str) -> bool:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
            
    def validate_network_range(self, range_str: str) -> bool:
        """Validate network range format (CIDR)."""
        try:
            ipaddress.ip_network(range_str, strict=False)
            return True
        except ValueError:
            return False
            
    def validate_domain(self, domain: str) -> bool:
        """Validate domain name format."""
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_pattern.match(domain)) and len(domain) <= 255
        
    def validate_url(self, url: str) -> bool:
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
        
    def validate_port(self, port: Union[str, int]) -> bool:
        """Validate port number."""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except ValueError:
            return False
            
    def parse_port_range(self, port_range: str) -> List[int]:
        """Parse port range string into list of ports."""
        ports = []
        
        for part in port_range.split(','):
            part = part.strip()
            
            if '-' in part:
                # Range like "80-90"
                try:
                    start, end = map(int, part.split('-', 1))
                    if 1 <= start <= end <= 65535:
                        ports.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                # Single port
                try:
                    port = int(part)
                    if 1 <= port <= 65535:
                        ports.append(port)
                except ValueError:
                    continue
                    
        return sorted(list(set(ports)))  # Remove duplicates and sort
        
    def format_bytes(self, bytes_val: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"
        
    def format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            seconds = seconds % 60
            return f"{minutes}m {seconds:.0f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
            
    def create_progress_bar(self, description: str) -> Progress:
        """Create a rich progress bar with standard styling."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
        
    def prompt_for_target(self) -> str:
        """Interactive prompt for target input with validation."""
        while True:
            target = Prompt.ask(
                "[cyan]Enter target[/] (IP, domain, or network range)"
            ).strip()
            
            if not target:
                self.console.print("[red]Target cannot be empty[/]")
                continue
                
            # Validate target format
            if (self.validate_ip_address(target) or 
                self.validate_domain(target) or 
                self.validate_network_range(target)):
                return target
            else:
                self.console.print("[red]Invalid target format. Use IP, domain, or CIDR notation.[/]")
                
    def prompt_for_ports(self, default: str = "1-1000") -> List[int]:
        """Interactive prompt for port selection with validation."""
        while True:
            port_input = Prompt.ask(
                "[cyan]Enter port range[/] (e.g., 80,443,8000-8080)",
                default=default
            ).strip()
            
            ports = self.parse_port_range(port_input)
            
            if ports:
                if len(ports) > 1000:
                    if not Confirm.ask(f"[yellow]Scanning {len(ports)} ports may take time. Continue?[/]"):
                        continue
                return ports
            else:
                self.console.print("[red]Invalid port format. Use individual ports or ranges.[/]")
                
    def prompt_for_wordlist(self, wordlist_type: str = "passwords") -> Optional[Path]:
        """Interactive prompt for wordlist selection."""
        wordlist_base = Path("data/wordlists") / wordlist_type
        
        if not wordlist_base.exists():
            self.console.print(f"[red]Wordlist directory not found: {wordlist_base}[/]")
            return None
            
        # List available wordlists
        wordlists = list(wordlist_base.glob("*.txt"))
        
        if not wordlists:
            self.console.print(f"[red]No wordlists found in {wordlist_base}[/]")
            return None
            
        # Show available wordlists
        table = Table(title=f"Available {wordlist_type.title()} Wordlists")
        table.add_column("ID", style="yellow")
        table.add_column("Filename", style="green")
        table.add_column("Size", style="cyan")
        
        for i, wordlist in enumerate(wordlists, 1):
            size = self.format_bytes(wordlist.stat().st_size)
            table.add_row(str(i), wordlist.name, size)
            
        self.console.print(table)
        
        # Prompt for selection
        while True:
            try:
                choice = IntPrompt.ask(
                    f"[cyan]Select wordlist[/] (1-{len(wordlists)})",
                    default=1
                )
                
                if 1 <= choice <= len(wordlists):
                    return wordlists[choice - 1]
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {len(wordlists)}[/]")
            except KeyboardInterrupt:
                return None
                
    def display_scan_results(self, results: Dict[str, Any]):
        """Display scan results in formatted tables."""
        if not results:
            self.console.print("[yellow]No results to display[/]")
            return
            
        # Display different result types
        if 'hosts' in results:
            self._display_host_results(results['hosts'])
            
        if 'ports' in results:
            self._display_port_results(results['ports'])
            
        if 'vulnerabilities' in results:
            self._display_vulnerability_results(results['vulnerabilities'])
            
        if 'credentials' in results:
            self._display_credential_results(results['credentials'])
            
    def _display_host_results(self, hosts: List[Dict[str, Any]]):
        """Display host discovery results."""
        table = Table(title="[bold green]Host Discovery Results[/]")
        table.add_column("IP Address", style="cyan")
        table.add_column("Hostname", style="green")
        table.add_column("OS", style="yellow")
        table.add_column("Status", style="white")
        
        for host in hosts:
            table.add_row(
                host.get('ip', 'Unknown'),
                host.get('hostname', 'N/A'),
                host.get('os', 'Unknown'),
                "[green]Up[/]" if host.get('status') == 'up' else "[red]Down[/]"
            )
            
        self.console.print(table)
        
    def _display_port_results(self, ports: List[Dict[str, Any]]):
        """Display port scan results."""
        table = Table(title="[bold green]Open Ports[/]")
        table.add_column("Port", style="yellow")
        table.add_column("Protocol", style="cyan")
        table.add_column("Service", style="green")
        table.add_column("Version", style="white")
        table.add_column("State", style="bold")
        
        for port in ports:
            state_color = "green" if port.get('state') == 'open' else "red"
            table.add_row(
                str(port.get('port', 0)),
                port.get('protocol', 'tcp'),
                port.get('service', 'unknown'),
                port.get('version', 'N/A'),
                f"[{state_color}]{port.get('state', 'unknown')}[/]"
            )
            
        self.console.print(table)
        
    def _display_vulnerability_results(self, vulns: List[Dict[str, Any]]):
        """Display vulnerability scan results."""
        table = Table(title="[bold red]Vulnerabilities Found[/]")
        table.add_column("Severity", style="bold")
        table.add_column("CVE/ID", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Port/Service", style="cyan")
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        sorted_vulns = sorted(vulns, key=lambda x: severity_order.get(x.get('severity', 'info').lower(), 5))
        
        for vuln in sorted_vulns:
            severity = vuln.get('severity', 'info').lower()
            if severity == 'critical':
                severity_style = "[bold red]CRITICAL[/]"
            elif severity == 'high':
                severity_style = "[red]HIGH[/]"
            elif severity == 'medium':
                severity_style = "[yellow]MEDIUM[/]"
            elif severity == 'low':
                severity_style = "[green]LOW[/]"
            else:
                severity_style = "[blue]INFO[/]"
                
            table.add_row(
                severity_style,
                vuln.get('id', 'N/A'),
                vuln.get('description', 'No description'),
                vuln.get('port', 'N/A')
            )
            
        self.console.print(table)
        
    def _display_credential_results(self, creds: List[Dict[str, Any]]):
        """Display discovered credentials."""
        table = Table(title="[bold yellow]Discovered Credentials[/]")
        table.add_column("Username", style="green")
        table.add_column("Password/Hash", style="red")
        table.add_column("Service", style="cyan")
        table.add_column("Source", style="white")
        
        for cred in creds:
            password = cred.get('password', cred.get('hash', 'N/A'))
            if len(password) > 30:
                password = password[:27] + "..."
                
            table.add_row(
                cred.get('username', 'N/A'),
                password,
                cred.get('service', 'Unknown'),
                cred.get('source', 'N/A')
            )
            
        self.console.print(table)
        
    def display_file_content(self, file_path: Path, syntax: str = "text"):
        """Display file content with syntax highlighting."""
        try:
            content = file_path.read_text()
            
            if syntax != "text":
                syntax_obj = Syntax(content, syntax, theme="monokai", line_numbers=True)
                self.console.print(syntax_obj)
            else:
                self.console.print(Panel(content, title=str(file_path)))
                
        except Exception as e:
            self.console.print(f"[red]Error reading file {file_path}: {e}[/]")
            
    def confirm_dangerous_action(self, action: str) -> bool:
        """Confirm dangerous actions with explicit user consent."""
        self.console.print(f"[bold red]WARNING:[/] You are about to {action}")
        self.console.print("[yellow]This action may be irreversible or cause system changes.[/]")
        
        return Confirm.ask("[bold]Are you sure you want to continue?")
        
    def save_results_to_file(self, results: Any, filename: Optional[str] = None) -> Path:
        """Save results to file with automatic naming."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pentest_results_{timestamp}.json"
            
        output_dir = Path("outputs/scans")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        
        import json
        with open(output_file, 'w') as f:
            if isinstance(results, dict) or isinstance(results, list):
                json.dump(results, f, indent=2, default=str)
            else:
                f.write(str(results))
                
        self.console.print(f"[green]Results saved to: {output_file}[/]")
        return output_file


# Example usage and testing
if __name__ == "__main__":
    utils = CLIUtils()
    
    # Test system info
    utils.console.print(utils.get_system_info())
    
    # Test validation functions
    print("IP validation:", utils.validate_ip_address("192.168.1.1"))
    print("Domain validation:", utils.validate_domain("example.com"))
    print("URL validation:", utils.validate_url("https://example.com"))
    
    # Test port parsing
    ports = utils.parse_port_range("80,443,8000-8080")
    print("Parsed ports:", ports)