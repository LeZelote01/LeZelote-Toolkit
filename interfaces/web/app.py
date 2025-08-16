#!/usr/bin/env python3
"""
Web Interface Application for Pentest-USB Toolkit
================================================

Flask-based web application providing a modern, responsive interface
for managing penetration testing operations, viewing results, and 
generating reports.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import threading
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets

# Local imports
from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import LoggingHandler
from core.db.sqlite_manager import SQLiteManager
from .routes import auth, scan, report, api, projects, settings

class PentestWebApp:
    """Main web application class for Pentest-USB Toolkit."""
    
    def __init__(self):
        """Initialize the Flask web application."""
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        
        # Configure Flask
        self.app.config.update({
            'SECRET_KEY': self.app.secret_key,
            'UPLOAD_FOLDER': str(project_root / 'uploads'),
            'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB max file size
            'SESSION_PERMANENT': False,
            'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
        })
        
        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize logging
        self.logger = LoggingHandler().get_logger("WebApp")
        
        # Initialize database
        self.db = SQLiteManager()
        
        # Application state
        self.active_scans = {}
        self.connected_users = {}
        self.system_stats = {
            'scans_completed': 0,
            'vulnerabilities_found': 0,
            'projects_created': 0,
            'active_sessions': 0
        }
        
        # Setup routes and handlers
        self._setup_routes()
        self._setup_socketio_handlers()
        self._setup_error_handlers()
        
        # Register blueprints
        self.app.register_blueprint(auth.bp)
        self.app.register_blueprint(scan.bp)
        self.app.register_blueprint(report.bp)
        self.app.register_blueprint(api.bp)
        self.app.register_blueprint(projects.bp)
        self.app.register_blueprint(settings.bp)
        
        # Ensure upload directory exists
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        self.logger.info("Pentest-USB Web Interface initialized")
        
    def _setup_routes(self):
        """Setup main application routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            if not session.get('authenticated'):
                return redirect(url_for('auth.login'))
            return render_template('dashboard.html', 
                                 user=session.get('username', 'User'),
                                 stats=self.system_stats)
        
        @self.app.route('/dashboard')
        def dashboard():
            """Dashboard page with real-time metrics."""
            if not session.get('authenticated'):
                return redirect(url_for('auth.login'))
            return render_template('dashboard.html', 
                                 user=session.get('username', 'User'),
                                 stats=self.system_stats)
        
        @self.app.route('/scans')
        def scans():
            """Scan management page."""
            if not session.get('authenticated'):
                return redirect(url_for('auth.login'))
            
            # Get recent scans from database
            recent_scans = self.db.get_recent_scans(limit=10)
            return render_template('scan_results.html', 
                                 scans=recent_scans,
                                 active_scans=self.active_scans)
        
        @self.app.route('/projects')
        def projects_list():
            """Project management page."""
            if not session.get('authenticated'):
                return redirect(url_for('auth.login'))
            
            # Get user projects
            user_projects = self.db.get_user_projects(session.get('user_id'))
            return render_template('project_management.html', projects=user_projects)
        
        @self.app.route('/reports')
        def reports():
            """Reports management page."""
            if not session.get('authenticated'):
                return redirect(url_for('auth.login'))
            
            # Get available reports
            available_reports = self.db.get_user_reports(session.get('user_id'))
            return render_template('report_view.html', reports=available_reports)
        
        @self.app.route('/settings')
        def settings_page():
            """Settings and configuration page."""
            if not session.get('authenticated'):
                return redirect(url_for('auth.login'))
            return render_template('settings.html')
        
        @self.app.route('/api/system/stats')
        def api_system_stats():
            """API endpoint for system statistics."""
            if not session.get('authenticated'):
                return jsonify({'error': 'Unauthorized'}), 401
                
            # Get real-time system statistics
            import psutil
            stats = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'active_scans': len(self.active_scans),
                'connected_users': len(self.connected_users),
                'scans_completed': self.system_stats['scans_completed'],
                'vulnerabilities_found': self.system_stats['vulnerabilities_found'],
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(stats)
        
        @self.app.route('/api/scans/active')
        def api_active_scans():
            """API endpoint for active scans."""
            if not session.get('authenticated'):
                return jsonify({'error': 'Unauthorized'}), 401
                
            return jsonify({
                'active_scans': list(self.active_scans.values()),
                'count': len(self.active_scans)
            })
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
            
    def _setup_socketio_handlers(self):
        """Setup WebSocket handlers for real-time communication."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            if not session.get('authenticated'):
                return False
                
            user_id = session.get('user_id')
            username = session.get('username', 'Anonymous')
            
            self.connected_users[request.sid] = {
                'user_id': user_id,
                'username': username,
                'connected_at': datetime.now().isoformat()
            }
            
            join_room(f"user_{user_id}")
            
            # Send welcome message with current stats
            emit('system_stats', self.system_stats)
            emit('active_scans', list(self.active_scans.values()))
            
            self.logger.info(f"User {username} connected via WebSocket")
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            if request.sid in self.connected_users:
                user_info = self.connected_users[request.sid]
                username = user_info['username']
                
                leave_room(f"user_{user_info['user_id']}")
                del self.connected_users[request.sid]
                
                self.logger.info(f"User {username} disconnected")
                
        @self.socketio.on('join_scan_room')
        def handle_join_scan(data):
            """Handle joining a scan room for updates."""
            scan_id = data.get('scan_id')
            if scan_id and scan_id in self.active_scans:
                join_room(f"scan_{scan_id}")
                emit('scan_status', self.active_scans[scan_id])
                
        @self.socketio.on('leave_scan_room')
        def handle_leave_scan(data):
            """Handle leaving a scan room."""
            scan_id = data.get('scan_id')
            if scan_id:
                leave_room(f"scan_{scan_id}")
                
    def _setup_error_handlers(self):
        """Setup error handlers for the application."""
        
        @self.app.errorhandler(404)
        def not_found_error(error):
            """Handle 404 errors."""
            return render_template('errors/404.html'), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors."""
            self.logger.error(f"Internal server error: {error}")
            return render_template('errors/500.html'), 500
        
        @self.app.errorhandler(403)
        def forbidden_error(error):
            """Handle 403 errors."""
            return render_template('errors/403.html'), 403
            
    def start_scan(self, scan_config: Dict[str, Any], user_id: str) -> str:
        """Start a new scan and track its progress."""
        scan_id = secrets.token_hex(8)
        
        scan_info = {
            'id': scan_id,
            'user_id': user_id,
            'target': scan_config.get('target'),
            'scan_type': scan_config.get('type', 'comprehensive'),
            'status': 'starting',
            'progress': 0,
            'started_at': datetime.now().isoformat(),
            'vulnerabilities': [],
            'logs': []
        }
        
        self.active_scans[scan_id] = scan_info
        
        # Start scan in background thread
        scan_thread = threading.Thread(
            target=self._run_scan_background,
            args=(scan_id, scan_config)
        )
        scan_thread.daemon = True
        scan_thread.start()
        
        # Notify connected clients
        self.socketio.emit('scan_started', scan_info, room=f"user_{user_id}")
        
        return scan_id
        
    def _run_scan_background(self, scan_id: str, scan_config: Dict[str, Any]):
        """Run scan in background thread with progress updates."""
        try:
            scan_info = self.active_scans[scan_id]
            user_id = scan_info['user_id']
            
            # Initialize orchestrator
            orchestrator = PentestOrchestrator(
                target=scan_config['target'],
                profile=scan_config.get('type', 'comprehensive')
            )
            
            # Simulate scan phases with progress updates
            phases = [
                ('Initializing scan', 5),
                ('Network discovery', 20),
                ('Port scanning', 25),
                ('Service enumeration', 20),
                ('Vulnerability detection', 25),
                ('Finalizing results', 5)
            ]
            
            total_progress = 0
            
            for phase_name, phase_weight in phases:
                scan_info['status'] = phase_name.lower().replace(' ', '_')
                
                # Update progress incrementally
                for i in range(phase_weight):
                    if scan_id not in self.active_scans:  # Scan was cancelled
                        return
                        
                    total_progress += 1
                    scan_info['progress'] = total_progress
                    scan_info['logs'].append({
                        'timestamp': datetime.now().isoformat(),
                        'message': f"{phase_name}: {i+1}/{phase_weight}",
                        'level': 'info'
                    })
                    
                    # Emit progress update
                    self.socketio.emit('scan_progress', {
                        'scan_id': scan_id,
                        'progress': total_progress,
                        'status': scan_info['status'],
                        'message': f"{phase_name}: {i+1}/{phase_weight}"
                    }, room=f"user_{user_id}")
                    
                    time.sleep(0.5)  # Simulate work
                    
            # Simulate vulnerability results
            vulnerabilities = [
                {
                    'id': 'VULN-001',
                    'title': 'SQL Injection vulnerability',
                    'severity': 'critical',
                    'cvss': 9.8,
                    'url': f"http://{scan_config['target']}/login.php",
                    'description': 'SQL injection in login form'
                },
                {
                    'id': 'VULN-002', 
                    'title': 'Cross-site scripting (XSS)',
                    'severity': 'high',
                    'cvss': 6.1,
                    'url': f"http://{scan_config['target']}/search.php",
                    'description': 'Reflected XSS in search parameter'
                }
            ]
            
            scan_info['vulnerabilities'] = vulnerabilities
            scan_info['status'] = 'completed'
            scan_info['completed_at'] = datetime.now().isoformat()
            scan_info['progress'] = 100
            
            # Update system statistics
            self.system_stats['scans_completed'] += 1
            self.system_stats['vulnerabilities_found'] += len(vulnerabilities)
            
            # Save to database
            self.db.save_scan_results(scan_info)
            
            # Notify completion
            self.socketio.emit('scan_completed', {
                'scan_id': scan_id,
                'vulnerabilities_count': len(vulnerabilities),
                'duration': self._calculate_duration(
                    scan_info['started_at'], 
                    scan_info['completed_at']
                )
            }, room=f"user_{user_id}")
            
            self.logger.info(f"Scan {scan_id} completed successfully")
            
        except Exception as e:
            # Handle scan failure
            scan_info['status'] = 'failed'
            scan_info['error'] = str(e)
            scan_info['failed_at'] = datetime.now().isoformat()
            
            self.socketio.emit('scan_failed', {
                'scan_id': scan_id,
                'error': str(e)
            }, room=f"user_{user_id}")
            
            self.logger.error(f"Scan {scan_id} failed: {e}")
            
        finally:
            # Remove from active scans after delay
            threading.Timer(300, lambda: self.active_scans.pop(scan_id, None)).start()
            
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between two ISO timestamps."""
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        duration = end - start
        return str(duration).split('.')[0]  # Remove microseconds
        
    def broadcast_system_update(self):
        """Broadcast system statistics to all connected clients."""
        self.socketio.emit('system_stats', self.system_stats)
        
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application."""
        self.logger.info(f"Starting Pentest-USB Web Interface on {host}:{port}")
        
        # Start background task for system monitoring
        def monitor_system():
            while True:
                try:
                    # Update active sessions count
                    self.system_stats['active_sessions'] = len(self.connected_users)
                    
                    # Broadcast updates every 30 seconds
                    self.broadcast_system_update()
                    time.sleep(30)
                except Exception as e:
                    self.logger.error(f"System monitoring error: {e}")
                    time.sleep(60)
                    
        monitor_thread = threading.Thread(target=monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Run the application
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )


def create_app():
    """Application factory function."""
    web_app = PentestWebApp()
    return web_app.app, web_app.socketio


# For direct execution
if __name__ == '__main__':
    app = PentestWebApp()
    app.run(debug=True)