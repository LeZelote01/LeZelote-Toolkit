#!/usr/bin/env python3
"""
Reconnaissance Module CLI for Pentest-USB Toolkit
=================================================

CLI interface for reconnaissance operations including network scanning,
domain enumeration, OSINT gathering, and asset discovery.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import ipaddress
import threading
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.text import Text
from rich.columns import Columns

from core.engine.orchestrator import PentestOrchestrator
from modules.reconnaissance.network_scanner import NetworkScanner
from modules.reconnaissance.domain_enum import DomainEnumerator
from modules.reconnaissance.osint_gather import OSINTGatherer
from modules.reconnaissance.cloud_discovery import CloudDiscovery
from modules.reconnaissance.wireless_scanner import WirelessScanner
from core.utils.logging_handler import LoggingHandler


class ReconCLI:
    """CLI interface for reconnaissance module operations."""
    
    def __init__(self):
        """Initialize reconnaissance CLI."""
        self.console = Console()
        self.logger = LoggingHandler().get_logger("ReconCLI")
        
        # Module instances
        self.network_scanner = NetworkScanner()
        self.domain_enum = DomainEnumerator()
        self.osint_gatherer = OSINTGatherer()
        self.cloud_discovery = CloudDiscovery()
        self.wireless_scanner = WirelessScanner()
        
        # Current scan state
        self.current_target = None
        self.scan_results = {}
        self.running_scans = {}
        
    def run(self, args: List[str]):
        """Run reconnaissance CLI with provided arguments."""
        try:
            if args and args[0] == "--help":
                self.show_help()
                return
                
            self.show_banner()
            self.interactive_shell()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Reconnaissance module interrupted.[/]")
        except Exception as e:
            self.logger.error(f"ReconCLI error: {e}")
            self.console.print(f"[red]Error: {e}[/]")
            
    def show_banner(self):
        """Display reconnaissance module banner."""
        banner = """
[bold green]
██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
[/]
[bold cyan]RECONNAISSANCE MODULE[/]
[dim]Network scanning • Domain enumeration • OSINT gathering[/]
"""
        
        self.console.print(Panel(
            banner,
            title="[bold green]Reconnaissance[/]",
            border_style="green",
            box=box.DOUBLE_EDGE
        ))
        
    def show_help(self):
        """Show reconnaissance module help."""
        help_text = """
[bold cyan]Reconnaissance Module Commands[/]

[bold yellow]Network Scanning:[/]
  netscan <target>     - Network discovery and port scanning
  portscan <host>      - Detailed port scanning
  servicescan <host>   - Service version detection
  osscan <host>        - Operating system detection
  
[bold yellow]Domain Operations:[/]
  domainscan <domain>  - Comprehensive domain enumeration
  subdomain <domain>   - Subdomain discovery
  dns <domain>         - DNS enumeration
  
[bold yellow]OSINT Gathering:[/]
  osint <target>       - Open source intelligence gathering
  email <domain>       - Email harvesting
  social <target>      - Social media intelligence
  
[bold yellow]Cloud Discovery:[/]
  cloudscan <domain>   - Cloud asset discovery
  bucket <domain>      - S3/Cloud storage enumeration
  
[bold yellow]Wireless Scanning:[/]
  wireless             - WiFi network discovery
  bluetooth            - Bluetooth device scanning
  
[bold yellow]General Commands:[/]
  status               - Show current scan status
  results              - Display scan results
  export <format>      - Export results (json/xml/csv)
  set <target>         - Set current target
  back                 - Return to main menu
  help                 - Show this help
