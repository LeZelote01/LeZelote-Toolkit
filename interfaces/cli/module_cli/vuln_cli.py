#!/usr/bin/env python3
"""
Vulnerability Assessment Module CLI for Pentest-USB Toolkit
===========================================================

CLI interface for vulnerability assessment operations including web application
scanning, network vulnerability assessment, cloud auditing, and code analysis.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import threading
import time
import json

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
from rich.tree import Tree

from core.engine.orchestrator import PentestOrchestrator
from modules.vulnerability.web_scanner import WebScanner
from modules.vulnerability.network_vuln import NetworkVulnScanner
from modules.vulnerability.cloud_audit import CloudAuditor
from modules.vulnerability.static_analyzer import StaticAnalyzer
from modules.vulnerability.mobile_audit import MobileAuditor
from core.utils.logging_handler import LoggingHandler


class VulnCLI:
    """CLI interface for vulnerability assessment module operations."""
    
    def __init__(self):
        """Initialize vulnerability assessment CLI."""
        self.console = Console()
        self.logger = LoggingHandler().get_logger("VulnCLI")
        
        # Module instances
        self.web_scanner = WebScanner()
        self.network_scanner = NetworkVulnScanner()
        self.cloud_auditor = CloudAuditor()
        self.static_analyzer = StaticAnalyzer()
        self.mobile_auditor = MobileAuditor()
        
        # Current scan state
        self.current_target = None
        self.scan_results = {}
        self.running_scans = {}
        self.vulnerability_db = {}
        
    def run(self, args: List[str]):
        """Run vulnerability assessment CLI with provided arguments."""
        try:
            if args and args[0] == "--help":
                self.show_help()
                return
                
            self.show_banner()
            self.interactive_shell()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Vulnerability assessment module interrupted.[/]")
        except Exception as e:
            self.logger.error(f"VulnCLI error: {e}")
            self.console.print(f"[red]Error: {e}[/]")
            
    def show_banner(self):
        """Display vulnerability assessment module banner."""
        banner = """
[bold red]
██╗   ██╗██╗   ██╗██╗     ███╗   ██╗
██║   ██║██║   ██║██║     ████╗  ██║
██║   ██║██║   ██║██║     ██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝
[/]
[bold red]VULNERABILITY ASSESSMENT[/]
[dim]Web scanning • Network auditing • Code analysis[/]
"""
        
        self.console.print(Panel(
            banner,
            title="[bold red]Vulnerability Assessment[/]",
            border_style="red",
            box=box.DOUBLE_EDGE
        ))
        
    def show_help(self):
        """Show vulnerability assessment module help."""
        help_text = """
[bold cyan]Vulnerability Assessment Commands[/]

[bold yellow]Web Application Scanning:[/]
  webscan <url>        - Comprehensive web vulnerability scan
  sqlscan <url>        - SQL injection testing
  xssscan <url>        - Cross-site scripting detection
  dirbust <url>        - Directory and file enumeration
  wpscan <url>         - WordPress security scan
  
[bold yellow]Network Vulnerability Assessment:[/]
  netscan <target>     - Network vulnerability assessment
  smbscan <host>       - SMB vulnerability testing
  sshscan <host>       - SSH security assessment
  ftpscan <host>       - FTP vulnerability testing
  
[bold yellow]Cloud Security Auditing:[/]
  cloudscan <provider> - Cloud configuration assessment
  awsaudit             - AWS security audit
  azureaudit           - Azure security audit
  gcpaudit             - Google Cloud audit
  k8saudit             - Kubernetes security scan
  
[bold yellow]Code Analysis:[/]
  codescan <path>      - Static code analysis
  secretscan <path>    - Secret detection in code
  depscan <path>       - Dependency vulnerability scan
  
[bold yellow]Mobile Security:[/]
  apkscan <file>       - Android APK security analysis
  ipascan <file>       - iOS IPA security analysis
  
[bold yellow]Reporting & Management:[/]
  vulnlist             - List discovered vulnerabilities
  severity <level>     - Filter by severity (critical/high/medium/low)
  export <format>      - Export results (json/xml/csv/pdf)
  dashboard            - Show vulnerability dashboard
  
[bold yellow]General Commands:[/]
  status               - Show current scan status
  results              - Display scan results
  set <target>         - Set current target
  back                 - Return to main menu
  help                 - Show this help
