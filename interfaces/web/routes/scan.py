#!/usr/bin/env python3
"""
Scan Management Routes for Pentest-USB Toolkit Web Interface
============================================================

Handles scan operations, monitoring, and results.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from datetime import datetime
import secrets
import logging
from .auth import require_auth, require_role

# Create blueprint
bp = Blueprint('scan', __name__, url_prefix='/scan')

@bp.route('/new', methods=['GET', 'POST'])
@require_auth
def new_scan():
    """Create and start a new scan."""
    if request.method == 'GET':
        return render_template('new_scan.html')
    
    # Handle POST request - start new scan
    try:
        scan_config = {
            'target': request.form.get('target', '').strip(),
            'type': request.form.get('scan_type', 'quick'),
            'ports': request.form.get('ports', '1-1000'),
            'threads': int(request.form.get('threads', 10)),
            'description': request.form.get('description', '').strip(),
            'save_project': request.form.get('save_project') == 'on',
            'notifications': request.form.get('notifications') == 'on'
        }
        
        # Validate input
        if not scan_config['target']:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Target is required'}), 400
            flash('Target is required', 'error')
            return render_template('new_scan.html')
        
        # Get current app instance to start scan
        from flask import current_app
        web_app = getattr(current_app, 'web_app', None)
        
        if web_app:
            scan_id = web_app.start_scan(scan_config, session.get('user_id'))
            
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({
                    'success': True,
                    'scan_id': scan_id,
                    'message': 'Scan started successfully'
                })
            
            flash(f'Scan started successfully! ID: {scan_id}', 'success')
            return redirect(url_for('scan.monitor', scan_id=scan_id))
        else:
            raise Exception('Web application not properly initialized')
            
    except Exception as e:
        logging.error(f"Error starting scan: {e}")
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': str(e)}), 500
        
        flash(f'Error starting scan: {e}', 'error')
        return render_template('new_scan.html')

@bp.route('/monitor/<scan_id>')
@require_auth
def monitor(scan_id):
    """Monitor scan progress."""
    return render_template('scan_monitor.html', scan_id=scan_id)

@bp.route('/api/start', methods=['POST'])
@require_auth
def api_start_scan():
    """API endpoint to start a scan."""
    try:
        data = request.get_json()
        
        if not data or not data.get('target'):
            return jsonify({'success': False, 'message': 'Target is required'}), 400
        
        scan_config = {
            'target': data.get('target'),
            'type': data.get('type', 'quick'),
            'ports': data.get('ports', '1-1000'),
            'threads': data.get('threads', 10),
            'description': data.get('description', ''),
            'save_project': data.get('save_project', False),
            'notifications': data.get('notifications', True)
        }
        
        # Get current app instance
        from flask import current_app
        web_app = getattr(current_app, 'web_app', None)
        
        if web_app:
            scan_id = web_app.start_scan(scan_config, session.get('user_id'))
            return jsonify({
                'success': True,
                'scan_id': scan_id,
                'message': 'Scan started successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Service not available'}), 503
            
    except Exception as e:
        logging.error(f"API scan start error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/status/<scan_id>')
@require_auth
def api_scan_status(scan_id):
    """Get scan status via API."""
    try:
        from flask import current_app
        web_app = getattr(current_app, 'web_app', None)
        
        if web_app and scan_id in web_app.active_scans:
            scan_info = web_app.active_scans[scan_id]
            return jsonify({'success': True, 'scan': scan_info})
        else:
            return jsonify({'success': False, 'message': 'Scan not found'}), 404
            
    except Exception as e:
        logging.error(f"API scan status error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/stop/<scan_id>', methods=['POST'])
@require_auth
def api_stop_scan(scan_id):
    """Stop a running scan."""
    try:
        from flask import current_app
        web_app = getattr(current_app, 'web_app', None)
        
        if web_app and scan_id in web_app.active_scans:
            # Remove from active scans to stop it
            scan_info = web_app.active_scans.pop(scan_id)
            scan_info['status'] = 'stopped'
            scan_info['stopped_at'] = datetime.now().isoformat()
            
            # Notify via WebSocket
            web_app.socketio.emit('scan_stopped', {
                'scan_id': scan_id
            }, room=f"user_{session.get('user_id')}")
            
            return jsonify({'success': True, 'message': 'Scan stopped successfully'})
        else:
            return jsonify({'success': False, 'message': 'Scan not found'}), 404
            
    except Exception as e:
        logging.error(f"API scan stop error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/logs/<scan_id>')
@require_auth
def api_scan_logs(scan_id):
    """Get scan logs via API."""
    try:
        from flask import current_app
        web_app = getattr(current_app, 'web_app', None)
        
        if web_app and scan_id in web_app.active_scans:
            scan_info = web_app.active_scans[scan_id]
            return jsonify({
                'success': True,
                'logs': scan_info.get('logs', [])
            })
        else:
            return jsonify({'success': False, 'message': 'Scan not found'}), 404
            
    except Exception as e:
        logging.error(f"API scan logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/reconnaissance')
@require_auth
def reconnaissance():
    """Reconnaissance scanning page."""
    return render_template('scan_reconnaissance.html')

@bp.route('/vulnerability')
@require_auth
def vulnerability():
    """Vulnerability assessment page."""
    return render_template('scan_vulnerability.html')

@bp.route('/exploitation')
@require_auth
def exploitation():
    """Exploitation testing page."""
    return render_template('scan_exploitation.html')

@bp.route('/results')
@require_auth
def results():
    """Scan results page."""
    return render_template('scan_results.html')

@bp.route('/api/results/<scan_id>')
@require_auth
def api_scan_results(scan_id):
    """Get detailed scan results."""
    try:
        # In a real implementation, fetch from database
        # For now, return mock data
        results = {
            'scan_id': scan_id,
            'target': 'example.com',
            'status': 'completed',
            'vulnerabilities': [
                {
                    'id': 'VULN-001',
                    'title': 'SQL Injection vulnerability',
                    'severity': 'critical',
                    'cvss': 9.8,
                    'description': 'SQL injection found in login form',
                    'url': 'http://example.com/login.php',
                    'parameter': 'username'
                }
            ],
            'scan_summary': {
                'total_vulnerabilities': 1,
                'critical': 1,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
        }
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logging.error(f"API scan results error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/templates')
@require_auth
def templates():
    """Scan template management page."""
    return render_template('scan_templates.html')

@bp.route('/api/templates', methods=['GET', 'POST'])
@require_auth
def api_templates():
    """Manage scan templates."""
    if request.method == 'GET':
        # Return available templates
        templates = [
            {
                'id': 'quick',
                'name': 'Quick Scan',
                'description': 'Fast network discovery and basic port scan',
                'duration': '5-10 minutes',
                'modules': ['reconnaissance']
            },
            {
                'id': 'comprehensive',
                'name': 'Comprehensive Scan',
                'description': 'Complete security assessment',
                'duration': '30-60 minutes',
                'modules': ['reconnaissance', 'vulnerability', 'exploitation']
            },
            {
                'id': 'web',
                'name': 'Web Application',
                'description': 'Web application security testing',
                'duration': '15-30 minutes',
                'modules': ['reconnaissance', 'vulnerability']
            }
        ]
        
        return jsonify({'success': True, 'templates': templates})
    
    elif request.method == 'POST':
        # Create new template
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'success': False, 'message': 'Template name is required'}), 400
        
        # In a real implementation, save to database
        template_id = secrets.token_hex(8)
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'message': 'Template created successfully'
        })

@bp.route('/history')
@require_auth
def history():
    """Scan history page."""
    return render_template('scan_history.html')

@bp.route('/api/history')
@require_auth
def api_scan_history():
    """Get scan history via API."""
    try:
        # In a real implementation, fetch from database
        # For now, return mock data
        history = [
            {
                'id': 'scan_001',
                'target': 'example.com',
                'type': 'web',
                'status': 'completed',
                'started_at': '2024-01-15T10:30:00Z',
                'completed_at': '2024-01-15T10:45:00Z',
                'vulnerabilities_found': 3,
                'severity_summary': {'critical': 1, 'high': 1, 'medium': 1}
            },
            {
                'id': 'scan_002',
                'target': '192.168.1.0/24',
                'type': 'network',
                'status': 'completed',
                'started_at': '2024-01-15T09:00:00Z',
                'completed_at': '2024-01-15T09:25:00Z',
                'vulnerabilities_found': 0,
                'severity_summary': {'critical': 0, 'high': 0, 'medium': 0}
            }
        ]
        
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        logging.error(f"API scan history error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500