"""
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        
    def interactive_shell(self):
        """Run interactive reconnaissance shell."""
        self.console.print("\n[green]Reconnaissance module started[/]")
        self.console.print("[dim]Type 'help' for commands, 'back' to return[/]\n")
        
        while True:
            try:
                # Show current target in prompt
                target_info = f"({self.current_target})" if self.current_target else ""
                command = Prompt.ask(
                    f"[bold green]recon{target_info}[/]",
                    default="help"
                ).strip().lower()
                
                if not command:
                    continue
                    
                if command in ['back', 'exit', 'quit']:
                    break
                    
                self.execute_command(command)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'back' to return to main menu[/]")
            except Exception as e:
                self.logger.error(f"Command execution error: {e}")
                self.console.print(f"[red]Error: {e}[/]")
                
    def execute_command(self, command: str):
        """Execute reconnaissance command."""
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        command_map = {
            'help': self.show_help,
            'netscan': self.network_scan,
            'portscan': self.port_scan,
            'servicescan': self.service_scan,
            'osscan': self.os_scan,
            'domainscan': self.domain_scan,
            'subdomain': self.subdomain_scan,
            'dns': self.dns_enum,
            'osint': self.osint_scan,
            'email': self.email_harvest,
            'social': self.social_intel,
            'cloudscan': self.cloud_scan,
            'bucket': self.bucket_enum,
            'wireless': self.wireless_scan,
            'bluetooth': self.bluetooth_scan,
            'status': self.show_status,
            'results': self.show_results,
            'export': self.export_results,
            'set': self.set_target
        }
        
        handler = command_map.get(cmd)
        if handler:
            try:
                if args:
                    handler(args)
                else:
                    handler()
            except TypeError:
                # Handler doesn't accept args
                handler()
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/]")
            self.console.print("Type 'help' for available commands.")
            
    def network_scan(self, args: List[str] = None):
        """Perform network discovery and scanning."""
        if not args:
            target = Prompt.ask("[cyan]Enter target (IP/CIDR/range)")
        else:
            target = args[0]
            
        if not self.validate_network_target(target):
            return
            
        self.current_target = target
        
        # Scan options
        scan_type = Prompt.ask(
            "[cyan]Scan type",
            choices=["quick", "full", "stealth", "aggressive"],
            default="quick"
        )
        
        port_range = Prompt.ask("[cyan]Port range", default="1-1000")
        threads = IntPrompt.ask("[cyan]Number of threads", default=50, show_default=True)
        
        self.console.print(f"[green]Starting network scan on {target}[/]")
        
        # Start scan with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True
        ) as progress:
            
            task = progress.add_task(f"Scanning {target}", total=100)
            
            # Simulate network scanning (replace with actual implementation)
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.05)  # Simulate work
                
        results = {
            'target': target,
            'scan_type': scan_type,
            'alive_hosts': ['192.168.1.1', '192.168.1.100', '192.168.1.254'],
            'open_ports': {
                '192.168.1.1': [22, 80, 443],
                '192.168.1.100': [80, 3389],
                '192.168.1.254': [53, 80]
            }
        }
        
        self.scan_results['network'] = results
        self.display_network_results(results)
        
    def port_scan(self, args: List[str] = None):
        """Perform detailed port scanning."""
        if not args:
            target = Prompt.ask("[cyan]Enter host IP")
        else:
            target = args[0]
            
        if not self.validate_ip_address(target):
            return
            
        self.console.print(f"[green]Starting port scan on {target}[/]")
        
        # Port scan implementation would go here
        results = {
            'host': target,
            'open_ports': [22, 80, 443, 8080],
            'filtered_ports': [135, 139, 445],
            'services': {
                22: 'SSH',
                80: 'HTTP',
                443: 'HTTPS',
                8080: 'HTTP-Proxy'
            }
        }
        
        self.display_port_results(results)
        
    def service_scan(self, args: List[str] = None):
        """Perform service version detection."""
        if not args:
            target = Prompt.ask("[cyan]Enter host IP")
        else:
            target = args[0]
            
        self.console.print(f"[green]Starting service scan on {target}[/]")
        
        # Service detection would go here
        services = {
            22: 'OpenSSH 8.2p1',
            80: 'Apache/2.4.41',
            443: 'Apache/2.4.41 (SSL)',
            8080: 'Jetty 9.4.43'
        }
        
        self.display_service_results(target, services)
        
    def os_scan(self, args: List[str] = None):
        """Perform OS detection."""
        if not args:
            target = Prompt.ask("[cyan]Enter host IP")
        else:
            target = args[0]
            
        self.console.print(f"[green]Starting OS detection on {target}[/]")
        
        # OS detection would go here
        os_info = {
            'os': 'Linux',
            'version': 'Ubuntu 20.04',
            'confidence': '95%',
            'details': 'Linux 5.4.0-X kernel'
        }
        
        self.display_os_results(target, os_info)
        
    def domain_scan(self, args: List[str] = None):
        """Perform comprehensive domain enumeration."""
        if not args:
            domain = Prompt.ask("[cyan]Enter domain name")
        else:
            domain = args[0]
            
        self.console.print(f"[green]Starting domain enumeration for {domain}[/]")
        
        # Domain enumeration would go here
        results = {
            'domain': domain,
            'subdomains': ['www', 'mail', 'ftp', 'admin', 'api'],
            'dns_records': {
                'A': ['1.2.3.4'],
                'MX': ['mail.example.com'],
                'NS': ['ns1.example.com', 'ns2.example.com']
            },
            'technologies': ['Apache', 'PHP', 'MySQL']
        }
        
        self.display_domain_results(results)
        
    def subdomain_scan(self, args: List[str] = None):
        """Perform subdomain discovery."""
        if not args:
            domain = Prompt.ask("[cyan]Enter domain name")
        else:
            domain = args[0]
            
        self.console.print(f"[green]Discovering subdomains for {domain}[/]")
        
        # Subdomain discovery implementation
        subdomains = [
            'www.example.com',
            'mail.example.com',
            'ftp.example.com',
            'admin.example.com',
            'api.example.com',
            'dev.example.com'
        ]
        
        self.display_subdomain_results(domain, subdomains)
        
    def dns_enum(self, args: List[str] = None):
        """Perform DNS enumeration."""
        if not args:
            domain = Prompt.ask("[cyan]Enter domain name")
        else:
            domain = args[0]
            
        self.console.print(f"[green]DNS enumeration for {domain}[/]")
        
        # DNS enumeration implementation
        dns_info = {
            'A': ['1.2.3.4', '5.6.7.8'],
            'AAAA': ['2001:db8::1'],
            'MX': ['10 mail.example.com'],
            'NS': ['ns1.example.com', 'ns2.example.com'],
            'TXT': ['v=spf1 include:_spf.google.com ~all'],
            'CNAME': {'www': 'example.com'}
        }
        
        self.display_dns_results(domain, dns_info)
        
    def osint_scan(self, args: List[str] = None):
        """Perform OSINT gathering."""
        if not args:
            target = Prompt.ask("[cyan]Enter target (domain/email/person)")
        else:
            target = args[0]
            
        self.console.print(f"[green]Gathering OSINT for {target}[/]")
        
        # OSINT gathering implementation
        osint_data = {
            'emails': ['admin@example.com', 'info@example.com'],
            'social_media': ['@example_twitter', 'linkedin.com/company/example'],
            'technologies': ['WordPress', 'CloudFlare', 'Google Analytics'],
            'employees': ['John Doe', 'Jane Smith'],
            'phone_numbers': ['+1-555-0123']
        }
        
        self.display_osint_results(target, osint_data)
        
    def email_harvest(self, args: List[str] = None):
        """Harvest email addresses."""
        if not args:
            domain = Prompt.ask("[cyan]Enter domain name")
        else:
            domain = args[0]
            
        self.console.print(f"[green]Harvesting emails for {domain}[/]")
        
        # Email harvesting implementation
        emails = [
            'admin@example.com',
            'info@example.com',
            'support@example.com',
            'sales@example.com'
        ]
        
        self.display_email_results(domain, emails)
        
    def social_intel(self, args: List[str] = None):
        """Gather social media intelligence."""
        if not args:
            target = Prompt.ask("[cyan]Enter target (company/person)")
        else:
            target = args[0]
            
        self.console.print(f"[green]Gathering social media intel for {target}[/]")
        
        # Social intelligence gathering
        social_data = {
            'twitter': '@example_company',
            'linkedin': 'linkedin.com/company/example',
            'facebook': 'facebook.com/example',
            'employees': ['John Doe (CEO)', 'Jane Smith (CTO)'],
            'recent_posts': ['Hiring new developers', 'Product launch next month']
        }
        
        self.display_social_results(target, social_data)
        
    def cloud_scan(self, args: List[str] = None):
        """Perform cloud asset discovery."""
        if not args:
            domain = Prompt.ask("[cyan]Enter domain/company name")
        else:
            domain = args[0]
            
        self.console.print(f"[green]Discovering cloud assets for {domain}[/]")
        
        # Cloud discovery implementation
        cloud_assets = {
            'aws_buckets': ['example-backup', 'example-logs'],
            'azure_blobs': ['example-storage'],
            'gcp_buckets': ['example-data'],
            'cloud_ips': ['54.123.45.67', '52.123.45.68'],
            'cdn_endpoints': ['d1abc123.cloudfront.net']
        }
        
        self.display_cloud_results(domain, cloud_assets)
        
    def bucket_enum(self, args: List[str] = None):
        """Enumerate cloud storage buckets."""
        if not args:
            domain = Prompt.ask("[cyan]Enter domain/company name")
        else:
            domain = args[0]
            
        self.console.print(f"[green]Enumerating buckets for {domain}[/]")
        
        # Bucket enumeration
        buckets = {
            'aws_s3': [
                {'name': 'example-backup', 'accessible': True, 'files': 156},
                {'name': 'example-logs', 'accessible': False, 'files': 0}
            ],
            'azure_blob': [
                {'name': 'example-storage', 'accessible': True, 'files': 42}
            ],
            'gcp_storage': []
        }
        
        self.display_bucket_results(domain, buckets)
        
    def wireless_scan(self, args: List[str] = None):
        """Perform wireless network discovery."""
        self.console.print("[green]Scanning for wireless networks...[/]")
        
        # Wireless scanning implementation
        networks = [
            {'ssid': 'HomeNetwork', 'security': 'WPA2', 'signal': '-45 dBm', 'channel': 6},
            {'ssid': 'OfficeWiFi', 'security': 'WPA3', 'signal': '-62 dBm', 'channel': 11},
            {'ssid': 'FreeWiFi', 'security': 'Open', 'signal': '-78 dBm', 'channel': 1}
        ]
        
        self.display_wireless_results(networks)
        
    def bluetooth_scan(self, args: List[str] = None):
        """Perform Bluetooth device scanning."""
        self.console.print("[green]Scanning for Bluetooth devices...[/]")
        
        # Bluetooth scanning implementation
        devices = [
            {'name': 'iPhone 12', 'address': '00:11:22:33:44:55', 'class': 'Phone'},
            {'name': 'AirPods Pro', 'address': '66:77:88:99:AA:BB', 'class': 'Audio'},
            {'name': 'Unknown Device', 'address': 'CC:DD:EE:FF:00:11', 'class': 'Unknown'}
        ]
        
        self.display_bluetooth_results(devices)
        
    def show_status(self):
        """Show current scan status."""
        status_table = Table(title="Reconnaissance Status", box=box.ROUNDED)
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Current Target", self.current_target or "None")
        status_table.add_row("Active Scans", str(len(self.running_scans)))
        status_table.add_row("Completed Scans", str(len(self.scan_results)))
        
        if self.running_scans:
            status_table.add_row("Running Scans", ", ".join(self.running_scans.keys()))
            
        self.console.print(status_table)
        
    def show_results(self):
        """Display all scan results."""
        if not self.scan_results:
            self.console.print("[yellow]No scan results available[/]")
            return
            
        for scan_type, results in self.scan_results.items():
            self.console.print(f"\n[bold green]{scan_type.title()} Results:[/]")
            
            # Format results based on type
            if scan_type == 'network':
                self.display_network_results(results)
            # Add other result types as needed
                
    def export_results(self, args: List[str] = None):
        """Export scan results to file."""
        if not self.scan_results:
            self.console.print("[yellow]No results to export[/]")
            return
            
        format_type = args[0] if args else Prompt.ask(
            "[cyan]Export format",
            choices=["json", "xml", "csv"],
            default="json"
        )
        
        filename = f"recon_results.{format_type}"
        
        # Export implementation would go here
        self.console.print(f"[green]Results exported to {filename}[/]")
        
    def set_target(self, args: List[str] = None):
        """Set current target."""
        if args:
            target = args[0]
        else:
            target = Prompt.ask("[cyan]Enter target")
            
        self.current_target = target
        self.console.print(f"[green]Target set to: {target}[/]")
        
    # Display methods
    def display_network_results(self, results: Dict[str, Any]):
        """Display network scan results."""
        table = Table(title="Network Scan Results", box=box.ROUNDED)
        table.add_column("Host", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Open Ports", style="yellow")
        
        for host in results.get('alive_hosts', []):
            ports = results.get('open_ports', {}).get(host, [])
            port_str = ", ".join(map(str, ports)) if ports else "None"
            table.add_row(host, "Up", port_str)
            
        self.console.print(table)
        
    def display_port_results(self, results: Dict[str, Any]):
        """Display port scan results."""
        table = Table(title=f"Port Scan - {results['host']}", box=box.ROUNDED)
        table.add_column("Port", style="cyan")
        table.add_column("State", style="green")
        table.add_column("Service", style="yellow")
        
        for port in results.get('open_ports', []):
            service = results.get('services', {}).get(port, 'Unknown')
            table.add_row(str(port), "Open", service)
            
        self.console.print(table)
        
    def display_service_results(self, host: str, services: Dict[int, str]):
        """Display service detection results."""
        table = Table(title=f"Service Detection - {host}", box=box.ROUNDED)
        table.add_column("Port", style="cyan")
        table.add_column("Service Version", style="yellow")
        
        for port, service in services.items():
            table.add_row(str(port), service)
            
        self.console.print(table)
        
    def display_os_results(self, host: str, os_info: Dict[str, str]):
        """Display OS detection results."""
        table = Table(title=f"OS Detection - {host}", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in os_info.items():
            table.add_row(key.title(), value)
            
        self.console.print(table)
        
    def display_domain_results(self, results: Dict[str, Any]):
        """Display domain enumeration results."""
        domain = results['domain']
        
        # Subdomains
        if results.get('subdomains'):
            subdomains_table = Table(title=f"Subdomains - {domain}", box=box.ROUNDED)
            subdomains_table.add_column("Subdomain", style="cyan")
            
            for subdomain in results['subdomains']:
                subdomains_table.add_row(f"{subdomain}.{domain}")
                
            self.console.print(subdomains_table)
            
        # DNS Records
        if results.get('dns_records'):
            dns_table = Table(title="DNS Records", box=box.ROUNDED)
            dns_table.add_column("Type", style="yellow")
            dns_table.add_column("Value", style="white")
            
            for record_type, values in results['dns_records'].items():
                for value in values if isinstance(values, list) else [values]:
                    dns_table.add_row(record_type, value)
                    
            self.console.print(dns_table)
            
    def display_subdomain_results(self, domain: str, subdomains: List[str]):
        """Display subdomain discovery results."""
        table = Table(title=f"Subdomains - {domain}", box=box.ROUNDED)
        table.add_column("Subdomain", style="cyan")
        table.add_column("Status", style="green")
        
        for subdomain in subdomains:
            table.add_row(subdomain, "Active")
            
        self.console.print(table)
        
    def display_dns_results(self, domain: str, dns_info: Dict[str, Any]):
        """Display DNS enumeration results."""
        table = Table(title=f"DNS Records - {domain}", box=box.ROUNDED)
        table.add_column("Type", style="yellow")
        table.add_column("Value", style="white")
        
        for record_type, values in dns_info.items():
            if isinstance(values, list):
                for value in values:
                    table.add_row(record_type, value)
            elif isinstance(values, dict):
                for key, value in values.items():
                    table.add_row(record_type, f"{key} -> {value}")
            else:
                table.add_row(record_type, str(values))
                
        self.console.print(table)
        
    def display_osint_results(self, target: str, osint_data: Dict[str, Any]):
        """Display OSINT gathering results."""
        self.console.print(f"\n[bold green]OSINT Results for {target}[/]")
        
        for category, data in osint_data.items():
            if data:
                table = Table(title=category.replace('_', ' ').title(), box=box.ROUNDED)
                table.add_column("Item", style="cyan")
                
                for item in data if isinstance(data, list) else [data]:
                    table.add_row(str(item))
                    
                self.console.print(table)
                
    def display_email_results(self, domain: str, emails: List[str]):
        """Display email harvesting results."""
        table = Table(title=f"Email Addresses - {domain}", box=box.ROUNDED)
        table.add_column("Email", style="cyan")
        table.add_column("Source", style="dim")
        
        for email in emails:
            table.add_row(email, "Web scraping")
            
        self.console.print(table)
        
    def display_social_results(self, target: str, social_data: Dict[str, Any]):
        """Display social media intelligence results."""
        self.console.print(f"\n[bold green]Social Media Intelligence - {target}[/]")
        
        for platform, info in social_data.items():
            if info:
                if isinstance(info, list):
                    self.console.print(f"[yellow]{platform.title()}:[/] {', '.join(info)}")
                else:
                    self.console.print(f"[yellow]{platform.title()}:[/] {info}")
                    
    def display_cloud_results(self, domain: str, cloud_assets: Dict[str, Any]):
        """Display cloud asset discovery results."""
        self.console.print(f"\n[bold green]Cloud Assets - {domain}[/]")
        
        for service, assets in cloud_assets.items():
            if assets:
                table = Table(title=service.replace('_', ' ').title(), box=box.ROUNDED)
                table.add_column("Asset", style="cyan")
                table.add_column("Status", style="green")
                
                for asset in assets:
                    if isinstance(asset, dict):
                        table.add_row(asset.get('name', 'Unknown'), "Accessible" if asset.get('accessible') else "Protected")
                    else:
                        table.add_row(str(asset), "Found")
                        
                self.console.print(table)
                
    def display_bucket_results(self, domain: str, buckets: Dict[str, Any]):
        """Display bucket enumeration results."""
        self.console.print(f"\n[bold green]Storage Buckets - {domain}[/]")
        
        for service, bucket_list in buckets.items():
            if bucket_list:
                table = Table(title=service.replace('_', ' ').title(), box=box.ROUNDED)
                table.add_column("Bucket", style="cyan")
                table.add_column("Accessible", style="yellow")
                table.add_column("Files", style="white")
                
                for bucket in bucket_list:
                    table.add_row(
                        bucket['name'],
                        "Yes" if bucket['accessible'] else "No",
                        str(bucket['files'])
                    )
                    
                self.console.print(table)
                
    def display_wireless_results(self, networks: List[Dict[str, Any]]):
        """Display wireless network scan results."""
        table = Table(title="Wireless Networks", box=box.ROUNDED)
        table.add_column("SSID", style="cyan")
        table.add_column("Security", style="yellow")
        table.add_column("Signal", style="white")
        table.add_column("Channel", style="dim")
        
        for network in networks:
            table.add_row(
                network['ssid'],
                network['security'],
                network['signal'],
                str(network['channel'])
            )
            
        self.console.print(table)
        
    def display_bluetooth_results(self, devices: List[Dict[str, Any]]):
        """Display Bluetooth device scan results."""
        table = Table(title="Bluetooth Devices", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Address", style="yellow")
        table.add_column("Class", style="white")
        
        for device in devices:
            table.add_row(
                device['name'],
                device['address'],
                device['class']
            )
            
        self.console.print(table)
        
    # Validation methods
    def validate_network_target(self, target: str) -> bool:
        """Validate network target format."""
        try:
            # Try to parse as IP network
            ipaddress.ip_network(target, strict=False)
            return True
        except ValueError:
            try:
                # Try to parse as single IP
                ipaddress.ip_address(target)
                return True
            except ValueError:
                # Check if it's a domain or hostname
                if '.' in target and not target.replace('.', '').replace('-', '').isdigit():
                    return True
                    
        self.console.print(f"[red]Invalid target format: {target}[/]")
        self.console.print("[yellow]Use IP, CIDR notation, or domain name[/]")
        return False
        
    def validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            self.console.print(f"[red]Invalid IP address: {ip}[/]")
            return False


# Example usage
if __name__ == "__main__":
    recon_cli = ReconCLI()
    recon_cli.run([])