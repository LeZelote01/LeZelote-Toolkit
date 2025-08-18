#!/usr/bin/env python3
"""
Real-time Dashboard for Pentest-USB Toolkit
===========================================

Provides real-time monitoring of system metrics, scan progress,
threat levels, and operational status.
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
from rich import box
from rich.align import Align

class Dashboard:
    """Real-time dashboard for monitoring toolkit operations."""
    
    def __init__(self):
        """Initialize the dashboard with default metrics."""
        self.console = Console()
        
        # System metrics
        self.system_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_usage': 0.0,
            'network_sent': 0,
            'network_recv': 0,
            'boot_time': psutil.boot_time(),
            'processes': 0
        }
        
        # Scan progress tracking
        self.scan_progress = {
            'current_scans': [],
            'completed_scans': 0,
            'failed_scans': 0,
            'total_targets': 0,
            'vulnerabilities_found': 0
        }
        
        # Threat level indicators
        self.threat_levels = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        # Activity log
        self.activity_log = []
        self.max_log_entries = 10
        
        # Update thread
        self._update_thread = None
        self._stop_updates = False
        
    def create_layout(self) -> Layout:
        """Create the main dashboard layout."""
        layout = Layout()
        
        # Split main layout
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into columns
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Split left column
        layout["left"].split_column(
            Layout(name="system", ratio=1),
            Layout(name="scans", ratio=1)
        )
        
        # Split right column
        layout["right"].split_column(
            Layout(name="threats", ratio=1),
            Layout(name="activity", ratio=1)
        )
        
        # Add content to layouts
        layout["header"].update(self._create_header())
        layout["system"].update(self._create_system_panel())
        layout["scans"].update(self._create_scan_panel())
        layout["threats"].update(self._create_threat_panel())
        layout["activity"].update(self._create_activity_panel())
        layout["footer"].update(self._create_footer())
        
        return layout
        
    def _create_header(self) -> Panel:
        """Create the header panel with title and timestamp."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header_text = Text()
        header_text.append("🛡️  ", style="bold red")
        header_text.append("PENTEST-USB TOOLKIT", style="bold cyan")
        header_text.append(" - REAL-TIME DASHBOARD", style="bold white")
        header_text.append(f"  📅 {current_time}", style="dim white")
        
        return Panel(
            Align.center(header_text),
            style="bold green",
            box=box.DOUBLE_EDGE
        )
        
    def _create_system_panel(self) -> Panel:
        """Create system metrics panel."""
        table = Table.grid(padding=1)
        table.add_column(style="cyan", justify="right")
        table.add_column(style="white")
        table.add_column(style="yellow")
        
        # CPU usage with color coding
        cpu_color = self._get_metric_color(self.system_metrics['cpu_percent'], 70, 90)
        table.add_row("CPU:", f"{self.system_metrics['cpu_percent']:.1f}%", f"[{cpu_color}]{'█' * int(self.system_metrics['cpu_percent'] / 5)}[/]")
        
        # Memory usage with color coding
        mem_color = self._get_metric_color(self.system_metrics['memory_percent'], 80, 90)
        table.add_row("Memory:", f"{self.system_metrics['memory_percent']:.1f}%", f"[{mem_color}]{'█' * int(self.system_metrics['memory_percent'] / 5)}[/]")
        
        # Disk usage
        disk_color = self._get_metric_color(self.system_metrics['disk_usage'], 85, 95)
        table.add_row("Disk:", f"{self.system_metrics['disk_usage']:.1f}%", f"[{disk_color}]{'█' * int(self.system_metrics['disk_usage'] / 5)}[/]")
        
        # Network stats
        table.add_row("Network TX:", self._format_bytes(self.system_metrics['network_sent']), "")
        table.add_row("Network RX:", self._format_bytes(self.system_metrics['network_recv']), "")
        
        # Processes
        table.add_row("Processes:", str(self.system_metrics['processes']), "")
        
        # Uptime
        uptime = datetime.now() - datetime.fromtimestamp(self.system_metrics['boot_time'])
        table.add_row("Uptime:", str(uptime).split('.')[0], "")
        
        return Panel(
            table,
            title="[bold cyan]System Metrics[/]",
            border_style="blue",
            box=box.ROUNDED
        )
        
    def _create_scan_panel(self) -> Panel:
        """Create scan progress panel."""
        table = Table.grid(padding=1)
        table.add_column(style="green", justify="right")
        table.add_column(style="white")
        
        table.add_row("Active Scans:", str(len(self.scan_progress['current_scans'])))
        table.add_row("Completed:", str(self.scan_progress['completed_scans']))
        table.add_row("Failed:", str(self.scan_progress['failed_scans']))
        table.add_row("Total Targets:", str(self.scan_progress['total_targets']))
        table.add_row("Vulnerabilities:", str(self.scan_progress['vulnerabilities_found']))
        
        # Show active scans
        if self.scan_progress['current_scans']:
            table.add_row("", "")
            table.add_row("[bold yellow]Current Scans:[/]", "")
            for scan in self.scan_progress['current_scans'][:3]:  # Show max 3
                table.add_row("  →", f"{scan['target']} ({scan['type']})")
                
        return Panel(
            table,
            title="[bold green]Scan Progress[/]",
            border_style="green",
            box=box.ROUNDED
        )
        
    def _create_threat_panel(self) -> Panel:
        """Create threat level indicators panel."""
        table = Table.grid(padding=1)
        table.add_column(style="white", justify="right", width=10)
        table.add_column(style="white")
        table.add_column(style="white")
        
        # Threat level indicators with colors
        threat_data = [
            ("Critical:", self.threat_levels['critical'], "red"),
            ("High:", self.threat_levels['high'], "orange3"),
            ("Medium:", self.threat_levels['medium'], "yellow"),
            ("Low:", self.threat_levels['low'], "green"),
            ("Info:", self.threat_levels['info'], "blue")
        ]
        
        for label, count, color in threat_data:
            bars = "█" * min(count, 15)  # Max 15 bars
            table.add_row(
                label,
                str(count),
                f"[{color}]{bars}[/]"
            )
            
        # Calculate total and risk score
        total_threats = sum(self.threat_levels.values())
        risk_score = (
            self.threat_levels['critical'] * 10 +
            self.threat_levels['high'] * 7 +
            self.threat_levels['medium'] * 4 +
            self.threat_levels['low'] * 2 +
            self.threat_levels['info'] * 1
        )
        
        table.add_row("", "", "")
        table.add_row("Total:", str(total_threats), "")
        
        risk_color = "green"
        if risk_score > 50:
            risk_color = "red"
        elif risk_score > 20:
            risk_color = "yellow"
            
        table.add_row("Risk Score:", f"[{risk_color}]{risk_score}[/]", "")
        
        return Panel(
            table,
            title="[bold red]Threat Levels[/]",
            border_style="red",
            box=box.ROUNDED
        )
        
    def _create_activity_panel(self) -> Panel:
        """Create activity log panel."""
        if not self.activity_log:
            content = Text("No recent activity", style="dim")
        else:
            content = "\n".join([
                f"[dim]{entry['time']}[/] {entry['message']}"
                for entry in self.activity_log[-self.max_log_entries:]
            ])
            
        return Panel(
            content,
            title="[bold magenta]Recent Activity[/]",
            border_style="magenta",
            box=box.ROUNDED
        )
        
    def _create_footer(self) -> Panel:
        """Create footer with controls and status."""
        footer_text = Text()
        footer_text.append("Press ", style="dim")
        footer_text.append("Ctrl+C", style="bold yellow")
        footer_text.append(" to exit dashboard | ", style="dim")
        footer_text.append("F5", style="bold yellow")
        footer_text.append(" refresh | ", style="dim")
        footer_text.append("h", style="bold yellow")
        footer_text.append(" help", style="dim")
        
        return Panel(
            Align.center(footer_text),
            style="dim"
        )
        
    def update_system_metrics(self):
        """Update system metrics from psutil."""
        try:
            self.system_metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
            self.system_metrics['memory_percent'] = psutil.virtual_memory().percent
            self.system_metrics['disk_usage'] = psutil.disk_usage('/').percent
            
            # Network stats
            net_io = psutil.net_io_counters()
            self.system_metrics['network_sent'] = net_io.bytes_sent
            self.system_metrics['network_recv'] = net_io.bytes_recv
            
            # Process count
            self.system_metrics['processes'] = len(psutil.pids())
            
        except Exception as e:
            self._log_activity(f"Error updating system metrics: {e}", "error")
            
    def update_scan_progress(self, scan_data: Optional[Dict[str, Any]] = None):
        """Update scan progress information."""
        if scan_data:
            # Update with provided data
            if scan_data.get('action') == 'start':
                self.scan_progress['current_scans'].append({
                    'target': scan_data.get('target', 'Unknown'),
                    'type': scan_data.get('type', 'Unknown'),
                    'start_time': datetime.now()
                })
                self._log_activity(f"Started scan: {scan_data.get('target')}")
                
            elif scan_data.get('action') == 'complete':
                target = scan_data.get('target')
                self.scan_progress['current_scans'] = [
                    s for s in self.scan_progress['current_scans']
                    if s['target'] != target
                ]
                self.scan_progress['completed_scans'] += 1
                vuln_count = scan_data.get('vulnerabilities', 0)
                self.scan_progress['vulnerabilities_found'] += vuln_count
                self._log_activity(f"Completed scan: {target} ({vuln_count} vulns)")
                
            elif scan_data.get('action') == 'fail':
                target = scan_data.get('target')
                self.scan_progress['current_scans'] = [
                    s for s in self.scan_progress['current_scans']
                    if s['target'] != target
                ]
                self.scan_progress['failed_scans'] += 1
                self._log_activity(f"Failed scan: {target}", "error")
                
    def update_threat_levels(self, threat_data: Optional[Dict[str, int]] = None):
        """Update threat level indicators."""
        if threat_data:
            for level, count in threat_data.items():
                if level in self.threat_levels:
                    self.threat_levels[level] += count
                    
    def add_vulnerability(self, severity: str, description: str):
        """Add a new vulnerability to threat levels."""
        if severity.lower() in self.threat_levels:
            self.threat_levels[severity.lower()] += 1
            self._log_activity(f"New {severity} vulnerability: {description}")
            
    def _log_activity(self, message: str, level: str = "info"):
        """Add an entry to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Style message based on level
        if level == "error":
            styled_message = f"[red]❌ {message}[/]"
        elif level == "warning":
            styled_message = f"[yellow]⚠️  {message}[/]"
        elif level == "success":
            styled_message = f"[green]✅ {message}[/]"
        else:
            styled_message = f"[blue]ℹ️  {message}[/]"
            
        entry = {
            'time': timestamp,
            'message': styled_message,
            'level': level
        }
        
        self.activity_log.append(entry)
        
        # Keep only recent entries
        if len(self.activity_log) > self.max_log_entries * 2:
            self.activity_log = self.activity_log[-self.max_log_entries:]
            
    def _get_metric_color(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Get color for metric based on thresholds."""
        if value >= critical_threshold:
            return "red"
        elif value >= warning_threshold:
            return "yellow"
        else:
            return "green"
            
    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"
        
    def start_auto_update(self, interval: float = 1.0):
        """Start automatic updates in background thread."""
        if self._update_thread and self._update_thread.is_alive():
            return
            
        self._stop_updates = False
        self._update_thread = threading.Thread(target=self._auto_update_loop, args=(interval,))
        self._update_thread.daemon = True
        self._update_thread.start()
        
    def stop_auto_update(self):
        """Stop automatic updates."""
        self._stop_updates = True
        if self._update_thread:
            self._update_thread.join(timeout=2.0)
            
    def _auto_update_loop(self, interval: float):
        """Auto-update loop running in background."""
        while not self._stop_updates:
            try:
                self.update_system_metrics()
                time.sleep(interval)
            except Exception as e:
                self._log_activity(f"Auto-update error: {e}", "error")
                time.sleep(interval * 2)  # Wait longer on error
                
    def reset_metrics(self):
        """Reset all metrics to default values."""
        self.scan_progress = {
            'current_scans': [],
            'completed_scans': 0,
            'failed_scans': 0,
            'total_targets': 0,
            'vulnerabilities_found': 0
        }
        
        self.threat_levels = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        self.activity_log = []
        self._log_activity("Dashboard metrics reset", "info")


# Example usage and testing
if __name__ == "__main__":
    dashboard = Dashboard()
    
    # Simulate some data
    dashboard.update_scan_progress({
        'action': 'start',
        'target': '192.168.1.100',
        'type': 'network'
    })
    
    dashboard.add_vulnerability('high', 'SQL Injection detected')
    dashboard.add_vulnerability('medium', 'XSS vulnerability found')
    
    # Show dashboard
    console = Console()
    try:
        with Live(dashboard.create_layout(), refresh_per_second=2, screen=True) as live:
            dashboard.start_auto_update()
            
            while True:
                live.update(dashboard.create_layout())
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        dashboard.stop_auto_update()
        console.print("\n[yellow]Dashboard closed.[/]")