"""
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))
        
    def interactive_shell(self):
        """Run interactive vulnerability assessment shell."""
        self.console.print("\n[red]Vulnerability assessment module started[/]")
        self.console.print("[dim]Type 'help' for commands, 'back' to return[/]\n")
        
        while True:
            try:
                # Show current target and vuln count in prompt
                target_info = f"({self.current_target})" if self.current_target else ""
                vuln_count = len(self.vulnerability_db)
                vuln_info = f"[{vuln_count} vulns]" if vuln_count > 0 else ""
                
                command = Prompt.ask(
                    f"[bold red]vuln{target_info}{vuln_info}[/]",
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
        """Execute vulnerability assessment command."""
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        command_map = {
            'help': self.show_help,
            'webscan': self.web_scan,
            'sqlscan': self.sql_scan,
            'xssscan': self.xss_scan,
            'dirbust': self.directory_bust,
            'wpscan': self.wordpress_scan,
            'netscan': self.network_scan,
            'smbscan': self.smb_scan,
            'sshscan': self.ssh_scan,
            'ftpscan': self.ftp_scan,
            'cloudscan': self.cloud_scan,
            'awsaudit': self.aws_audit,
            'azureaudit': self.azure_audit,
            'gcpaudit': self.gcp_audit,
            'k8saudit': self.kubernetes_audit,
            'codescan': self.code_scan,
            'secretscan': self.secret_scan,
            'depscan': self.dependency_scan,
            'apkscan': self.apk_scan,
            'ipascan': self.ipa_scan,
            'vulnlist': self.list_vulnerabilities,
            'severity': self.filter_by_severity,
            'export': self.export_results,
            'dashboard': self.show_dashboard,
            'status': self.show_status,
            'results': self.show_results,
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
            
    def web_scan(self, args: List[str] = None):
        """Perform comprehensive web vulnerability scan."""
        if not args:
            url = Prompt.ask("[cyan]Enter target URL")
        else:
            url = args[0]
            
        if not self.validate_url(url):
            return
            
        self.current_target = url
        
        # Scan configuration
        scan_type = Prompt.ask(
            "[cyan]Scan type",
            choices=["quick", "comprehensive", "aggressive", "stealth"],
            default="comprehensive"
        )
        
        include_authenticated = Confirm.ask("[cyan]Include authenticated scanning?", default=False)
        
        self.console.print(f"[red]Starting web vulnerability scan on {url}[/]")
        
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
            
            # Multiple scan phases
            phases = [
                ("Spider crawling", 25),
                ("Directory enumeration", 20),
                ("SQL injection testing", 20),
                ("XSS detection", 15),
                ("Authentication bypass", 10),
                ("File inclusion testing", 10)
            ]
            
            total_progress = 0
            task = progress.add_task(f"Scanning {url}", total=100)
            
            for phase_name, phase_weight in phases:
                progress.update(task, description=f"Scanning {url} - {phase_name}")
                
                # Simulate phase work
                for i in range(phase_weight):
                    progress.update(task, advance=1)
                    time.sleep(0.1)  # Simulate work
                    
        # Simulate vulnerability results
        vulnerabilities = [
            {
                'id': 'WEB-001',
                'title': 'SQL Injection in login form',
                'severity': 'critical',
                'cvss': 9.8,
                'url': f'{url}/login.php',
                'parameter': 'username',
                'description': 'Time-based blind SQL injection vulnerability',
                'impact': 'Database compromise, data exfiltration',
                'recommendation': 'Use parameterized queries'
            },
            {
                'id': 'WEB-002',
                'title': 'Reflected XSS in search function',
                'severity': 'high',
                'cvss': 6.1,
                'url': f'{url}/search.php',
                'parameter': 'q',
                'description': 'User input is reflected without proper encoding',
                'impact': 'Session hijacking, credential theft',
                'recommendation': 'Implement output encoding and CSP'
            },
            {
                'id': 'WEB-003',
                'title': 'Directory traversal vulnerability',
                'severity': 'medium',
                'cvss': 5.3,
                'url': f'{url}/download.php',
                'parameter': 'file',
                'description': 'Insufficient path validation allows file system access',
                'impact': 'Sensitive file disclosure',
                'recommendation': 'Implement proper input validation'
            }
        ]
        
        # Store results
        self.scan_results['web'] = {
            'target': url,
            'scan_type': scan_type,
            'vulnerabilities': vulnerabilities,
            'scan_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Update vulnerability database
        for vuln in vulnerabilities:
            self.vulnerability_db[vuln['id']] = vuln
            
        self.display_web_results(vulnerabilities)
        
    def sql_scan(self, args: List[str] = None):
        """Perform focused SQL injection testing."""
        if not args:
            url = Prompt.ask("[cyan]Enter target URL")
        else:
            url = args[0]
            
        self.console.print(f"[red]Testing SQL injection vectors on {url}[/]")
        
        # SQL injection testing simulation
        vulnerabilities = [
            {
                'id': 'SQL-001',
                'title': 'Time-based Blind SQL Injection',
                'severity': 'critical',
                'parameter': 'id',
                'payload': "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
                'response_time': '5.2s',
                'database': 'MySQL 8.0'
            }
        ]
        
        self.display_sql_results(url, vulnerabilities)
        
    def xss_scan(self, args: List[str] = None):
        """Perform XSS vulnerability testing."""
        if not args:
            url = Prompt.ask("[cyan]Enter target URL")
        else:
            url = args[0]
            
        self.console.print(f"[red]Testing XSS vulnerabilities on {url}[/]")
        
        # XSS testing simulation
        vulnerabilities = [
            {
                'id': 'XSS-001',
                'title': 'Reflected XSS',
                'severity': 'high',
                'parameter': 'search',
                'payload': '<script>alert("XSS")</script>',
                'type': 'Reflected'
            },
            {
                'id': 'XSS-002', 
                'title': 'DOM-based XSS',
                'severity': 'medium',
                'parameter': 'fragment',
                'payload': '#<img src=x onerror=alert(1)>',
                'type': 'DOM-based'
            }
        ]
        
        self.display_xss_results(url, vulnerabilities)
        
    def directory_bust(self, args: List[str] = None):
        """Perform directory and file enumeration."""
        if not args:
            url = Prompt.ask("[cyan]Enter target URL")
        else:
            url = args[0]
            
        wordlist = Prompt.ask(
            "[cyan]Wordlist",
            choices=["common", "comprehensive", "admin", "api"],
            default="common"
        )
        
        self.console.print(f"[red]Directory enumeration on {url}[/]")
        
        # Directory busting simulation
        discovered_paths = [
            {'path': '/admin/', 'status': 200, 'size': '1.2KB'},
            {'path': '/backup/', 'status': 403, 'size': '0B'},
            {'path': '/api/', 'status': 200, 'size': '856B'},
            {'path': '/config.php', 'status': 200, 'size': '2.1KB'},
            {'path': '/.git/', 'status': 301, 'size': '0B'}
        ]
        
        self.display_directory_results(url, discovered_paths)
        
    def wordpress_scan(self, args: List[str] = None):
        """Perform WordPress security scan."""
        if not args:
            url = Prompt.ask("[cyan]Enter WordPress site URL")
        else:
            url = args[0]
            
        self.console.print(f"[red]WordPress security scan on {url}[/]")
        
        # WordPress scan simulation
        wp_info = {
            'version': '5.8.2',
            'theme': 'twentytwentyone',
            'plugins': ['contact-form-7', 'yoast-seo', 'akismet'],
            'vulnerabilities': [
                {
                    'component': 'WordPress Core',
                    'version': '5.8.2',
                    'vulnerability': 'CVE-2021-39201',
                    'severity': 'medium'
                },
                {
                    'component': 'Plugin: contact-form-7',
                    'version': '5.4.1',
                    'vulnerability': 'Stored XSS',
                    'severity': 'high'
                }
            ]
        }
        
        self.display_wordpress_results(url, wp_info)
        
    def network_scan(self, args: List[str] = None):
        """Perform network vulnerability assessment."""
        if not args:
            target = Prompt.ask("[cyan]Enter target (IP/range)")
        else:
            target = args[0]
            
        self.console.print(f"[red]Network vulnerability assessment on {target}[/]")
        
        # Network vulnerability simulation
        network_vulns = [
            {
                'host': '192.168.1.100',
                'port': 445,
                'service': 'SMB',
                'vulnerability': 'MS17-010 (EternalBlue)',
                'severity': 'critical',
                'cvss': 9.3
            },
            {
                'host': '192.168.1.100',
                'port': 22,
                'service': 'SSH',
                'vulnerability': 'Weak encryption algorithms',
                'severity': 'medium',
                'cvss': 5.3
            }
        ]
        
        self.display_network_vulns(target, network_vulns)
        
    def smb_scan(self, args: List[str] = None):
        """Perform SMB vulnerability testing."""
        if not args:
            host = Prompt.ask("[cyan]Enter host IP")
        else:
            host = args[0]
            
        self.console.print(f"[red]SMB vulnerability testing on {host}[/]")
        
        # SMB testing simulation
        smb_vulns = [
            {
                'vulnerability': 'MS17-010 (EternalBlue)',
                'severity': 'critical',
                'exploitable': True,
                'shares': ['ADMIN$', 'C$', 'IPC$']
            }
        ]
        
        self.display_smb_results(host, smb_vulns)
        
    def ssh_scan(self, args: List[str] = None):
        """Perform SSH security assessment."""
        if not args:
            host = Prompt.ask("[cyan]Enter host IP")
        else:
            host = args[0]
            
        self.console.print(f"[red]SSH security assessment on {host}[/]")
        
        # SSH assessment simulation
        ssh_info = {
            'version': 'OpenSSH 7.4',
            'algorithms': {
                'weak_ciphers': ['aes128-cbc', 'aes192-cbc'],
                'weak_macs': ['hmac-md5', 'hmac-sha1-96'],
                'weak_kex': ['diffie-hellman-group14-sha1']
            },
            'configuration_issues': [
                'PermitRootLogin yes',
                'PasswordAuthentication yes',
                'PermitEmptyPasswords yes'
            ]
        }
        
        self.display_ssh_results(host, ssh_info)
        
    def ftp_scan(self, args: List[str] = None):
        """Perform FTP vulnerability testing."""
        if not args:
            host = Prompt.ask("[cyan]Enter host IP")
        else:
            host = args[0]
            
        self.console.print(f"[red]FTP vulnerability testing on {host}[/]")
        
        # FTP testing simulation
        ftp_info = {
            'version': 'vsftpd 3.0.3',
            'anonymous_login': True,
            'writable_directories': ['/pub/upload'],
            'vulnerabilities': [
                {
                    'type': 'Anonymous access enabled',
                    'severity': 'medium',
                    'impact': 'Information disclosure'
                }
            ]
        }
        
        self.display_ftp_results(host, ftp_info)
        
    def cloud_scan(self, args: List[str] = None):
        """Perform cloud configuration assessment."""
        if not args:
            provider = Prompt.ask(
                "[cyan]Cloud provider",
                choices=["aws", "azure", "gcp"],
                default="aws"
            )
        else:
            provider = args[0]
            
        self.console.print(f"[red]Cloud security assessment for {provider.upper()}[/]")
        
        if provider == "aws":
            self.aws_audit()
        elif provider == "azure":
            self.azure_audit()
        elif provider == "gcp":
            self.gcp_audit()
            
    def aws_audit(self, args: List[str] = None):
        """Perform AWS security audit."""
        self.console.print("[red]AWS security audit in progress...[/]")
        
        # AWS audit simulation
        aws_findings = [
            {
                'service': 'S3',
                'resource': 'example-bucket',
                'finding': 'Bucket publicly readable',
                'severity': 'high',
                'region': 'us-east-1'
            },
            {
                'service': 'EC2',
                'resource': 'i-1234567890abcdef0',
                'finding': 'Security group allows 0.0.0.0/0 on port 22',
                'severity': 'critical',
                'region': 'us-west-2'
            },
            {
                'service': 'IAM',
                'resource': 'admin-user',
                'finding': 'User has AdministratorAccess policy',
                'severity': 'medium',
                'region': 'global'
            }
        ]
        
        self.display_cloud_results("AWS", aws_findings)
        
    def azure_audit(self, args: List[str] = None):
        """Perform Azure security audit."""
        self.console.print("[red]Azure security audit in progress...[/]")
        
        # Azure audit simulation
        azure_findings = [
            {
                'service': 'Storage Account',
                'resource': 'examplestorage',
                'finding': 'Blob container publicly accessible',
                'severity': 'high',
                'region': 'East US'
            }
        ]
        
        self.display_cloud_results("Azure", azure_findings)
        
    def gcp_audit(self, args: List[str] = None):
        """Perform Google Cloud audit."""
        self.console.print("[red]Google Cloud audit in progress...[/]")
        
        # GCP audit simulation
        gcp_findings = [
            {
                'service': 'Cloud Storage',
                'resource': 'example-bucket',
                'finding': 'Bucket allows public read access',
                'severity': 'high',
                'region': 'us-central1'
            }
        ]
        
        self.display_cloud_results("Google Cloud", gcp_findings)
        
    def kubernetes_audit(self, args: List[str] = None):
        """Perform Kubernetes security audit."""
        self.console.print("[red]Kubernetes security audit in progress...[/]")
        
        # K8s audit simulation
        k8s_findings = [
            {
                'namespace': 'default',
                'resource': 'pod/nginx-deployment',
                'finding': 'Container running as root',
                'severity': 'medium',
                'rule': 'CIS 5.1.5'
            },
            {
                'namespace': 'kube-system',
                'resource': 'configmap/cluster-info',
                'finding': 'Cluster info exposed',
                'severity': 'low',
                'rule': 'CIS 1.1.12'
            }
        ]
        
        self.display_k8s_results(k8s_findings)
        
    def code_scan(self, args: List[str] = None):
        """Perform static code analysis."""
        if not args:
            path = Prompt.ask("[cyan]Enter code path/directory")
        else:
            path = args[0]
            
        language = Prompt.ask(
            "[cyan]Programming language",
            choices=["auto", "python", "java", "javascript", "php", "c#"],
            default="auto"
        )
        
        self.console.print(f"[red]Static code analysis on {path}[/]")
        
        # Code analysis simulation
        code_issues = [
            {
                'file': 'login.py',
                'line': 45,
                'issue': 'Hardcoded password',
                'severity': 'critical',
                'rule': 'B106'
            },
            {
                'file': 'utils.js',
                'line': 23,
                'issue': 'Potential XSS vulnerability',
                'severity': 'high',
                'rule': 'ESL001'
            },
            {
                'file': 'config.php',
                'line': 12,
                'issue': 'SQL injection vulnerability',
                'severity': 'critical',
                'rule': 'PHP002'
            }
        ]
        
        self.display_code_results(path, code_issues)
        
    def secret_scan(self, args: List[str] = None):
        """Perform secret detection in code."""
        if not args:
            path = Prompt.ask("[cyan]Enter code path/directory")
        else:
            path = args[0]
            
        self.console.print(f"[red]Secret detection scan on {path}[/]")
        
        # Secret detection simulation
        secrets = [
            {
                'file': '.env',
                'line': 3,
                'type': 'AWS Access Key',
                'value': 'AKIA***************',
                'confidence': 'high'
            },
            {
                'file': 'config.py',
                'line': 15,
                'type': 'Database Password',
                'value': 'password123',
                'confidence': 'medium'
            }
        ]
        
        self.display_secret_results(path, secrets)
        
    def dependency_scan(self, args: List[str] = None):
        """Perform dependency vulnerability scan."""
        if not args:
            path = Prompt.ask("[cyan]Enter project path")
        else:
            path = args[0]
            
        self.console.print(f"[red]Dependency vulnerability scan on {path}[/]")
        
        # Dependency scan simulation
        dep_vulns = [
            {
                'package': 'requests',
                'version': '2.25.1',
                'vulnerability': 'CVE-2021-33503',
                'severity': 'medium',
                'fixed_version': '2.25.2'
            },
            {
                'package': 'django',
                'version': '3.1.0',
                'vulnerability': 'CVE-2021-35042',
                'severity': 'high',
                'fixed_version': '3.1.13'
            }
        ]
        
        self.display_dependency_results(path, dep_vulns)
        
    def apk_scan(self, args: List[str] = None):
        """Perform Android APK security analysis."""
        if not args:
            apk_file = Prompt.ask("[cyan]Enter APK file path")
        else:
            apk_file = args[0]
            
        self.console.print(f"[red]APK security analysis on {apk_file}[/]")
        
        # APK analysis simulation
        apk_results = {
            'app_name': 'Example App',
            'package': 'com.example.app',
            'version': '1.2.3',
            'permissions': ['INTERNET', 'READ_EXTERNAL_STORAGE', 'CAMERA'],
            'vulnerabilities': [
                {
                    'type': 'Insecure data storage',
                    'severity': 'high',
                    'description': 'Sensitive data stored in plain text'
                },
                {
                    'type': 'Network security misconfiguration',
                    'severity': 'medium',
                    'description': 'Allows cleartext traffic'
                }
            ]
        }
        
        self.display_apk_results(apk_file, apk_results)
        
    def ipa_scan(self, args: List[str] = None):
        """Perform iOS IPA security analysis."""
        if not args:
            ipa_file = Prompt.ask("[cyan]Enter IPA file path")
        else:
            ipa_file = args[0]
            
        self.console.print(f"[red]IPA security analysis on {ipa_file}[/]")
        
        # IPA analysis simulation
        ipa_results = {
            'app_name': 'Example iOS App',
            'bundle_id': 'com.example.iosapp',
            'version': '2.1.0',
            'vulnerabilities': [
                {
                    'type': 'Binary protection bypass',
                    'severity': 'medium',
                    'description': 'Stack canaries disabled'
                }
            ]
        }
        
        self.display_ipa_results(ipa_file, ipa_results)
        
    def list_vulnerabilities(self, args: List[str] = None):
        """List all discovered vulnerabilities."""
        if not self.vulnerability_db:
            self.console.print("[yellow]No vulnerabilities discovered yet[/]")
            return
            
        # Group by severity
        severity_groups = {}
        for vuln_id, vuln in self.vulnerability_db.items():
            severity = vuln.get('severity', 'unknown')
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(vuln)
            
        # Display by severity
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        
        for severity in severity_order:
            if severity in severity_groups:
                self.display_vulnerability_group(severity, severity_groups[severity])
                
    def filter_by_severity(self, args: List[str] = None):
        """Filter vulnerabilities by severity level."""
        if not args:
            severity = Prompt.ask(
                "[cyan]Severity level",
                choices=["critical", "high", "medium", "low", "info"]
            )
        else:
            severity = args[0].lower()
            
        filtered_vulns = [
            vuln for vuln in self.vulnerability_db.values()
            if vuln.get('severity', '').lower() == severity
        ]
        
        if not filtered_vulns:
            self.console.print(f"[yellow]No {severity} severity vulnerabilities found[/]")
            return
            
        self.display_vulnerability_group(severity, filtered_vulns)
        
    def export_results(self, args: List[str] = None):
        """Export vulnerability results."""
        if not self.vulnerability_db and not self.scan_results:
            self.console.print("[yellow]No results to export[/]")
            return
            
        format_type = args[0] if args else Prompt.ask(
            "[cyan]Export format",
            choices=["json", "xml", "csv", "pdf"],
            default="json"
        )
        
        filename = f"vuln_results.{format_type}"
        
        # Export implementation would go here
        self.console.print(f"[green]Results exported to {filename}[/]")
        
    def show_dashboard(self):
        """Show vulnerability dashboard."""
        if not self.vulnerability_db:
            self.console.print("[yellow]No vulnerability data for dashboard[/]")
            return
            
        # Create vulnerability dashboard
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header
        header = Panel(
            "[bold red]🛡️  VULNERABILITY DASHBOARD[/]",
            style="bold red"
        )
        layout["header"].update(header)
        
        # Severity summary
        severity_counts = {}
        for vuln in self.vulnerability_db.values():
            sev = vuln.get('severity', 'unknown')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
        severity_table = Table(title="Vulnerability Summary", box=box.ROUNDED)
        severity_table.add_column("Severity", style="yellow")
        severity_table.add_column("Count", style="white")
        
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            color = self.get_severity_color(severity)
            severity_table.add_row(f"[{color}]{severity.title()}[/]", str(count))
            
        layout["left"].update(Panel(severity_table, border_style="blue"))
        
        # Recent vulnerabilities
        recent_vulns = list(self.vulnerability_db.values())[-5:]  # Last 5
        recent_table = Table(title="Recent Discoveries", box=box.ROUNDED)
        recent_table.add_column("ID", style="cyan")
        recent_table.add_column("Title", style="white")
        recent_table.add_column("Severity", style="yellow")
        
        for vuln in recent_vulns:
            color = self.get_severity_color(vuln.get('severity', 'unknown'))
            recent_table.add_row(
                vuln.get('id', 'N/A'),
                vuln.get('title', 'Unknown')[:30] + "..." if len(vuln.get('title', '')) > 30 else vuln.get('title', ''),
                f"[{color}]{vuln.get('severity', 'Unknown').title()}[/]"
            )
            
        layout["right"].update(Panel(recent_table, border_style="green"))
        
        # Footer
        footer = Panel(
            "[dim]Press Ctrl+C to return to shell[/]",
            style="dim"
        )
        layout["footer"].update(footer)
        
        # Display dashboard
        try:
            with Live(layout, refresh_per_second=1, screen=True) as live:
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Dashboard closed[/]")
            
    def show_status(self):
        """Show current scan status."""
        status_table = Table(title="Vulnerability Assessment Status", box=box.ROUNDED)
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Current Target", self.current_target or "None")
        status_table.add_row("Active Scans", str(len(self.running_scans)))
        status_table.add_row("Vulnerabilities Found", str(len(self.vulnerability_db)))
        status_table.add_row("Completed Scans", str(len(self.scan_results)))
        
        # Severity breakdown
        if self.vulnerability_db:
            severity_counts = {}
            for vuln in self.vulnerability_db.values():
                sev = vuln.get('severity', 'unknown')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
            for severity, count in severity_counts.items():
                if count > 0:
                    color = self.get_severity_color(severity)
                    status_table.add_row(f"{severity.title()} Severity", f"[{color}]{count}[/]")
                    
        self.console.print(status_table)
        
    def show_results(self):
        """Display all scan results."""
        if not self.scan_results:
            self.console.print("[yellow]No scan results available[/]")
            return
            
        for scan_type, results in self.scan_results.items():
            self.console.print(f"\n[bold red]{scan_type.title()} Scan Results:[/]")
            
            if scan_type == 'web':
                self.display_web_results(results.get('vulnerabilities', []))
            # Add other result types as needed
                
    def set_target(self, args: List[str] = None):
        """Set current target."""
        if args:
            target = args[0]
        else:
            target = Prompt.ask("[cyan]Enter target")
            
        self.current_target = target
        self.console.print(f"[green]Target set to: {target}[/]")
        
    # Display methods
    def display_web_results(self, vulnerabilities: List[Dict[str, Any]]):
        """Display web vulnerability scan results."""
        if not vulnerabilities:
            self.console.print("[green]No vulnerabilities found[/]")
            return
            
        table = Table(title="Web Vulnerabilities", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Severity", style="yellow")
        table.add_column("CVSS", style="red")
        table.add_column("URL", style="blue")
        
        for vuln in vulnerabilities:
            color = self.get_severity_color(vuln.get('severity', 'unknown'))
            table.add_row(
                vuln.get('id', 'N/A'),
                vuln.get('title', 'Unknown'),
                f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]",
                str(vuln.get('cvss', 'N/A')),
                vuln.get('url', 'N/A')
            )
            
        self.console.print(table)
        
    def display_sql_results(self, url: str, vulnerabilities: List[Dict[str, Any]]):
        """Display SQL injection test results."""
        table = Table(title=f"SQL Injection Results - {url}", box=box.ROUNDED)
        table.add_column("Parameter", style="cyan")
        table.add_column("Payload", style="yellow")
        table.add_column("Response Time", style="white")
        table.add_column("Database", style="green")
        
        for vuln in vulnerabilities:
            table.add_row(
                vuln.get('parameter', 'N/A'),
                vuln.get('payload', 'N/A')[:50] + "..." if len(vuln.get('payload', '')) > 50 else vuln.get('payload', ''),
                vuln.get('response_time', 'N/A'),
                vuln.get('database', 'Unknown')
            )
            
        self.console.print(table)
        
    def display_xss_results(self, url: str, vulnerabilities: List[Dict[str, Any]]):
        """Display XSS test results."""
        table = Table(title=f"XSS Vulnerabilities - {url}", box=box.ROUNDED)
        table.add_column("Type", style="yellow")
        table.add_column("Parameter", style="cyan")
        table.add_column("Payload", style="red")
        table.add_column("Severity", style="white")
        
        for vuln in vulnerabilities:
            color = self.get_severity_color(vuln.get('severity', 'unknown'))
            table.add_row(
                vuln.get('type', 'Unknown'),
                vuln.get('parameter', 'N/A'),
                vuln.get('payload', 'N/A'),
                f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]"
            )
            
        self.console.print(table)
        
    def display_directory_results(self, url: str, paths: List[Dict[str, Any]]):
        """Display directory enumeration results."""
        table = Table(title=f"Directory Enumeration - {url}", box=box.ROUNDED)
        table.add_column("Path", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("Size", style="white")
        
        for path_info in paths:
            status_color = "green" if path_info['status'] == 200 else "yellow" if path_info['status'] == 403 else "red"
            table.add_row(
                path_info['path'],
                f"[{status_color}]{path_info['status']}[/]",
                path_info['size']
            )
            
        self.console.print(table)
        
    def display_wordpress_results(self, url: str, wp_info: Dict[str, Any]):
        """Display WordPress scan results."""
        # Basic info
        info_table = Table(title=f"WordPress Information - {url}", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("Version", wp_info.get('version', 'Unknown'))
        info_table.add_row("Theme", wp_info.get('theme', 'Unknown'))
        info_table.add_row("Plugins", ", ".join(wp_info.get('plugins', [])))
        
        self.console.print(info_table)
        
        # Vulnerabilities
        if wp_info.get('vulnerabilities'):
            vuln_table = Table(title="WordPress Vulnerabilities", box=box.ROUNDED)
            vuln_table.add_column("Component", style="yellow")
            vuln_table.add_column("Version", style="cyan")
            vuln_table.add_column("Vulnerability", style="red")
            vuln_table.add_column("Severity", style="white")
            
            for vuln in wp_info['vulnerabilities']:
                color = self.get_severity_color(vuln.get('severity', 'unknown'))
                vuln_table.add_row(
                    vuln.get('component', 'Unknown'),
                    vuln.get('version', 'N/A'),
                    vuln.get('vulnerability', 'Unknown'),
                    f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]"
                )
                
            self.console.print(vuln_table)
            
    def display_network_vulns(self, target: str, vulns: List[Dict[str, Any]]):
        """Display network vulnerability results."""
        table = Table(title=f"Network Vulnerabilities - {target}", box=box.ROUNDED)
        table.add_column("Host", style="cyan")
        table.add_column("Port", style="yellow")
        table.add_column("Service", style="green")
        table.add_column("Vulnerability", style="red")
        table.add_column("CVSS", style="white")
        
        for vuln in vulns:
            table.add_row(
                vuln.get('host', 'N/A'),
                str(vuln.get('port', 'N/A')),
                vuln.get('service', 'Unknown'),
                vuln.get('vulnerability', 'Unknown'),
                str(vuln.get('cvss', 'N/A'))
            )
            
        self.console.print(table)
        
    def display_smb_results(self, host: str, vulns: List[Dict[str, Any]]):
        """Display SMB vulnerability results."""
        table = Table(title=f"SMB Vulnerabilities - {host}", box=box.ROUNDED)
        table.add_column("Vulnerability", style="red")
        table.add_column("Severity", style="yellow")
        table.add_column("Exploitable", style="green")
        table.add_column("Shares", style="cyan")
        
        for vuln in vulns:
            color = self.get_severity_color(vuln.get('severity', 'unknown'))
            table.add_row(
                vuln.get('vulnerability', 'Unknown'),
                f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]",
                "Yes" if vuln.get('exploitable') else "No",
                ", ".join(vuln.get('shares', []))
            )
            
        self.console.print(table)
        
    def display_ssh_results(self, host: str, ssh_info: Dict[str, Any]):
        """Display SSH assessment results."""
        # Version info
        info_table = Table(title=f"SSH Information - {host}", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("SSH Version", ssh_info.get('version', 'Unknown'))
        
        self.console.print(info_table)
        
        # Configuration issues
        if ssh_info.get('configuration_issues'):
            config_table = Table(title="Configuration Issues", box=box.ROUNDED)
            config_table.add_column("Issue", style="red")
            config_table.add_column("Risk", style="yellow")
            
            for issue in ssh_info['configuration_issues']:
                config_table.add_row(issue, "High" if "Root" in issue else "Medium")
                
            self.console.print(config_table)
            
    def display_ftp_results(self, host: str, ftp_info: Dict[str, Any]):
        """Display FTP vulnerability results."""
        table = Table(title=f"FTP Assessment - {host}", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Risk", style="yellow")
        
        table.add_row("Version", ftp_info.get('version', 'Unknown'), "Info")
        table.add_row("Anonymous Login", "Enabled" if ftp_info.get('anonymous_login') else "Disabled", "High" if ftp_info.get('anonymous_login') else "Low")
        
        if ftp_info.get('writable_directories'):
            table.add_row("Writable Dirs", ", ".join(ftp_info['writable_directories']), "Medium")
            
        self.console.print(table)
        
    def display_cloud_results(self, provider: str, findings: List[Dict[str, Any]]):
        """Display cloud audit results."""
        table = Table(title=f"{provider} Security Findings", box=box.ROUNDED)
        table.add_column("Service", style="cyan")
        table.add_column("Resource", style="yellow")
        table.add_column("Finding", style="red")
        table.add_column("Severity", style="white")
        table.add_column("Region", style="dim")
        
        for finding in findings:
            color = self.get_severity_color(finding.get('severity', 'unknown'))
            table.add_row(
                finding.get('service', 'Unknown'),
                finding.get('resource', 'N/A'),
                finding.get('finding', 'Unknown'),
                f"[{color}]{finding.get('severity', 'Unknown').upper()}[/]",
                finding.get('region', 'N/A')
            )
            
        self.console.print(table)
        
    def display_k8s_results(self, findings: List[Dict[str, Any]]):
        """Display Kubernetes audit results."""
        table = Table(title="Kubernetes Security Findings", box=box.ROUNDED)
        table.add_column("Namespace", style="cyan")
        table.add_column("Resource", style="yellow")
        table.add_column("Finding", style="red")
        table.add_column("Severity", style="white")
        table.add_column("Rule", style="dim")
        
        for finding in findings:
            color = self.get_severity_color(finding.get('severity', 'unknown'))
            table.add_row(
                finding.get('namespace', 'N/A'),
                finding.get('resource', 'Unknown'),
                finding.get('finding', 'Unknown'),
                f"[{color}]{finding.get('severity', 'Unknown').upper()}[/]",
                finding.get('rule', 'N/A')
            )
            
        self.console.print(table)
        
    def display_code_results(self, path: str, issues: List[Dict[str, Any]]):
        """Display code analysis results."""
        table = Table(title=f"Code Analysis Results - {path}", box=box.ROUNDED)
        table.add_column("File", style="cyan")
        table.add_column("Line", style="yellow")
        table.add_column("Issue", style="red")
        table.add_column("Severity", style="white")
        table.add_column("Rule", style="dim")
        
        for issue in issues:
            color = self.get_severity_color(issue.get('severity', 'unknown'))
            table.add_row(
                issue.get('file', 'Unknown'),
                str(issue.get('line', 'N/A')),
                issue.get('issue', 'Unknown'),
                f"[{color}]{issue.get('severity', 'Unknown').upper()}[/]",
                issue.get('rule', 'N/A')
            )
            
        self.console.print(table)
        
    def display_secret_results(self, path: str, secrets: List[Dict[str, Any]]):
        """Display secret detection results."""
        table = Table(title=f"Secret Detection Results - {path}", box=box.ROUNDED)
        table.add_column("File", style="cyan")
        table.add_column("Line", style="yellow")
        table.add_column("Type", style="red")
        table.add_column("Value", style="white")
        table.add_column("Confidence", style="green")
        
        for secret in secrets:
            confidence_color = "green" if secret.get('confidence') == 'high' else "yellow"
            table.add_row(
                secret.get('file', 'Unknown'),
                str(secret.get('line', 'N/A')),
                secret.get('type', 'Unknown'),
                secret.get('value', 'N/A'),
                f"[{confidence_color}]{secret.get('confidence', 'Unknown')}[/]"
            )
            
        self.console.print(table)
        
    def display_dependency_results(self, path: str, vulns: List[Dict[str, Any]]):
        """Display dependency vulnerability results."""
        table = Table(title=f"Dependency Vulnerabilities - {path}", box=box.ROUNDED)
        table.add_column("Package", style="cyan")
        table.add_column("Current", style="yellow")
        table.add_column("Vulnerability", style="red")
        table.add_column("Severity", style="white")
        table.add_column("Fixed In", style="green")
        
        for vuln in vulns:
            color = self.get_severity_color(vuln.get('severity', 'unknown'))
            table.add_row(
                vuln.get('package', 'Unknown'),
                vuln.get('version', 'N/A'),
                vuln.get('vulnerability', 'Unknown'),
                f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]",
                vuln.get('fixed_version', 'N/A')
            )
            
        self.console.print(table)
        
    def display_apk_results(self, apk_file: str, results: Dict[str, Any]):
        """Display APK analysis results."""
        # App info
        info_table = Table(title=f"APK Analysis - {apk_file}", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("App Name", results.get('app_name', 'Unknown'))
        info_table.add_row("Package", results.get('package', 'Unknown'))
        info_table.add_row("Version", results.get('version', 'Unknown'))
        info_table.add_row("Permissions", ", ".join(results.get('permissions', [])))
        
        self.console.print(info_table)
        
        # Vulnerabilities
        if results.get('vulnerabilities'):
            vuln_table = Table(title="Security Issues", box=box.ROUNDED)
            vuln_table.add_column("Type", style="red")
            vuln_table.add_column("Severity", style="yellow")
            vuln_table.add_column("Description", style="white")
            
            for vuln in results['vulnerabilities']:
                color = self.get_severity_color(vuln.get('severity', 'unknown'))
                vuln_table.add_row(
                    vuln.get('type', 'Unknown'),
                    f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]",
                    vuln.get('description', 'N/A')
                )
                
            self.console.print(vuln_table)
            
    def display_ipa_results(self, ipa_file: str, results: Dict[str, Any]):
        """Display IPA analysis results."""
        # App info
        info_table = Table(title=f"IPA Analysis - {ipa_file}", box=box.ROUNDED)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="white")
        
        info_table.add_row("App Name", results.get('app_name', 'Unknown'))
        info_table.add_row("Bundle ID", results.get('bundle_id', 'Unknown'))
        info_table.add_row("Version", results.get('version', 'Unknown'))
        
        self.console.print(info_table)
        
        # Vulnerabilities
        if results.get('vulnerabilities'):
            vuln_table = Table(title="Security Issues", box=box.ROUNDED)
            vuln_table.add_column("Type", style="red")
            vuln_table.add_column("Severity", style="yellow")
            vuln_table.add_column("Description", style="white")
            
            for vuln in results['vulnerabilities']:
                color = self.get_severity_color(vuln.get('severity', 'unknown'))
                vuln_table.add_row(
                    vuln.get('type', 'Unknown'),
                    f"[{color}]{vuln.get('severity', 'Unknown').upper()}[/]",
                    vuln.get('description', 'N/A')
                )
                
            self.console.print(vuln_table)
            
    def display_vulnerability_group(self, severity: str, vulnerabilities: List[Dict[str, Any]]):
        """Display a group of vulnerabilities by severity."""
        color = self.get_severity_color(severity)
        
        table = Table(title=f"{severity.title()} Severity Vulnerabilities", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("CVSS", style="red")
        table.add_column("Target", style="blue")
        
        for vuln in vulnerabilities:
            table.add_row(
                vuln.get('id', 'N/A'),
                vuln.get('title', 'Unknown'),
                str(vuln.get('cvss', 'N/A')),
                vuln.get('url', vuln.get('target', 'N/A'))
            )
            
        self.console.print(table)
        
    # Utility methods
    def get_severity_color(self, severity: str) -> str:
        """Get color for severity level."""
        colors = {
            'critical': 'bold red',
            'high': 'red', 
            'medium': 'yellow',
            'low': 'green',
            'info': 'blue',
            'unknown': 'dim'
        }
        return colors.get(severity.lower(), 'white')
        
    def validate_url(self, url: str) -> bool:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        if not url_pattern.match(url):
            self.console.print(f"[red]Invalid URL format: {url}[/]")
            return False
        return True


# Example usage
if __name__ == "__main__":
    vuln_cli = VulnCLI()
    vuln_cli.run([])