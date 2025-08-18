#!/usr/bin/env python3
"""
Reporting CLI Module for Pentest-USB Toolkit
============================================

Command-line interface for generating comprehensive security reports
including executive summaries, technical reports, and compliance assessments.
"""

import sys
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from interfaces.cli.utils import CLIUtils
from modules.reporting.report_generator import ReportGenerator
from modules.reporting.template_manager import TemplateManager
from modules.reporting.data_analyzer import DataAnalyzer
from modules.reporting.export_manager import ExportManager


class ReportCLI:
    """Command-line interface for reporting module."""
    
    def __init__(self):
        """Initialize reporting CLI."""
        self.console = Console()
        self.utils = CLIUtils()
        
        # Initialize reporting modules
        self.report_generator = ReportGenerator()
        self.template_manager = TemplateManager()
        self.data_analyzer = DataAnalyzer()
        self.export_manager = ExportManager()
        
        # CLI state
        self.available_data = {}
        self.generated_reports = []
        
    def run(self, args: List[str] = None):
        """Main entry point for reporting CLI."""
        try:
            self._show_banner()
            self._load_available_data()
            
            if args and len(args) > 0:
                # Direct command mode
                self._handle_direct_command(args)
            else:
                # Interactive mode
                self._interactive_mode()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Reporting module interrupted.[/]")
        except Exception as e:
            self.console.print(f"[red]Error in reporting module: {e}[/]")
            
    def _show_banner(self):
        """Show reporting module banner."""
        banner = """
[bold blue]📊 REPORTING MODULE[/]
[dim]Executive Reports • Technical Analysis • Compliance Assessment • Custom Templates[/]
"""
        self.console.print(Panel(banner, border_style="blue"))
        
    def _load_available_data(self):
        """Load available scan data for reporting."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Loading available data...", total=None)
            
            try:
                # Load data from various sources
                self.available_data = self.data_analyzer.load_all_data()
                
                data_count = sum(len(v) if isinstance(v, list) else 1 for v in self.available_data.values())
                progress.update(task, description=f"Loaded {data_count} data items")
                
            except Exception as e:
                progress.update(task, description=f"Error loading data: {e}")
                
        if self.available_data:
            self.console.print(f"[green]Found data for reporting: {list(self.available_data.keys())}[/]")
        else:
            self.console.print("[yellow]No scan data found. Some report types may not be available.[/]")
            
    def _handle_direct_command(self, args: List[str]):
        """Handle direct command execution."""
        if not args:
            return
            
        command = args[0].lower()
        
        if command in ['executive', 'exec']:
            self._generate_executive_report()
        elif command in ['technical', 'tech']:
            self._generate_technical_report()
        elif command in ['vulnerability', 'vuln']:
            self._generate_vulnerability_report()
        elif command in ['compliance', 'comp']:
            framework = args[1] if len(args) > 1 else None
            self._generate_compliance_report(framework)
        elif command in ['custom']:
            template = args[1] if len(args) > 1 else None
            self._generate_custom_report(template)
        elif command in ['list']:
            self._list_reports()
        elif command in ['templates']:
            self._manage_templates()
        else:
            self.console.print(f"[red]Unknown reporting command: {command}[/]")
            self._show_help()
            
    def _interactive_mode(self):
        """Run interactive reporting mode."""
        while True:
            self._show_menu()
            
            choice = Prompt.ask(
                "\n[bold cyan]Select reporting option[/]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self._generate_executive_report()
            elif choice == "2":
                self._generate_technical_report()
            elif choice == "3":
                self._generate_vulnerability_report()
            elif choice == "4":
                framework = Prompt.ask("[cyan]Compliance framework", choices=["iso27001", "nist", "pci_dss", "owasp"], default="iso27001")
                self._generate_compliance_report(framework)
            elif choice == "5":
                self._generate_custom_report()
            elif choice == "6":
                self._list_reports()
            elif choice == "7":
                self._manage_templates()
            elif choice == "8":
                self._analyze_data()
            elif choice == "9":
                self._export_reports()
                
    def _show_menu(self):
        """Display reporting menu options."""
        table = Table(title="[bold blue]Reporting Options[/]", box=box.ROUNDED)
        table.add_column("Option", style="bold yellow", justify="center")
        table.add_column("Report Type", style="bold green")
        table.add_column("Description", style="white")
        
        table.add_row("1", "Executive Summary", "High-level summary for management")
        table.add_row("2", "Technical Report", "Detailed technical findings and analysis")
        table.add_row("3", "Vulnerability Report", "Focused vulnerability assessment report")
        table.add_row("4", "Compliance Report", "Compliance framework assessment")
        table.add_row("5", "Custom Report", "Generate report from custom template")
        table.add_row("", "", "")
        table.add_row("6", "List Reports", "View generated reports")
        table.add_row("7", "Manage Templates", "Manage report templates")
        table.add_row("8", "Analyze Data", "Perform data analysis")
        table.add_row("9", "Export Reports", "Export reports to various formats")
        table.add_row("0", "Back", "Return to main menu")
        
        self.console.print(table)
        
    def _generate_executive_report(self):
        """Generate executive summary report."""
        self.console.print("\n[bold green]Generating Executive Summary Report[/]")
        
        if not self.available_data:
            self.console.print("[red]No data available for report generation.[/]")
            if Confirm.ask("[cyan]Load sample data for demonstration?[/]"):
                self.available_data = self._load_sample_data()
            else:
                return
                
        # Report configuration
        config = {
            'report_type': 'executive',
            'include_charts': Confirm.ask("[cyan]Include charts and graphs?[/]", default=True),
            'include_recommendations': Confirm.ask("[cyan]Include executive recommendations?[/]", default=True),
            'risk_threshold': Prompt.ask("[cyan]Risk threshold", choices=["low", "medium", "high"], default="medium"),
            'target_audience': 'executives'
        }
        
        # Company information
        config['company_info'] = {
            'name': Prompt.ask("[cyan]Company name", default="Target Organization"),
            'assessment_date': Prompt.ask("[cyan]Assessment date", default=datetime.now().strftime("%Y-%m-%d")),
            'assessor': Prompt.ask("[cyan]Lead assessor", default="Pentest Team")
        }
        
        self._generate_report(config)
        
    def _generate_technical_report(self):
        """Generate detailed technical report."""
        self.console.print("\n[bold green]Generating Technical Report[/]")
        
        if not self.available_data:
            self.console.print("[red]No data available for report generation.[/]")
            return
            
        # Report configuration
        config = {
            'report_type': 'technical',
            'detail_level': Prompt.ask("[cyan]Detail level", choices=["basic", "standard", "comprehensive"], default="standard"),
            'include_screenshots': Confirm.ask("[cyan]Include screenshots?[/]", default=True),
            'include_code_samples': Confirm.ask("[cyan]Include code samples?[/]", default=True),
            'include_remediation': Confirm.ask("[cyan]Include remediation steps?[/]", default=True),
            'target_audience': 'technical'
        }
        
        # Section selection
        sections = []
        if Confirm.ask("[cyan]Include reconnaissance findings?[/]", default=True):
            sections.append("reconnaissance")
        if Confirm.ask("[cyan]Include vulnerability details?[/]", default=True):
            sections.append("vulnerabilities")
        if Confirm.ask("[cyan]Include exploitation proof-of-concepts?[/]", default=True):
            sections.append("exploitation")
        if Confirm.ask("[cyan]Include post-exploitation activities?[/]", default=False):
            sections.append("post_exploitation")
            
        config['sections'] = sections
        
        self._generate_report(config)
        
    def _generate_vulnerability_report(self):
        """Generate vulnerability-focused report."""
        self.console.print("\n[bold green]Generating Vulnerability Report[/]")
        
        if not self.available_data.get('vulnerabilities'):
            self.console.print("[yellow]No vulnerability data available.[/]")
            if not Confirm.ask("[cyan]Generate report anyway?[/]"):
                return
                
        # Report configuration
        config = {
            'report_type': 'vulnerability',
            'severity_filter': Prompt.ask("[cyan]Minimum severity", choices=["info", "low", "medium", "high", "critical"], default="low"),
            'group_by': Prompt.ask("[cyan]Group vulnerabilities by", choices=["severity", "category", "host"], default="severity"),
            'include_cvss': Confirm.ask("[cyan]Include CVSS scores?[/]", default=True),
            'include_references': Confirm.ask("[cyan]Include CVE references?[/]", default=True),
            'include_remediation': Confirm.ask("[cyan]Include remediation guidance?[/]", default=True)
        }
        
        # CVSS scoring
        if config['include_cvss']:
            config['cvss_version'] = Prompt.ask("[cyan]CVSS version", choices=["2.0", "3.0", "3.1"], default="3.1")
            
        self._generate_report(config)
        
    def _generate_compliance_report(self, framework: str = None):
        """Generate compliance assessment report."""
        self.console.print("\n[bold green]Generating Compliance Report[/]")
        
        if not framework:
            framework = Prompt.ask(
                "[cyan]Compliance framework[/]",
                choices=["iso27001", "nist", "pci_dss", "owasp", "cis", "sox"],
                default="iso27001"
            )
            
        # Framework-specific configuration
        config = {
            'report_type': 'compliance',
            'framework': framework,
            'include_gap_analysis': Confirm.ask("[cyan]Include gap analysis?[/]", default=True),
            'include_recommendations': Confirm.ask("[cyan]Include compliance recommendations?[/]", default=True),
            'maturity_assessment': Confirm.ask("[cyan]Include maturity assessment?[/]", default=True)
        }
        
        # Framework-specific options
        if framework == "pci_dss":
            config['merchant_level'] = Prompt.ask("[cyan]Merchant level", choices=["1", "2", "3", "4"], default="1")
        elif framework == "iso27001":
            config['certification_scope'] = Prompt.ask("[cyan]Certification scope", default="Organization-wide")
        elif framework == "nist":
            config['nist_profile'] = Prompt.ask("[cyan]NIST profile", choices=["low", "moderate", "high"], default="moderate")
            
        self._generate_report(config)
        
    def _generate_custom_report(self, template: str = None):
        """Generate report from custom template."""
        self.console.print("\n[bold green]Generating Custom Report[/]")
        
        # List available templates
        templates = self.template_manager.list_templates()
        
        if not templates:
            self.console.print("[red]No custom templates available.[/]")
            if Confirm.ask("[cyan]Create a new template?[/]"):
                self._create_template()
            return
            
        if not template:
            self.console.print("\n[bold yellow]Available Templates:[/]")
            for i, tmpl in enumerate(templates, 1):
                self.console.print(f"[yellow]{i}[/] - {tmpl['name']} ({tmpl['description']})")
                
            choice = IntPrompt.ask(f"[cyan]Select template[/] (1-{len(templates)})", default=1)
            template = templates[choice - 1]['name']
            
        # Template configuration
        template_info = self.template_manager.get_template(template)
        config = {
            'report_type': 'custom',
            'template': template,
            'template_info': template_info
        }
        
        # Template-specific configuration
        if template_info.get('configurable_sections'):
            config['enabled_sections'] = []
            for section in template_info['configurable_sections']:
                if Confirm.ask(f"[cyan]Include {section} section?[/]", default=True):
                    config['enabled_sections'].append(section)
                    
        self._generate_report(config)
        
    def _generate_report(self, config: Dict[str, Any]):
        """Generate report with given configuration."""
        report_type = config['report_type']
        
        self.console.print(f"\n[green]Generating {report_type} report...[/]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            
            # Data analysis phase
            task1 = progress.add_task("Analyzing data...", total=100)
            try:
                analyzed_data = self.data_analyzer.analyze_for_report(
                    self.available_data,
                    config,
                    progress_callback=lambda p: progress.update(task1, completed=p)
                )
                progress.update(task1, completed=100, description="Data analysis completed")
            except Exception as e:
                self.console.print(f"[red]Data analysis failed: {e}[/]")
                return
                
            # Report generation phase
            task2 = progress.add_task("Generating report content...", total=100)
            try:
                report_content = self.report_generator.generate_content(
                    analyzed_data,
                    config,
                    progress_callback=lambda p: progress.update(task2, completed=p)
                )
                progress.update(task2, completed=100, description="Content generation completed")
            except Exception as e:
                self.console.print(f"[red]Report generation failed: {e}[/]")
                return
                
            # Formatting phase
            task3 = progress.add_task("Formatting report...", total=100)
            try:
                formatted_report = self.report_generator.format_report(
                    report_content,
                    config,
                    progress_callback=lambda p: progress.update(task3, completed=p)
                )
                progress.update(task3, completed=100, description="Formatting completed")
            except Exception as e:
                self.console.print(f"[red]Report formatting failed: {e}[/]")
                return
                
        # Store generated report
        report_info = {
            'type': report_type,
            'config': config,
            'content': formatted_report,
            'timestamp': datetime.now(),
            'filename': f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        self.generated_reports.append(report_info)
        
        self._display_report_summary(report_info)
        
        # Export options
        if Confirm.ask("[cyan]Export report now?[/]"):
            self._export_single_report(report_info)
            
    def _display_report_summary(self, report_info: Dict[str, Any]):
        """Display report generation summary."""
        summary_table = Table(title="[bold green]Report Generation Summary[/]")
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="white")
        
        content = report_info['content']
        
        summary_table.add_row("Report Type", report_info['type'].title())
        summary_table.add_row("Generated", report_info['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
        summary_table.add_row("Sections", str(len(content.get('sections', []))))
        summary_table.add_row("Pages", str(content.get('page_count', 'N/A')))
        summary_table.add_row("Vulnerabilities", str(len(content.get('vulnerabilities', []))))
        summary_table.add_row("Findings", str(len(content.get('findings', []))))
        
        self.console.print(summary_table)
        
        # Show key metrics
        if content.get('metrics'):
            metrics_table = Table(title="Key Metrics")
            metrics_table.add_column("Metric", style="yellow")
            metrics_table.add_column("Value", style="bold")
            
            metrics = content['metrics']
            if 'risk_score' in metrics:
                risk_color = "red" if metrics['risk_score'] > 7 else "yellow" if metrics['risk_score'] > 4 else "green"
                metrics_table.add_row("Overall Risk Score", f"[{risk_color}]{metrics['risk_score']}/10[/]")
                
            if 'vulnerability_count' in metrics:
                metrics_table.add_row("Total Vulnerabilities", str(metrics['vulnerability_count']))
                
            if 'critical_count' in metrics:
                metrics_table.add_row("Critical Issues", f"[red]{metrics['critical_count']}[/]")
                
            if 'high_count' in metrics:
                metrics_table.add_row("High Issues", f"[orange3]{metrics['high_count']}[/]")
                
            self.console.print(metrics_table)
            
    def _list_reports(self):
        """List all generated reports."""
        if not self.generated_reports:
            self.console.print("[yellow]No reports have been generated yet.[/]")
            return
            
        reports_table = Table(title="[bold blue]Generated Reports[/]")
        reports_table.add_column("ID", style="yellow")
        reports_table.add_column("Type", style="green")
        reports_table.add_column("Generated", style="cyan")
        reports_table.add_column("Filename", style="white")
        reports_table.add_column("Status", style="bold")
        
        for i, report in enumerate(self.generated_reports, 1):
            reports_table.add_row(
                str(i),
                report['type'].title(),
                report['timestamp'].strftime("%Y-%m-%d %H:%M"),
                report['filename'],
                "[green]Ready[/]"
            )
            
        self.console.print(reports_table)
        
        # Report actions
        if Confirm.ask("[cyan]Perform action on a report?[/]"):
            report_id = IntPrompt.ask(f"[cyan]Select report ID[/] (1-{len(self.generated_reports)})")
            if 1 <= report_id <= len(self.generated_reports):
                self._report_actions(self.generated_reports[report_id - 1])
                
    def _report_actions(self, report_info: Dict[str, Any]):
        """Perform actions on a specific report."""
        actions = {
            "1": ("view", "View report summary"),
            "2": ("export", "Export report"),
            "3": ("edit", "Edit report configuration"),
            "4": ("regenerate", "Regenerate report"),
            "5": ("delete", "Delete report")
        }
        
        self.console.print("\n[bold yellow]Report Actions:[/]")
        for key, (action_id, desc) in actions.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        choice = Prompt.ask("[cyan]Select action[/]", choices=list(actions.keys()), default="1")
        action = actions[choice][0]
        
        if action == "view":
            self._display_report_summary(report_info)
        elif action == "export":
            self._export_single_report(report_info)
        elif action == "edit":
            self.console.print("[yellow]Report editing not yet implemented[/]")
        elif action == "regenerate":
            self._generate_report(report_info['config'])
        elif action == "delete":
            if Confirm.ask(f"[red]Delete {report_info['type']} report?[/]"):
                self.generated_reports.remove(report_info)
                self.console.print("[green]Report deleted[/]")
                
    def _manage_templates(self):
        """Manage report templates."""
        self.console.print("\n[bold blue]Report Template Management[/]")
        
        template_actions = {
            "1": ("list", "List available templates"),
            "2": ("create", "Create new template"),
            "3": ("edit", "Edit existing template"),
            "4": ("delete", "Delete template"),
            "5": ("import", "Import template"),
            "6": ("export", "Export template")
        }
        
        self.console.print("\n[bold yellow]Template Actions:[/]")
        for key, (action_id, desc) in template_actions.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        choice = Prompt.ask("[cyan]Select action[/]", choices=list(template_actions.keys()), default="1")
        action = template_actions[choice][0]
        
        if action == "list":
            self._list_templates()
        elif action == "create":
            self._create_template()
        elif action == "edit":
            self._edit_template()
        elif action == "delete":
            self._delete_template()
        elif action == "import":
            self._import_template()
        elif action == "export":
            self._export_template()
            
    def _list_templates(self):
        """List available report templates."""
        templates = self.template_manager.list_templates()
        
        if not templates:
            self.console.print("[yellow]No templates available.[/]")
            return
            
        templates_table = Table(title="Available Templates")
        templates_table.add_column("Name", style="green")
        templates_table.add_column("Type", style="cyan")
        templates_table.add_column("Description", style="white")
        templates_table.add_column("Created", style="dim")
        
        for template in templates:
            templates_table.add_row(
                template['name'],
                template.get('type', 'Custom'),
                template.get('description', 'No description'),
                template.get('created_date', 'Unknown')
            )
            
        self.console.print(templates_table)
        
    def _create_template(self):
        """Create new report template."""
        self.console.print("\n[green]Creating New Report Template[/]")
        
        template_config = {
            'name': Prompt.ask("[cyan]Template name"),
            'description': Prompt.ask("[cyan]Template description"),
            'type': Prompt.ask("[cyan]Template type", choices=["executive", "technical", "vulnerability", "compliance", "custom"], default="custom"),
            'sections': []
        }
        
        # Define sections
        self.console.print("\n[yellow]Define template sections (press Enter when done):[/]")
        while True:
            section_name = Prompt.ask("[cyan]Section name (or Enter to finish)", default="")
            if not section_name:
                break
            template_config['sections'].append({
                'name': section_name,
                'required': Confirm.ask(f"[cyan]Is '{section_name}' required?[/]", default=True),
                'order': len(template_config['sections']) + 1
            })
            
        try:
            self.template_manager.create_template(template_config)
            self.console.print(f"[green]Template '{template_config['name']}' created successfully[/]")
        except Exception as e:
            self.console.print(f"[red]Template creation failed: {e}[/]")
            
    def _edit_template(self):
        """Edit existing template."""
        self.console.print("[yellow]Template editing not yet implemented[/]")
        
    def _delete_template(self):
        """Delete template."""
        templates = self.template_manager.list_templates()
        if not templates:
            self.console.print("[yellow]No templates to delete.[/]")
            return
            
        self._list_templates()
        template_name = Prompt.ask("[cyan]Enter template name to delete")
        
        if Confirm.ask(f"[red]Delete template '{template_name}'?[/]"):
            try:
                self.template_manager.delete_template(template_name)
                self.console.print(f"[green]Template '{template_name}' deleted[/]")
            except Exception as e:
                self.console.print(f"[red]Template deletion failed: {e}[/]")
                
    def _import_template(self):
        """Import template from file."""
        template_file = Prompt.ask("[cyan]Template file path")
        
        try:
            self.template_manager.import_template(template_file)
            self.console.print(f"[green]Template imported successfully[/]")
        except Exception as e:
            self.console.print(f"[red]Template import failed: {e}[/]")
            
    def _export_template(self):
        """Export template to file."""
        templates = self.template_manager.list_templates()
        if not templates:
            self.console.print("[yellow]No templates to export.[/]")
            return
            
        self._list_templates()
        template_name = Prompt.ask("[cyan]Enter template name to export")
        output_file = Prompt.ask("[cyan]Output file path", default=f"{template_name}_template.json")
        
        try:
            self.template_manager.export_template(template_name, output_file)
            self.console.print(f"[green]Template exported to {output_file}[/]")
        except Exception as e:
            self.console.print(f"[red]Template export failed: {e}[/]")
            
    def _analyze_data(self):
        """Perform interactive data analysis."""
        self.console.print("\n[bold blue]Data Analysis[/]")
        
        if not self.available_data:
            self.console.print("[red]No data available for analysis.[/]")
            return
            
        analysis_options = {
            "1": ("vulnerability_analysis", "Vulnerability trend analysis"),
            "2": ("risk_assessment", "Risk assessment and scoring"),
            "3": ("host_analysis", "Host-based analysis"),
            "4": ("service_analysis", "Service and port analysis"),
            "5": ("timeline_analysis", "Timeline analysis"),
            "6": ("comparison_analysis", "Comparison with previous assessments")
        }
        
        self.console.print("\n[bold yellow]Analysis Options:[/]")
        for key, (analysis_id, desc) in analysis_options.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        choice = Prompt.ask("[cyan]Select analysis[/]", choices=list(analysis_options.keys()), default="1")
        analysis_type = analysis_options[choice][0]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Performing analysis...", total=100)
            
            try:
                results = self.data_analyzer.perform_analysis(
                    self.available_data,
                    analysis_type,
                    progress_callback=lambda p: progress.update(task, completed=p)
                )
                progress.update(task, completed=100, description="Analysis completed")
                
            except Exception as e:
                self.console.print(f"[red]Analysis failed: {e}[/]")
                return
                
        self._display_analysis_results(results, analysis_type)
        
    def _display_analysis_results(self, results: Dict[str, Any], analysis_type: str):
        """Display data analysis results."""
        self.console.print(f"\n[bold green]{analysis_type.replace('_', ' ').title()} Results[/]")
        
        if analysis_type == "vulnerability_analysis":
            self._display_vulnerability_analysis(results)
        elif analysis_type == "risk_assessment":
            self._display_risk_assessment(results)
        elif analysis_type == "host_analysis":
            self._display_host_analysis(results)
        else:
            # Generic display
            for key, value in results.items():
                if isinstance(value, (int, float)):
                    self.console.print(f"[cyan]{key.replace('_', ' ').title()}:[/] {value}")
                elif isinstance(value, list):
                    self.console.print(f"[cyan]{key.replace('_', ' ').title()}:[/] {len(value)} items")
                    
    def _display_vulnerability_analysis(self, results: Dict[str, Any]):
        """Display vulnerability analysis results."""
        if 'severity_distribution' in results:
            severity_table = Table(title="Vulnerability Severity Distribution")
            severity_table.add_column("Severity", style="bold")
            severity_table.add_column("Count", style="yellow")
            severity_table.add_column("Percentage", style="cyan")
            
            total = sum(results['severity_distribution'].values())
            for severity, count in results['severity_distribution'].items():
                percentage = (count / total * 100) if total > 0 else 0
                severity_table.add_row(severity.title(), str(count), f"{percentage:.1f}%")
                
            self.console.print(severity_table)
            
        if 'top_vulnerabilities' in results:
            top_vulns_table = Table(title="Top Vulnerabilities")
            top_vulns_table.add_column("Vulnerability", style="red")
            top_vulns_table.add_column("Count", style="yellow")
            top_vulns_table.add_column("Severity", style="bold")
            
            for vuln in results['top_vulnerabilities'][:10]:
                top_vulns_table.add_row(
                    vuln['name'][:50] + "..." if len(vuln['name']) > 50 else vuln['name'],
                    str(vuln['count']),
                    vuln['severity'].upper()
                )
                
            self.console.print(top_vulns_table)
            
    def _display_risk_assessment(self, results: Dict[str, Any]):
        """Display risk assessment results."""
        if 'overall_risk_score' in results:
            risk_score = results['overall_risk_score']
            risk_color = "red" if risk_score > 7 else "yellow" if risk_score > 4 else "green"
            self.console.print(f"[bold]Overall Risk Score: [{risk_color}]{risk_score:.1f}/10[/]")
            
        if 'risk_categories' in results:
            risk_table = Table(title="Risk Categories")
            risk_table.add_column("Category", style="cyan")
            risk_table.add_column("Risk Level", style="bold")
            risk_table.add_column("Score", style="yellow")
            
            for category, data in results['risk_categories'].items():
                level = data['level']
                score = data['score']
                level_color = "red" if level == "High" else "yellow" if level == "Medium" else "green"
                risk_table.add_row(category.title(), f"[{level_color}]{level}[/]", f"{score:.1f}")
                
            self.console.print(risk_table)
            
    def _display_host_analysis(self, results: Dict[str, Any]):
        """Display host analysis results."""
        if 'host_summary' in results:
            host_table = Table(title="Host Summary")
            host_table.add_column("Host", style="cyan")
            host_table.add_column("Vulnerabilities", style="red")
            host_table.add_column("Risk Score", style="yellow")
            host_table.add_column("Status", style="bold")
            
            for host_data in results['host_summary'][:20]:  # Show top 20
                risk_color = "red" if host_data['risk_score'] > 7 else "yellow" if host_data['risk_score'] > 4 else "green"
                host_table.add_row(
                    host_data['host'],
                    str(host_data['vulnerability_count']),
                    f"[{risk_color}]{host_data['risk_score']:.1f}[/]",
                    host_data['status']
                )
                
            self.console.print(host_table)
            
    def _export_reports(self):
        """Export generated reports."""
        if not self.generated_reports:
            self.console.print("[yellow]No reports to export.[/]")
            return
            
        self.console.print("\n[bold blue]Export Reports[/]")
        
        # Export format selection
        export_formats = {
            "1": ("pdf", "PDF Document"),
            "2": ("html", "HTML Report"),
            "3": ("docx", "Word Document"),
            "4": ("xlsx", "Excel Spreadsheet"),
            "5": ("json", "JSON Data"),
            "6": ("all", "All Formats")
        }
        
        self.console.print("\n[bold yellow]Export Formats:[/]")
        for key, (format_id, desc) in export_formats.items():
            self.console.print(f"[yellow]{key}[/] - {desc}")
            
        format_choice = Prompt.ask("[cyan]Select export format[/]", choices=list(export_formats.keys()), default="1")
        export_format = export_formats[format_choice][0]
        
        # Report selection
        export_all = Confirm.ask("[cyan]Export all reports?[/]", default=True)
        
        if export_all:
            reports_to_export = self.generated_reports
        else:
            self._list_reports()
            report_ids = Prompt.ask("[cyan]Enter report IDs to export (comma-separated)")
            try:
                ids = [int(x.strip()) for x in report_ids.split(',')]
                reports_to_export = [self.generated_reports[i-1] for i in ids if 1 <= i <= len(self.generated_reports)]
            except ValueError:
                self.console.print("[red]Invalid report IDs[/]")
                return
                
        # Export process
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:
            
            export_task = progress.add_task("Exporting reports...", total=len(reports_to_export))
            
            exported_files = []
            for report in reports_to_export:
                try:
                    if export_format == "all":
                        for fmt in ["pdf", "html", "docx", "json"]:
                            output_file = self.export_manager.export_report(report, fmt)
                            exported_files.append(output_file)
                    else:
                        output_file = self.export_manager.export_report(report, export_format)
                        exported_files.append(output_file)
                        
                    progress.advance(export_task)
                    
                except Exception as e:
                    self.console.print(f"[red]Export failed for {report['filename']}: {e}[/]")
                    
        self.console.print(f"\n[green]Exported {len(exported_files)} files:[/]")
        for file_path in exported_files:
            self.console.print(f"  [cyan]{file_path}[/]")
            
    def _export_single_report(self, report_info: Dict[str, Any]):
        """Export a single report."""
        export_format = Prompt.ask(
            "[cyan]Export format[/]",
            choices=["pdf", "html", "docx", "xlsx", "json"],
            default="pdf"
        )
        
        try:
            output_file = self.export_manager.export_report(report_info, export_format)
            self.console.print(f"[green]Report exported to: {output_file}[/]")
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/]")
            
    def _load_sample_data(self) -> Dict[str, Any]:
        """Load sample data for demonstration purposes."""
        return {
            'vulnerabilities': [
                {
                    'title': 'SQL Injection',
                    'severity': 'high',
                    'cvss': 8.2,
                    'host': '192.168.1.100',
                    'port': 80,
                    'description': 'SQL injection vulnerability in login form'
                },
                {
                    'title': 'Cross-Site Scripting',
                    'severity': 'medium',
                    'cvss': 6.1,
                    'host': '192.168.1.100',
                    'port': 80,
                    'description': 'Reflected XSS in search parameter'
                }
            ],
            'hosts': [
                {'ip': '192.168.1.100', 'os': 'Windows Server 2019', 'status': 'up'},
                {'ip': '192.168.1.101', 'os': 'Ubuntu 20.04', 'status': 'up'}
            ],
            'ports': [
                {'host': '192.168.1.100', 'port': 80, 'service': 'http', 'state': 'open'},
                {'host': '192.168.1.100', 'port': 443, 'service': 'https', 'state': 'open'}
            ]
        }
        
    def _show_help(self):
        """Display help information."""
        help_text = """
[bold blue]Reporting Module Help[/]

[bold yellow]Available Commands:[/]
  report executive             - Generate executive summary report
  report technical             - Generate detailed technical report
  report vulnerability         - Generate vulnerability-focused report
  report compliance <framework> - Generate compliance assessment report
  report custom [template]     - Generate custom report from template
  report list                  - List generated reports
  report templates             - Manage report templates

[bold yellow]Interactive Mode:[/]
  Run 'report' without arguments to enter interactive mode

[bold yellow]Examples:[/]
  report executive
  report technical
  report vulnerability
  report compliance iso27001
  report custom penetration_test

[bold yellow]Export Formats:[/]
  PDF, HTML, Word (DOCX), Excel (XLSX), JSON
"""
        
        self.console.print(Panel(help_text, title="Help", border_style="blue"))


if __name__ == "__main__":
    import sys
    report_cli = ReportCLI()
    report_cli.run(sys.argv[1:] if len(sys.argv) > 1 else [])