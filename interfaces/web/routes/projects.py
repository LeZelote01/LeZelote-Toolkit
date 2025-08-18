#!/usr/bin/env python3
"""
Project Management Routes for Pentest-USB Toolkit Web Interface
===============================================================

Handles project creation, management, and organization.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from datetime import datetime
import secrets
import logging
from .auth import require_auth

# Create blueprint
bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/')
@require_auth
def projects_list():
    """Show projects management page."""
    user_projects = get_user_projects(session.get('user_id'))
    return render_template('project_management.html', projects=user_projects)

@bp.route('/create', methods=['POST'])
@require_auth
def create_project():
    """Create a new project."""
    try:
        data = request.get_json() if request.is_json else request.form
        
        project_data = {
            'name': data.get('name', '').strip(),
            'client': data.get('client', '').strip(),
            'type': data.get('type'),
            'priority': data.get('priority', 'medium'),
            'description': data.get('description', '').strip(),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'target_systems': data.get('target_systems', '').strip(),
            'auto_scan': data.get('auto_scan') == 'on' or data.get('auto_scan') is True,
            'notifications': data.get('notifications') == 'on' or data.get('notifications') is True
        }
        
        # Validate required fields
        if not project_data['name']:
            return jsonify({'success': False, 'message': 'Project name is required'}), 400
        
        if not project_data['type']:
            return jsonify({'success': False, 'message': 'Project type is required'}), 400
        
        # Create project
        project_id = create_project_record(project_data, session.get('user_id'))
        
        # Start initial scan if requested
        if project_data['auto_scan'] and project_data['target_systems']:
            start_initial_project_scan(project_id, project_data['target_systems'])
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': 'Project created successfully'
        })
        
    except Exception as e:
        logging.error(f"Project creation error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>')
@require_auth
def project_details(project_id):
    """Show project details."""
    project = get_project_by_id(project_id, session.get('user_id'))
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.projects_list'))
    
    # Get project scans and reports
    project_scans = get_project_scans(project_id)
    project_reports = get_project_reports(project_id)
    
    return render_template('project_details.html', 
                         project=project,
                         scans=project_scans,
                         reports=project_reports)

@bp.route('/<project_id>/update', methods=['PUT', 'POST'])
@require_auth
def update_project(project_id):
    """Update project information."""
    try:
        project = get_project_by_id(project_id, session.get('user_id'))
        
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        data = request.get_json() if request.is_json else request.form
        
        # Update project fields
        update_data = {}
        updatable_fields = ['name', 'client', 'type', 'priority', 'description', 
                           'start_date', 'end_date', 'target_systems']
        
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        if update_data:
            update_project_record(project_id, update_data)
        
        return jsonify({
            'success': True,
            'message': 'Project updated successfully'
        })
        
    except Exception as e:
        logging.error(f"Project update error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>/delete', methods=['DELETE', 'POST'])
@require_auth
def delete_project(project_id):
    """Delete a project."""
    try:
        project = get_project_by_id(project_id, session.get('user_id'))
        
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        # Check if project has active scans
        active_scans = get_active_project_scans(project_id)
        if active_scans:
            return jsonify({
                'success': False,
                'message': 'Cannot delete project with active scans'
            }), 400
        
        # Delete project and associated data
        delete_project_record(project_id)
        
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Project deletion error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>/scans')
@require_auth
def project_scans(project_id):
    """Get project scans."""
    try:
        project = get_project_by_id(project_id, session.get('user_id'))
        
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        scans = get_project_scans(project_id)
        return jsonify({'success': True, 'scans': scans})
        
    except Exception as e:
        logging.error(f"Project scans error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>/reports')
@require_auth
def project_reports(project_id):
    """Get project reports."""
    try:
        project = get_project_by_id(project_id, session.get('user_id'))
        
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        reports = get_project_reports(project_id)
        return jsonify({'success': True, 'reports': reports})
        
    except Exception as e:
        logging.error(f"Project reports error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>/vulnerabilities')
@require_auth
def project_vulnerabilities(project_id):
    """Get project vulnerabilities."""
    try:
        project = get_project_by_id(project_id, session.get('user_id'))
        
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        vulnerabilities = get_project_vulnerabilities(project_id)
        return jsonify({'success': True, 'vulnerabilities': vulnerabilities})
        
    except Exception as e:
        logging.error(f"Project vulnerabilities error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<project_id>/archive', methods=['POST'])
@require_auth
def archive_project(project_id):
    """Archive a project."""
    try:
        project = get_project_by_id(project_id, session.get('user_id'))
        
        if not project:
            return jsonify({'success': False, 'message': 'Project not found'}), 404
        
        # Archive the project
        archive_project_record(project_id)
        
        return jsonify({
            'success': True,
            'message': 'Project archived successfully'
        })
        
    except Exception as e:
        logging.error(f"Project archive error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/templates')
@require_auth
def project_templates():
    """Get project templates."""
    templates = [
        {
            'id': 'network_assessment',
            'name': 'Network Security Assessment',
            'description': 'Comprehensive network infrastructure security testing',
            'default_type': 'network',
            'suggested_duration': '5-10 days',
            'typical_scope': ['Network scanning', 'Port enumeration', 'Service identification', 'Vulnerability assessment']
        },
        {
            'id': 'web_app_test',
            'name': 'Web Application Penetration Test',
            'description': 'Security testing of web applications and APIs',
            'default_type': 'web',
            'suggested_duration': '3-7 days',
            'typical_scope': ['Web application scanning', 'Authentication testing', 'Input validation', 'Session management']
        },
        {
            'id': 'mobile_app_test',
            'name': 'Mobile Application Security Test',
            'description': 'Security assessment of mobile applications',
            'default_type': 'mobile',
            'suggested_duration': '4-8 days',
            'typical_scope': ['Static analysis', 'Dynamic analysis', 'API testing', 'Data storage review']
        },
        {
            'id': 'wireless_assessment',
            'name': 'Wireless Security Assessment',
            'description': 'Wireless network security evaluation',
            'default_type': 'wireless',
            'suggested_duration': '2-5 days',
            'typical_scope': ['WLAN discovery', 'Encryption analysis', 'Access point testing', 'Client attacks']
        },
        {
            'id': 'compliance_audit',
            'name': 'Compliance Security Audit',
            'description': 'Regulatory compliance security assessment',
            'default_type': 'compliance',
            'suggested_duration': '7-14 days',
            'typical_scope': ['Policy review', 'Technical controls', 'Documentation audit', 'Gap analysis']
        }
    ]
    
    return jsonify({'success': True, 'templates': templates})

@bp.route('/api/list')
@require_auth
def api_projects_list():
    """API endpoint for projects list."""
    try:
        projects = get_user_projects(session.get('user_id'))
        return jsonify({'success': True, 'projects': projects})
        
    except Exception as e:
        logging.error(f"API projects list error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/statistics')
@require_auth
def api_project_statistics():
    """Get project statistics."""
    try:
        user_id = session.get('user_id')
        projects = get_user_projects(user_id)
        
        stats = {
            'total_projects': len(projects),
            'active_projects': len([p for p in projects if p.get('status') == 'in_progress']),
            'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
            'archived_projects': len([p for p in projects if p.get('status') == 'archived']),
            'by_type': {},
            'by_priority': {},
            'recent_activity': get_recent_project_activity(user_id)
        }
        
        # Calculate type distribution
        for project in projects:
            project_type = project.get('type', 'unknown')
            stats['by_type'][project_type] = stats['by_type'].get(project_type, 0) + 1
        
        # Calculate priority distribution
        for project in projects:
            priority = project.get('priority', 'medium')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return jsonify({'success': True, 'statistics': stats})
        
    except Exception as e:
        logging.error(f"Project statistics error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Database helper functions (mock implementation)
_projects_db = {}
_project_scans = {}
_project_reports = {}

def create_project_record(project_data, user_id):
    """Create project record."""
    project_id = secrets.token_hex(8)
    
    project = {
        'id': project_id,
        'user_id': user_id,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        **project_data
    }
    
    _projects_db[project_id] = project
    return project_id

def get_project_by_id(project_id, user_id):
    """Get project by ID."""
    project = _projects_db.get(project_id)
    if project and project['user_id'] == user_id:
        return project
    return None

def get_user_projects(user_id):
    """Get all projects for user."""
    return [project for project in _projects_db.values() if project['user_id'] == user_id]

def update_project_record(project_id, update_data):
    """Update project record."""
    if project_id in _projects_db:
        _projects_db[project_id].update(update_data)
        _projects_db[project_id]['updated_at'] = datetime.now().isoformat()

def delete_project_record(project_id):
    """Delete project record."""
    if project_id in _projects_db:
        del _projects_db[project_id]
    
    # Clean up associated data
    _project_scans.pop(project_id, None)
    _project_reports.pop(project_id, None)

def archive_project_record(project_id):
    """Archive project."""
    if project_id in _projects_db:
        _projects_db[project_id]['status'] = 'archived'
        _projects_db[project_id]['archived_at'] = datetime.now().isoformat()

def get_project_scans(project_id):
    """Get scans for project."""
    return _project_scans.get(project_id, [])

def get_project_reports(project_id):
    """Get reports for project."""
    return _project_reports.get(project_id, [])

def get_project_vulnerabilities(project_id):
    """Get vulnerabilities for project."""
    # Mock vulnerabilities
    return [
        {
            'id': 'vuln_001',
            'title': 'SQL Injection in login form',
            'severity': 'critical',
            'cvss': 9.8,
            'status': 'confirmed',
            'found_at': datetime.now().isoformat()
        }
    ]

def get_active_project_scans(project_id):
    """Get active scans for project."""
    scans = get_project_scans(project_id)
    return [scan for scan in scans if scan.get('status') in ['running', 'starting']]

def start_initial_project_scan(project_id, targets):
    """Start initial scan for project."""
    # Mock scan start
    scan_data = {
        'id': secrets.token_hex(8),
        'project_id': project_id,
        'targets': targets.split('\n'),
        'type': 'initial',
        'status': 'starting',
        'started_at': datetime.now().isoformat()
    }
    
    if project_id not in _project_scans:
        _project_scans[project_id] = []
    
    _project_scans[project_id].append(scan_data)

def get_recent_project_activity(user_id):
    """Get recent project activity."""
    # Mock activity
    return [
        {
            'type': 'project_created',
            'project_name': 'Web App Assessment',
            'timestamp': datetime.now().isoformat()
        },
        {
            'type': 'scan_completed',
            'project_name': 'Network Test',
            'timestamp': datetime.now().isoformat()
        }
    ]