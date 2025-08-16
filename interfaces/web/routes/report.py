#!/usr/bin/env python3
"""
Report Generation Routes for Pentest-USB Toolkit Web Interface
==============================================================

Handles report creation, management, and download functionality.
"""

from flask import Blueprint, render_template, request, jsonify, session, send_file, flash, redirect, url_for
from datetime import datetime
import secrets
import logging
import json
import os
import tempfile
from .auth import require_auth, require_role

# Create blueprint
bp = Blueprint('report', __name__, url_prefix='/reports')

@bp.route('/')
@require_auth
def reports_list():
    """Show reports management page."""
    # Get user reports from database
    user_reports = get_user_reports(session.get('user_id'))
    return render_template('report_view.html', reports=user_reports)

@bp.route('/generate', methods=['POST'])
@require_auth
def generate_report():
    """Generate a new report."""
    try:
        data = request.get_json() if request.is_json else request.form
        
        report_config = {
            'project_id': data.get('project_id'),
            'template': data.get('template', 'technical'),
            'format': data.get('format', 'pdf'),
            'title': data.get('title', 'Security Assessment Report'),
            'include_summary': data.get('include_summary', True),
            'include_vulns': data.get('include_vulns', True),
            'include_evidence': data.get('include_evidence', True),
            'include_remediation': data.get('include_remediation', True),
            'include_appendix': data.get('include_appendix', False),
            'include_compliance': data.get('include_compliance', False),
            'notes': data.get('notes', ''),
            'auto_download': data.get('auto_download', True)
        }
        
        if not report_config['project_id']:
            return jsonify({'success': False, 'message': 'Project ID is required'}), 400
        
        # Generate report in background
        report_id = start_report_generation(report_config, session.get('user_id'))
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'message': 'Report generation started'
        })
        
    except Exception as e:
        logging.error(f"Report generation error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/status/<report_id>')
@require_auth
def report_status(report_id):
    """Get report generation status."""
    try:
        # Get report status from database or cache
        report_info = get_report_status(report_id, session.get('user_id'))
        
        if not report_info:
            return jsonify({'success': False, 'message': 'Report not found'}), 404
        
        return jsonify({'success': True, 'report': report_info})
        
    except Exception as e:
        logging.error(f"Report status error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/download/<report_id>')
@require_auth
def download_report(report_id):
    """Download generated report."""
    try:
        # Get report file path
        report_info = get_report_info(report_id, session.get('user_id'))
        
        if not report_info:
            flash('Report not found', 'error')
            return redirect(url_for('report.reports_list'))
        
        if report_info['status'] != 'completed':
            flash('Report is not ready for download', 'warning')
            return redirect(url_for('report.reports_list'))
        
        file_path = report_info.get('file_path')
        if not file_path or not os.path.exists(file_path):
            flash('Report file not found', 'error')
            return redirect(url_for('report.reports_list'))
        
        # Update download count
        increment_download_count(report_id)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=report_info.get('filename', f'report_{report_id}.pdf'),
            mimetype=get_mimetype(report_info.get('format', 'pdf'))
        )
        
    except Exception as e:
        logging.error(f"Report download error: {e}")
        flash('Failed to download report', 'error')
        return redirect(url_for('report.reports_list'))

@bp.route('/preview/<report_id>')
@require_auth
def preview_report(report_id):
    """Preview report in browser."""
    try:
        report_info = get_report_info(report_id, session.get('user_id'))
        
        if not report_info or report_info['status'] != 'completed':
            return jsonify({'success': False, 'message': 'Report not available'}), 404
        
        # For HTML reports, serve directly
        if report_info.get('format') == 'html':
            file_path = report_info.get('file_path')
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        # For other formats, return preview info
        return jsonify({
            'success': True,
            'preview_available': False,
            'message': 'Preview not available for this format'
        })
        
    except Exception as e:
        logging.error(f"Report preview error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/delete/<report_id>', methods=['POST'])
@require_auth
def delete_report(report_id):
    """Delete a report."""
    try:
        # Verify ownership
        report_info = get_report_info(report_id, session.get('user_id'))
        
        if not report_info:
            return jsonify({'success': False, 'message': 'Report not found'}), 404
        
        # Delete file if exists
        file_path = report_info.get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        delete_report_record(report_id)
        
        return jsonify({'success': True, 'message': 'Report deleted successfully'})
        
    except Exception as e:
        logging.error(f"Report deletion error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/templates')
@require_auth
def report_templates():
    """Get available report templates."""
    templates = [
        {
            'id': 'executive',
            'name': 'Executive Summary',
            'description': 'High-level overview for executives and management',
            'sections': ['Executive Summary', 'Risk Assessment', 'Recommendations'],
            'suitable_for': ['Management', 'Board Members', 'Decision Makers']
        },
        {
            'id': 'technical',
            'name': 'Technical Report',
            'description': 'Detailed technical findings and vulnerabilities',
            'sections': ['Vulnerability Details', 'Technical Evidence', 'Exploitation Steps'],
            'suitable_for': ['IT Teams', 'Security Engineers', 'Developers']
        },
        {
            'id': 'compliance',
            'name': 'Compliance Report',
            'description': 'Regulatory compliance assessment and mapping',
            'sections': ['Compliance Status', 'Gap Analysis', 'Remediation Plan'],
            'suitable_for': ['Compliance Officers', 'Auditors', 'Legal Teams']
        },
        {
            'id': 'remediation',
            'name': 'Remediation Guide',
            'description': 'Step-by-step remediation instructions',
            'sections': ['Prioritized Fixes', 'Implementation Steps', 'Validation Tests'],
            'suitable_for': ['System Administrators', 'DevOps Teams', 'IT Support']
        }
    ]
    
    return jsonify({'success': True, 'templates': templates})

@bp.route('/formats')
@require_auth
def report_formats():
    """Get available report formats."""
    formats = [
        {
            'id': 'pdf',
            'name': 'PDF Document',
            'description': 'Portable document format for sharing and printing',
            'mime_type': 'application/pdf',
            'extension': '.pdf'
        },
        {
            'id': 'html',
            'name': 'HTML Report',
            'description': 'Interactive web-based report with navigation',
            'mime_type': 'text/html',
            'extension': '.html'
        },
        {
            'id': 'docx',
            'name': 'Word Document',
            'description': 'Microsoft Word format for editing and collaboration',
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'extension': '.docx'
        },
        {
            'id': 'json',
            'name': 'JSON Data',
            'description': 'Raw data format for integration and analysis',
            'mime_type': 'application/json',
            'extension': '.json'
        }
    ]
    
    return jsonify({'success': True, 'formats': formats})

@bp.route('/api/list')
@require_auth
def api_reports_list():
    """API endpoint to get user's reports."""
    try:
        reports = get_user_reports(session.get('user_id'))
        return jsonify({'success': True, 'reports': reports})
        
    except Exception as e:
        logging.error(f"API reports list error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/analytics')
@require_auth
def api_report_analytics():
    """Get report generation analytics."""
    try:
        analytics = get_report_analytics(session.get('user_id'))
        return jsonify({'success': True, 'analytics': analytics})
        
    except Exception as e:
        logging.error(f"Report analytics error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def start_report_generation(config, user_id):
    """Start report generation process."""
    report_id = secrets.token_hex(8)
    
    # Create report record
    report_data = {
        'id': report_id,
        'user_id': user_id,
        'project_id': config['project_id'],
        'template': config['template'],
        'format': config['format'],
        'title': config['title'],
        'status': 'generating',
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'config': config
    }
    
    # Save to database
    save_report_record(report_data)
    
    # Start generation in background (simulated)
    # In real implementation, this would be a background task
    simulate_report_generation(report_id, config)
    
    return report_id

def simulate_report_generation(report_id, config):
    """Simulate report generation process."""
    # In real implementation, this would generate actual reports
    import threading
    import time
    
    def generate():
        try:
            # Simulate generation phases
            phases = [
                ('Collecting data', 20),
                ('Processing vulnerabilities', 30),
                ('Generating content', 25),
                ('Formatting report', 15),
                ('Finalizing document', 10)
            ]
            
            progress = 0
            for phase, increment in phases:
                time.sleep(2)  # Simulate work
                progress += increment
                update_report_progress(report_id, progress, phase)
            
            # Mark as completed
            complete_report_generation(report_id, config)
            
        except Exception as e:
            logging.error(f"Report generation failed: {e}")
            mark_report_failed(report_id, str(e))
    
    thread = threading.Thread(target=generate)
    thread.daemon = True
    thread.start()

def complete_report_generation(report_id, config):
    """Complete report generation."""
    # Create a dummy file for demonstration
    format_ext = {
        'pdf': '.pdf',
        'html': '.html',
        'docx': '.docx',
        'json': '.json'
    }
    
    filename = f"report_{report_id}{format_ext.get(config['format'], '.pdf')}"
    
    # In real implementation, save actual generated report
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    # Create dummy content
    if config['format'] == 'json':
        content = {
            'report_id': report_id,
            'title': config['title'],
            'generated_at': datetime.now().isoformat(),
            'vulnerabilities': [
                {
                    'id': 'VULN-001',
                    'title': 'SQL Injection vulnerability',
                    'severity': 'critical',
                    'cvss': 9.8
                }
            ]
        }
        with open(file_path, 'w') as f:
            json.dump(content, f, indent=2)
    else:
        with open(file_path, 'w') as f:
            f.write(f"Sample {config['format'].upper()} report for {report_id}\n")
            f.write(f"Title: {config['title']}\n")
            f.write(f"Generated: {datetime.now()}\n")
    
    # Update report record
    update_report_completion(report_id, file_path, filename)

# Database helper functions (in real implementation, use actual database)
_reports_db = {}
_report_analytics = {}

def save_report_record(report_data):
    """Save report record to database."""
    _reports_db[report_data['id']] = report_data

def get_report_status(report_id, user_id):
    """Get report status."""
    report = _reports_db.get(report_id)
    if report and report['user_id'] == user_id:
        return report
    return None

def get_report_info(report_id, user_id):
    """Get report information."""
    return get_report_status(report_id, user_id)

def update_report_progress(report_id, progress, status):
    """Update report progress."""
    if report_id in _reports_db:
        _reports_db[report_id]['progress'] = progress
        _reports_db[report_id]['status'] = status

def mark_report_failed(report_id, error):
    """Mark report as failed."""
    if report_id in _reports_db:
        _reports_db[report_id]['status'] = 'failed'
        _reports_db[report_id]['error'] = error

def update_report_completion(report_id, file_path, filename):
    """Update report completion."""
    if report_id in _reports_db:
        _reports_db[report_id]['status'] = 'completed'
        _reports_db[report_id]['progress'] = 100
        _reports_db[report_id]['file_path'] = file_path
        _reports_db[report_id]['filename'] = filename
        _reports_db[report_id]['completed_at'] = datetime.now().isoformat()

def delete_report_record(report_id):
    """Delete report record."""
    if report_id in _reports_db:
        del _reports_db[report_id]

def increment_download_count(report_id):
    """Increment download count."""
    if report_id in _reports_db:
        _reports_db[report_id]['download_count'] = _reports_db[report_id].get('download_count', 0) + 1

def get_user_reports(user_id):
    """Get reports for user."""
    return [report for report in _reports_db.values() if report['user_id'] == user_id]

def get_report_analytics(user_id):
    """Get report analytics for user."""
    user_reports = get_user_reports(user_id)
    
    return {
        'total_reports': len(user_reports),
        'completed_reports': len([r for r in user_reports if r['status'] == 'completed']),
        'failed_reports': len([r for r in user_reports if r['status'] == 'failed']),
        'generating_reports': len([r for r in user_reports if r['status'] == 'generating']),
        'total_downloads': sum(r.get('download_count', 0) for r in user_reports),
        'popular_templates': {
            'technical': len([r for r in user_reports if r.get('template') == 'technical']),
            'executive': len([r for r in user_reports if r.get('template') == 'executive']),
            'compliance': len([r for r in user_reports if r.get('template') == 'compliance']),
            'remediation': len([r for r in user_reports if r.get('template') == 'remediation'])
        },
        'format_distribution': {
            'pdf': len([r for r in user_reports if r.get('format') == 'pdf']),
            'html': len([r for r in user_reports if r.get('format') == 'html']),
            'docx': len([r for r in user_reports if r.get('format') == 'docx']),
            'json': len([r for r in user_reports if r.get('format') == 'json'])
        }
    }

def get_mimetype(format_type):
    """Get MIME type for format."""
    mime_types = {
        'pdf': 'application/pdf',
        'html': 'text/html',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'json': 'application/json'
    }
    return mime_types.get(format_type, 'application/octet-stream')