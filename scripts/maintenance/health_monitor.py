#!/usr/bin/env python3
"""
LeZelote-Toolkit - Health Monitoring System
========================================

This script provides continuous health monitoring for the
Pentest-USB Toolkit, including:
- Real-time system resource monitoring
- Service availability checking
- Performance trend analysis
- Alert generation and notifications
- Health metrics collection
- Automatic remediation triggers

Author: LeZelote Toolkit Team
Version: 1.0.0
"""

import os
import sys
import time
import json
import sqlite3
import threading
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import logging
import argparse
import signal

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.utils.logging_handler import setup_logging
from core.utils.network_utils import check_network_connectivity

class HealthMonitor:
    """Continuous health monitoring system."""
    
    def __init__(self, config_file: str = None):
        """Initialize the health monitor."""
        self.logger = setup_logging(__name__)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Monitoring configuration
        self.config = {
            'monitoring_interval': 30,  # seconds
            'data_retention_days': 7,
            'alert_thresholds': {
                'cpu_warning': 80.0,
                'cpu_critical': 95.0,
                'memory_warning': 80.0,
                'memory_critical': 95.0,
                'disk_warning': 85.0,
                'disk_critical': 95.0,
                'response_time_warning': 5.0,
                'response_time_critical': 10.0
            },
            'services_to_monitor': [
                'toolkit_core',
                'database_service',
                'web_interface'
            ],
            'network_tests': [
                ('google.com', 80),
                ('github.com', 443)
            ]
        }
        
        # Runtime state
        self.running = False
        self.monitor_thread = None
        self.metrics_db_path = os.path.join(self.project_root, 'logs', 'health_metrics.db')
        self.alert_callbacks = []
        self.last_alerts = {}
        
        # Initialize metrics database
        self._init_metrics_database()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.running:
            self.logger.warning("Health monitoring is already running")
            return
        
        self.logger.info("Starting health monitoring...")
        self.running = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop health monitoring."""
        if not self.running:
            return
        
        self.logger.info("Stopping health monitoring...")
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Health monitoring stopped")
    
    def add_alert_callback(self, callback: Callable[[Dict], None]):
        """Add callback function for alerts."""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Dict:
        """Get current system metrics."""
        return self._collect_metrics()
    
    def get_historical_metrics(self, hours: int = 24) -> List[Dict]:
        """Get historical metrics from database."""
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                
                since_time = datetime.now() - timedelta(hours=hours)
                cursor.execute("""
                    SELECT timestamp, metrics_json FROM health_metrics 
                    WHERE timestamp > ? ORDER BY timestamp DESC
                """, (since_time.isoformat(),))
                
                results = []
                for row in cursor.fetchall():
                    timestamp, metrics_json = row
                    metrics = json.loads(metrics_json)
                    metrics['timestamp'] = timestamp
                    results.append(metrics)
                
                return results
        
        except Exception as e:
            self.logger.error(f"Failed to retrieve historical metrics: {e}")
            return []
    
    def get_health_summary(self) -> Dict:
        """Get overall health summary."""
        current_metrics = self._collect_metrics()
        historical_metrics = self.get_historical_metrics(1)  # Last hour
        
        summary = {
            'current_status': self._determine_overall_status(current_metrics),
            'current_metrics': current_metrics,
            'trends': self._calculate_trends(historical_metrics),
            'active_alerts': self._get_active_alerts(),
            'uptime': self._get_system_uptime(),
            'last_updated': datetime.now().isoformat()
        }
        
        return summary
    
    def generate_health_report(self, hours: int = 24) -> Dict:
        """Generate comprehensive health report."""
        self.logger.info(f"Generating health report for last {hours} hours...")
        
        historical_data = self.get_historical_metrics(hours)
        current_metrics = self._collect_metrics()
        
        report = {
            'report_period_hours': hours,
            'report_generated': datetime.now().isoformat(),
            'current_status': self._determine_overall_status(current_metrics),
            'metrics_summary': self._analyze_historical_data(historical_data),
            'alerts_summary': self._get_alerts_summary(hours),
            'performance_trends': self._calculate_performance_trends(historical_data),
            'recommendations': self._generate_recommendations(historical_data, current_metrics)
        }
        
        return report
    
    def cleanup_old_metrics(self, days: int = None):
        """Clean up old metrics data."""
        retention_days = days or self.config['data_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM health_metrics WHERE timestamp < ?", (cutoff_date.isoformat(),))
                deleted_count = cursor.rowcount
                
                cursor.execute("DELETE FROM health_alerts WHERE timestamp < ?", (cutoff_date.isoformat(),))
                deleted_alerts = cursor.rowcount
                
                # Vacuum database to reclaim space
                cursor.execute("VACUUM")
                
                self.logger.info(f"Cleaned up {deleted_count} old metrics and {deleted_alerts} old alerts")
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                
                # Store metrics
                self._store_metrics(metrics)
                
                # Check for alerts
                alerts = self._check_alerts(metrics)
                
                # Process alerts
                for alert in alerts:
                    self._process_alert(alert)
                
                # Clean up old data periodically
                if datetime.now().minute == 0:  # Every hour
                    self.cleanup_old_metrics()
                
                # Wait for next interval
                time.sleep(self.config['monitoring_interval'])
            
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Brief pause before retrying
    
    def _collect_metrics(self) -> Dict:
        """Collect current system metrics."""
        try:
            # System resource metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = psutil.disk_usage(self.project_root)
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            # Service availability
            services = self._check_services()
            
            # Network connectivity
            network_tests = self._test_network_connectivity()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_percent': (disk_usage.used / disk_usage.total) * 100,
                    'disk_free_gb': round(disk_usage.free / (1024**3), 2),
                    'process_count': process_count
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv,
                    'connectivity_tests': network_tests
                },
                'services': services,
                'toolkit': {
                    'project_root_size_gb': self._get_directory_size(self.project_root),
                    'log_files_count': len(list(Path(os.path.join(self.project_root, 'logs')).glob('*.log'))),
                    'database_accessible': self._check_database_access()
                }
            }
            
            return metrics
        
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {}
    
    def _store_metrics(self, metrics: Dict):
        """Store metrics in database."""
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO health_metrics (timestamp, metrics_json)
                    VALUES (?, ?)
                """, (metrics['timestamp'], json.dumps(metrics)))
        
        except Exception as e:
            self.logger.error(f"Failed to store metrics: {e}")
    
    def _check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check metrics against alert thresholds."""
        alerts = []
        thresholds = self.config['alert_thresholds']
        
        try:
            system_metrics = metrics.get('system', {})
            
            # CPU alerts
            cpu_percent = system_metrics.get('cpu_percent', 0)
            if cpu_percent >= thresholds['cpu_critical']:
                alerts.append({
                    'type': 'cpu',
                    'level': 'critical',
                    'message': f'CPU usage critically high: {cpu_percent:.1f}%',
                    'value': cpu_percent,
                    'threshold': thresholds['cpu_critical']
                })
            elif cpu_percent >= thresholds['cpu_warning']:
                alerts.append({
                    'type': 'cpu',
                    'level': 'warning',
                    'message': f'CPU usage high: {cpu_percent:.1f}%',
                    'value': cpu_percent,
                    'threshold': thresholds['cpu_warning']
                })
            
            # Memory alerts
            memory_percent = system_metrics.get('memory_percent', 0)
            if memory_percent >= thresholds['memory_critical']:
                alerts.append({
                    'type': 'memory',
                    'level': 'critical',
                    'message': f'Memory usage critically high: {memory_percent:.1f}%',
                    'value': memory_percent,
                    'threshold': thresholds['memory_critical']
                })
            elif memory_percent >= thresholds['memory_warning']:
                alerts.append({
                    'type': 'memory',
                    'level': 'warning',
                    'message': f'Memory usage high: {memory_percent:.1f}%',
                    'value': memory_percent,
                    'threshold': thresholds['memory_warning']
                })
            
            # Disk alerts
            disk_percent = system_metrics.get('disk_percent', 0)
            if disk_percent >= thresholds['disk_critical']:
                alerts.append({
                    'type': 'disk',
                    'level': 'critical',
                    'message': f'Disk usage critically high: {disk_percent:.1f}%',
                    'value': disk_percent,
                    'threshold': thresholds['disk_critical']
                })
            elif disk_percent >= thresholds['disk_warning']:
                alerts.append({
                    'type': 'disk',
                    'level': 'warning',
                    'message': f'Disk usage high: {disk_percent:.1f}%',
                    'value': disk_percent,
                    'threshold': thresholds['disk_warning']
                })
            
            # Service alerts
            services = metrics.get('services', {})
            for service_name, service_status in services.items():
                if service_status.get('status') == 'error':
                    alerts.append({
                        'type': 'service',
                        'level': 'critical',
                        'message': f'Service {service_name} is not responding',
                        'service': service_name,
                        'error': service_status.get('error', 'Unknown error')
                    })
                elif service_status.get('response_time', 0) >= thresholds['response_time_critical']:
                    alerts.append({
                        'type': 'performance',
                        'level': 'warning',
                        'message': f'Service {service_name} response time high: {service_status["response_time"]:.2f}s',
                        'service': service_name,
                        'value': service_status['response_time']
                    })
            
            # Add timestamp to all alerts
            for alert in alerts:
                alert['timestamp'] = datetime.now().isoformat()
        
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
        
        return alerts
    
    def _process_alert(self, alert: Dict):
        """Process and store an alert."""
        alert_key = f"{alert['type']}_{alert['level']}"
        
        # Check if this alert was recently sent (avoid spam)
        now = datetime.now()
        last_alert_time = self.last_alerts.get(alert_key)
        
        if last_alert_time:
            time_diff = now - last_alert_time
            if time_diff.total_seconds() < 300:  # 5 minutes cooldown
                return
        
        # Store alert in database
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO health_alerts (timestamp, alert_type, alert_level, message, alert_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (alert['timestamp'], alert['type'], alert['level'], alert['message'], json.dumps(alert)))
        
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
        
        # Send alert to callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
        
        # Log the alert
        log_level = logging.CRITICAL if alert['level'] == 'critical' else logging.WARNING
        self.logger.log(log_level, f"HEALTH ALERT: {alert['message']}")
        
        # Update last alert time
        self.last_alerts[alert_key] = now
    
    def _check_services(self) -> Dict:
        """Check status of monitored services."""
        services = {}
        
        for service_name in self.config['services_to_monitor']:
            start_time = time.time()
            
            try:
                if service_name == 'toolkit_core':
                    status = self._check_toolkit_core()
                elif service_name == 'database_service':
                    status = self._check_database_service()
                elif service_name == 'web_interface':
                    status = self._check_web_interface()
                else:
                    status = 'unknown'
                
                response_time = time.time() - start_time
                
                services[service_name] = {
                    'status': status,
                    'response_time': response_time,
                    'last_checked': datetime.now().isoformat()
                }
            
            except Exception as e:
                services[service_name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_checked': datetime.now().isoformat()
                }
        
        return services
    
    def _test_network_connectivity(self) -> Dict:
        """Test network connectivity to external services."""
        results = {}
        
        for host, port in self.config['network_tests']:
            start_time = time.time()
            
            try:
                is_connected = check_network_connectivity(host, port, timeout=5)
                response_time = time.time() - start_time
                
                results[f"{host}:{port}"] = {
                    'connected': is_connected,
                    'response_time': response_time
                }
            
            except Exception as e:
                results[f"{host}:{port}"] = {
                    'connected': False,
                    'error': str(e)
                }
        
        return results
    
    def _check_toolkit_core(self) -> str:
        """Check toolkit core module status."""
        try:
            # Try to import core modules
            sys.path.insert(0, self.project_root)
            import core
            return 'healthy'
        except Exception:
            return 'error'
    
    def _check_database_service(self) -> str:
        """Check database service status."""
        return 'healthy' if self._check_database_access() else 'error'
    
    def _check_web_interface(self) -> str:
        """Check web interface status."""
        try:
            web_app_path = os.path.join(self.project_root, 'interfaces', 'web', 'app.py')
            return 'healthy' if os.path.exists(web_app_path) else 'error'
        except Exception:
            return 'error'
    
    def _check_database_access(self) -> bool:
        """Check if database is accessible."""
        try:
            db_path = os.path.join(self.project_root, 'core', 'db', 'knowledge_base.db')
            if os.path.exists(db_path):
                with sqlite3.connect(db_path, timeout=5) as conn:
                    conn.execute('SELECT 1')
                return True
            return False
        except Exception:
            return False
    
    def _get_directory_size(self, directory: str) -> float:
        """Get directory size in GB."""
        try:
            total_size = sum(f.stat().st_size for f in Path(directory).rglob('*') if f.is_file())
            return round(total_size / (1024**3), 2)
        except Exception:
            return 0.0
    
    def _get_system_uptime(self) -> float:
        """Get system uptime in seconds."""
        try:
            return time.time() - psutil.boot_time()
        except Exception:
            return 0.0
    
    def _init_metrics_database(self):
        """Initialize the metrics database."""
        try:
            os.makedirs(os.path.dirname(self.metrics_db_path), exist_ok=True)
            
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                
                # Create metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS health_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metrics_json TEXT NOT NULL
                    )
                """)
                
                # Create alerts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS health_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        alert_level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        alert_json TEXT NOT NULL
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON health_metrics (timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON health_alerts (timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_type ON health_alerts (alert_type, alert_level)")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize metrics database: {e}")
    
    def _determine_overall_status(self, metrics: Dict) -> str:
        """Determine overall system health status."""
        if not metrics:
            return 'unknown'
        
        system = metrics.get('system', {})
        services = metrics.get('services', {})
        
        # Check for critical issues
        if (system.get('cpu_percent', 0) >= self.config['alert_thresholds']['cpu_critical'] or
            system.get('memory_percent', 0) >= self.config['alert_thresholds']['memory_critical'] or
            system.get('disk_percent', 0) >= self.config['alert_thresholds']['disk_critical']):
            return 'critical'
        
        # Check for service errors
        if any(service.get('status') == 'error' for service in services.values()):
            return 'degraded'
        
        # Check for warnings
        if (system.get('cpu_percent', 0) >= self.config['alert_thresholds']['cpu_warning'] or
            system.get('memory_percent', 0) >= self.config['alert_thresholds']['memory_warning'] or
            system.get('disk_percent', 0) >= self.config['alert_thresholds']['disk_warning']):
            return 'warning'
        
        return 'healthy'
    
    def _calculate_trends(self, historical_data: List[Dict]) -> Dict:
        """Calculate performance trends from historical data."""
        if len(historical_data) < 2:
            return {}
        
        # Sort by timestamp
        historical_data.sort(key=lambda x: x.get('timestamp', ''))
        
        trends = {}
        
        try:
            # CPU trend
            cpu_values = [item['system']['cpu_percent'] for item in historical_data if 'system' in item]
            if len(cpu_values) >= 2:
                trends['cpu'] = 'increasing' if cpu_values[-1] > cpu_values[0] else 'decreasing'
            
            # Memory trend
            memory_values = [item['system']['memory_percent'] for item in historical_data if 'system' in item]
            if len(memory_values) >= 2:
                trends['memory'] = 'increasing' if memory_values[-1] > memory_values[0] else 'decreasing'
            
            # Disk trend
            disk_values = [item['system']['disk_percent'] for item in historical_data if 'system' in item]
            if len(disk_values) >= 2:
                trends['disk'] = 'increasing' if disk_values[-1] > disk_values[0] else 'decreasing'
        
        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
        
        return trends
    
    def _get_active_alerts(self) -> List[Dict]:
        """Get currently active alerts."""
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                
                # Get alerts from last hour
                since_time = datetime.now() - timedelta(hours=1)
                cursor.execute("""
                    SELECT alert_json FROM health_alerts 
                    WHERE timestamp > ? ORDER BY timestamp DESC LIMIT 10
                """, (since_time.isoformat(),))
                
                alerts = []
                for (alert_json,) in cursor.fetchall():
                    alerts.append(json.loads(alert_json))
                
                return alerts
        
        except Exception as e:
            self.logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop_monitoring()
        sys.exit(0)

def console_alert_callback(alert: Dict):
    """Simple console alert callback."""
    print(f"ALERT [{alert['level'].upper()}]: {alert['message']}")

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='LeZelote Toolkit Health Monitor')
    parser.add_argument('action', choices=['start', 'status', 'report', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--daemon', action='store_true', 
                       help='Run as daemon (for start action)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Monitoring interval in seconds')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours of data for report/cleanup')
    parser.add_argument('--save-report', help='Save report to file')
    
    args = parser.parse_args()
    
    try:
        monitor = HealthMonitor()
        
        # Configure monitoring interval
        monitor.config['monitoring_interval'] = args.interval
        
        # Add console alert callback
        monitor.add_alert_callback(console_alert_callback)
        
        if args.action == 'start':
            monitor.start_monitoring()
            
            if args.daemon:
                # Keep running until signal
                try:
                    while monitor.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    monitor.stop_monitoring()
            else:
                # Run for a short time then exit
                print("Health monitoring started. Press Ctrl+C to stop.")
                try:
                    time.sleep(60)  # Run for 1 minute
                except KeyboardInterrupt:
                    pass
                monitor.stop_monitoring()
        
        elif args.action == 'status':
            summary = monitor.get_health_summary()
            print("\n=== HEALTH STATUS ===")
            print(f"Overall Status: {summary['current_status'].upper()}")
            print(f"CPU: {summary['current_metrics']['system']['cpu_percent']:.1f}%")
            print(f"Memory: {summary['current_metrics']['system']['memory_percent']:.1f}%")
            print(f"Disk: {summary['current_metrics']['system']['disk_percent']:.1f}%")
            
            if summary['active_alerts']:
                print(f"\nActive Alerts: {len(summary['active_alerts'])}")
                for alert in summary['active_alerts'][:5]:
                    print(f"  - [{alert['level'].upper()}] {alert['message']}")
        
        elif args.action == 'report':
            report = monitor.generate_health_report(args.hours)
            
            if args.save_report:
                with open(args.save_report, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Health report saved to: {args.save_report}")
            else:
                print(json.dumps(report, indent=2))
        
        elif args.action == 'cleanup':
            days = args.hours // 24
            monitor.cleanup_old_metrics(days)
            print(f"Cleaned up metrics older than {days} days")
    
    except Exception as e:
        print(f"Error during health monitoring: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()