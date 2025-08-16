#!/usr/bin/env python3
"""
API Routes for Pentest-USB Toolkit Web Interface
================================================

Handles RESTful API endpoints for data access and operations.
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging
import psutil
from .auth import require_auth, require_role

# Create blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/system/info')
@require_auth
def system_info():
    """Get system information."""
    try:
        info = {
            'hostname': 'pentest-usb',
            'platform': 'Linux',
            'architecture': 'x86_64',
            'python_version': '3.9.0',
            'toolkit_version': '1.0.0',
            'uptime': get_system_uptime(),
            'timezone': 'UTC'
        }
        
        return jsonify({'success': True, 'info': info})
        
    except Exception as e:
        logging.error(f"System info error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/system/resources')
@require_auth
def system_resources():
    """Get system resource usage."""
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        
        # Get network stats
        network = psutil.net_io_counters()
        
        resources = {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'per_core': psutil.cpu_percent(percpu=True)
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100
            },
            'network': {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({'success': True, 'resources': resources})
        
    except Exception as e:
        logging.error(f"System resources error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/system/processes')
@require_auth
def system_processes():
    """Get running processes."""
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['name'] and 'pentest' in proc_info['name'].lower():
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return jsonify({'success': True, 'processes': processes})
        
    except Exception as e:
        logging.error(f"System processes error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/tools/status')
@require_auth
def tools_status():
    """Get status of security tools."""
    try:
        tools = [
            {'name': 'Nmap', 'status': 'available', 'version': '7.91'},
            {'name': 'SQLMap', 'status': 'available', 'version': '1.6.12'},
            {'name': 'Nikto', 'status': 'available', 'version': '2.5.0'},
            {'name': 'OWASP ZAP', 'status': 'available', 'version': '2.12.0'},
            {'name': 'Metasploit', 'status': 'available', 'version': '6.3.4'},
            {'name': 'Hydra', 'status': 'available', 'version': '9.3'},
            {'name': 'John the Ripper', 'status': 'available', 'version': '1.9.0'},
            {'name': 'Hashcat', 'status': 'available', 'version': '6.2.5'},
            {'name': 'Gobuster', 'status': 'available', 'version': '3.2.0'},
            {'name': 'Dirb', 'status': 'available', 'version': '2.22'}
        ]
        
        return jsonify({'success': True, 'tools': tools})
        
    except Exception as e:
        logging.error(f"Tools status error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/vulnerabilities/stats')
@require_auth
def vulnerability_stats():
    """Get vulnerability statistics."""
    try:
        # Mock vulnerability statistics
        stats = {
            'total': 156,
            'by_severity': {
                'critical': 12,
                'high': 28,
                'medium': 54,
                'low': 42,
                'info': 20
            },
            'by_category': {
                'web_application': 67,
                'network': 34,
                'system': 28,
                'database': 15,
                'wireless': 8,
                'social_engineering': 4
            },
            'by_status': {
                'new': 45,
                'confirmed': 78,
                'false_positive': 12,
                'fixed': 21
            },
            'trend': {
                'last_30_days': 23,
                'last_7_days': 8,
                'last_24_hours': 3
            }
        }
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logging.error(f"Vulnerability stats error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/scans/history')
@require_auth
def scan_history():
    """Get scan history."""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Mock scan history
        scans = []
        for i in range(limit):
            scan = {
                'id': f'scan_{1000 + i + offset}',
                'target': f'192.168.1.{100 + (i % 50)}',
                'type': ['quick', 'comprehensive', 'web', 'network'][i % 4],
                'status': ['completed', 'failed', 'stopped'][i % 3],
                'started_at': datetime.now().isoformat(),
                'completed_at': datetime.now().isoformat(),
                'duration': 300 + (i * 30),
                'vulnerabilities_found': i % 10,
                'user_id': session.get('user_id')
            }
            scans.append(scan)
        
        return jsonify({
            'success': True,
            'scans': scans,
            'total': 1000,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logging.error(f"Scan history error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/projects/list')
@require_auth
def projects_list():
    """Get user projects."""
    try:
        # Mock projects data
        projects = [
            {
                'id': 'proj_001',
                'name': 'Corporate Network Assessment',
                'client': 'Acme Corp',
                'type': 'network',
                'status': 'in_progress',
                'created_at': '2024-01-15T10:00:00Z',
                'targets': ['192.168.1.0/24', 'example.com'],
                'scan_count': 15,
                'vulnerability_count': 23
            },
            {
                'id': 'proj_002',
                'name': 'Web Application Pentest',
                'client': 'Tech Solutions Inc',
                'type': 'web',
                'status': 'completed',
                'created_at': '2024-01-10T14:30:00Z',
                'targets': ['app.techsolutions.com'],
                'scan_count': 8,
                'vulnerability_count': 12
            }
        ]
        
        return jsonify({'success': True, 'projects': projects})
        
    except Exception as e:
        logging.error(f"Projects list error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/notifications/list')
@require_auth
def notifications_list():
    """Get user notifications."""
    try:
        # Mock notifications
        notifications = [
            {
                'id': 'notif_001',
                'type': 'scan_completed',
                'title': 'Scan Completed',
                'message': 'Network scan of 192.168.1.0/24 completed successfully',
                'severity': 'info',
                'read': False,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 'notif_002',
                'type': 'vulnerability_found',
                'title': 'Critical Vulnerability Found',
                'message': 'SQL Injection vulnerability detected in login form',
                'severity': 'critical',
                'read': False,
                'created_at': datetime.now().isoformat()
            }
        ]
        
        return jsonify({'success': True, 'notifications': notifications})
        
    except Exception as e:
        logging.error(f"Notifications error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/logs/system')
@require_auth
@require_role('admin')
def system_logs():
    """Get system logs (admin only)."""
    try:
        limit = request.args.get('limit', 100, type=int)
        level = request.args.get('level', 'INFO')
        
        # Mock log entries
        logs = []
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for i in range(limit):
            log = {
                'timestamp': datetime.now().isoformat(),
                'level': levels[i % len(levels)],
                'module': 'pentest_toolkit',
                'message': f'Log message {i + 1}',
                'user_id': session.get('user_id') if i % 3 == 0 else None
            }
            logs.append(log)
        
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        logging.error(f"System logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/export/data', methods=['POST'])
@require_auth
def export_data():
    """Export user data."""
    try:
        data_type = request.json.get('type', 'all')
        format_type = request.json.get('format', 'json')
        
        # Mock export data
        export_data = {
            'user_id': session.get('user_id'),
            'export_type': data_type,
            'exported_at': datetime.now().isoformat(),
            'data': {
                'scans': [],
                'projects': [],
                'reports': [],
                'settings': {}
            }
        }
        
        return jsonify({
            'success': True,
            'download_url': f'/api/download/export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format_type}'
        })
        
    except Exception as e:
        logging.error(f"Export data error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/search')
@require_auth
def global_search():
    """Global search across all data."""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', 'all')
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({'success': False, 'message': 'Search query required'}), 400
        
        # Mock search results
        results = {
            'scans': [
                {
                    'id': 'scan_001',
                    'target': '192.168.1.100',
                    'type': 'network',
                    'match_field': 'target'
                }
            ],
            'vulnerabilities': [
                {
                    'id': 'vuln_001',
                    'title': 'SQL Injection in login form',
                    'severity': 'critical',
                    'match_field': 'title'
                }
            ],
            'projects': [],
            'reports': []
        }
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'total': sum(len(v) for v in results.values())
        })
        
    except Exception as e:
        logging.error(f"Global search error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': 'healthy',
            'redis': 'healthy',
            'celery': 'healthy'
        }
    })

def get_system_uptime():
    """Get system uptime in seconds."""
    try:
        return psutil.boot_time()
    except:
        return 0