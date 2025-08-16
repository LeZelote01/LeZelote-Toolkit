#!/usr/bin/env python3
"""
Settings Management Routes for Pentest-USB Toolkit Web Interface
================================================================

Handles application settings, user preferences, and configuration.
"""

from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from datetime import datetime
import json
import logging
from .auth import require_auth, require_role

# Create blueprint
bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route('/')
@require_auth
def settings_page():
    """Show settings management page."""
    user_settings = get_user_settings(session.get('user_id'))
    system_settings = get_system_settings() if session.get('role') == 'admin' else {}
    
    return render_template('settings.html', 
                         user_settings=user_settings,
                         system_settings=system_settings)

@bp.route('/update', methods=['POST'])
@require_auth
def update_settings():
    """Update user settings."""
    try:
        data = request.get_json() if request.is_json else request.form
        category = data.get('category', 'general')
        
        # Validate category
        valid_categories = ['general', 'security', 'scanning', 'reporting', 'notifications']
        if category not in valid_categories:
            return jsonify({'success': False, 'message': 'Invalid settings category'}), 400
        
        # Get current settings
        user_id = session.get('user_id')
        current_settings = get_user_settings(user_id)
        
        # Update settings based on category
        if category == 'general':
            settings_update = {
                'timezone': data.get('timezone'),
                'date_format': data.get('date_format'),
                'theme': data.get('theme'),
                'language': data.get('language'),
                'auto_save': data.get('auto_save') == 'on' or data.get('auto_save') is True,
                'confirm_actions': data.get('confirm_actions') == 'on' or data.get('confirm_actions') is True
            }
            
        elif category == 'security':
            settings_update = {
                'session_timeout': int(data.get('session_timeout', 60)),
                'max_login_attempts': int(data.get('max_login_attempts', 3)),
                'enable_audit_log': data.get('enable_audit_log') == 'on' or data.get('enable_audit_log') is True,
                'require_strong_password': data.get('require_strong_password') == 'on' or data.get('require_strong_password') is True,
                'enable_two_factor': data.get('enable_two_factor') == 'on' or data.get('enable_two_factor') is True
            }
            
        elif category == 'scanning':
            settings_update = {
                'default_scan_type': data.get('default_scan_type'),
                'max_concurrent_scans': int(data.get('max_concurrent_scans', 3)),
                'scan_timeout': int(data.get('scan_timeout', 30)),
                'default_ports': data.get('default_ports'),
                'auto_save_results': data.get('auto_save_results') == 'on' or data.get('auto_save_results') is True,
                'enable_stealth_mode': data.get('enable_stealth_mode') == 'on' or data.get('enable_stealth_mode') is True
            }
            
        elif category == 'reporting':
            settings_update = {
                'default_report_format': data.get('default_report_format'),
                'report_template': data.get('report_template'),
                'company_name': data.get('company_name'),
                'report_author': data.get('report_author'),
                'include_executive_summary': data.get('include_executive_summary') == 'on' or data.get('include_executive_summary') is True,
                'include_screenshots': data.get('include_screenshots') == 'on' or data.get('include_screenshots') is True
            }
            
        elif category == 'notifications':
            settings_update = {
                'enable_notifications': data.get('enable_notifications') == 'on' or data.get('enable_notifications') is True,
                'scan_completion_notify': data.get('scan_completion_notify') == 'on' or data.get('scan_completion_notify') is True,
                'vuln_found_notify': data.get('vuln_found_notify') == 'on' or data.get('vuln_found_notify') is True,
                'system_alerts_notify': data.get('system_alerts_notify') == 'on' or data.get('system_alerts_notify') is True,
                'notification_email': data.get('notification_email'),
                'enable_email_notify': data.get('enable_email_notify') == 'on' or data.get('enable_email_notify') is True
            }
        
        # Filter None values
        settings_update = {k: v for k, v in settings_update.items() if v is not None}
        
        # Update settings
        update_user_settings(user_id, category, settings_update)
        
        return jsonify({
            'success': True,
            'message': f'{category.title()} settings updated successfully'
        })
        
    except Exception as e:
        logging.error(f"Settings update error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/reset', methods=['POST'])
@require_auth
def reset_settings():
    """Reset settings to defaults."""
    try:
        category = request.json.get('category', 'all') if request.is_json else request.form.get('category', 'all')
        user_id = session.get('user_id')
        
        if category == 'all':
            reset_all_user_settings(user_id)
        else:
            reset_category_settings(user_id, category)
        
        return jsonify({
            'success': True,
            'message': 'Settings reset to defaults successfully'
        })
        
    except Exception as e:
        logging.error(f"Settings reset error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/export', methods=['GET'])
@require_auth
def export_settings():
    """Export user settings."""
    try:
        user_id = session.get('user_id')
        settings = get_user_settings(user_id)
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'user_id': user_id,
            'settings': settings,
            'version': '1.0.0'
        }
        
        # Return JSON response with attachment headers
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=pentest_settings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        logging.error(f"Settings export error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/import', methods=['POST'])
@require_auth
def import_settings():
    """Import user settings."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'message': 'Invalid file format. JSON required.'}), 400
        
        # Read and parse JSON
        try:
            content = file.read().decode('utf-8')
            import_data = json.loads(content)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return jsonify({'success': False, 'message': 'Invalid JSON file'}), 400
        
        # Validate import data structure
        if 'settings' not in import_data:
            return jsonify({'success': False, 'message': 'Invalid settings file format'}), 400
        
        # Import settings
        user_id = session.get('user_id')
        import_user_settings(user_id, import_data['settings'])
        
        return jsonify({
            'success': True,
            'message': 'Settings imported successfully'
        })
        
    except Exception as e:
        logging.error(f"Settings import error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/system', methods=['GET', 'POST'])
@require_auth
@require_role('admin')
def system_settings():
    """Manage system-wide settings (admin only)."""
    if request.method == 'GET':
        try:
            settings = get_system_settings()
            return jsonify({'success': True, 'settings': settings})
            
        except Exception as e:
            logging.error(f"System settings get error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate system settings
            system_update = {}
            
            # Security settings
            if 'max_memory_usage' in data:
                system_update['max_memory_usage'] = max(50, min(95, int(data['max_memory_usage'])))
            
            if 'max_cpu_usage' in data:
                system_update['max_cpu_usage'] = max(50, min(95, int(data['max_cpu_usage'])))
            
            if 'log_level' in data:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if data['log_level'] in valid_levels:
                    system_update['log_level'] = data['log_level']
            
            if 'log_retention' in data:
                system_update['log_retention'] = max(1, min(365, int(data['log_retention'])))
            
            # Boolean settings
            bool_settings = ['enable_debug_mode', 'enable_performance_metrics']
            for setting in bool_settings:
                if setting in data:
                    system_update[setting] = bool(data[setting])
            
            # Update system settings
            update_system_settings(system_update)
            
            return jsonify({
                'success': True,
                'message': 'System settings updated successfully'
            })
            
        except Exception as e:
            logging.error(f"System settings update error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/tools', methods=['GET', 'POST'])
@require_auth
def tool_settings():
    """Manage tool configuration."""
    if request.method == 'GET':
        try:
            tools_config = get_tools_configuration(session.get('user_id'))
            return jsonify({'success': True, 'tools': tools_config})
            
        except Exception as e:
            logging.error(f"Tools config get error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            user_id = session.get('user_id')
            
            # Update tool enablement
            tools_update = {}
            available_tools = [
                'nmap', 'sqlmap', 'zap', 'nikto', 'metasploit', 
                'nessus', 'openvas', 'burp', 'hydra', 'john'
            ]
            
            for tool in available_tools:
                enable_key = f'enable_{tool}'
                if enable_key in data:
                    tools_update[tool] = bool(data[enable_key])
            
            # Update tools configuration
            update_tools_configuration(user_id, tools_update)
            
            return jsonify({
                'success': True,
                'message': 'Tools configuration updated successfully'
            })
            
        except Exception as e:
            logging.error(f"Tools config update error: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/maintenance', methods=['POST'])
@require_auth
@require_role('admin')
def maintenance_actions():
    """Perform maintenance actions (admin only)."""
    try:
        action = request.json.get('action') if request.is_json else request.form.get('action')
        
        if action == 'clear_cache':
            # Clear application cache
            clear_application_cache()
            message = 'Application cache cleared successfully'
            
        elif action == 'cleanup_logs':
            # Clean up old log files
            cleanup_old_logs()
            message = 'Old log files cleaned up successfully'
            
        elif action == 'optimize_db':
            # Optimize database
            optimize_database()
            message = 'Database optimized successfully'
            
        elif action == 'backup_settings':
            # Backup system settings
            backup_path = backup_system_settings()
            message = f'Settings backed up to {backup_path}'
            
        else:
            return jsonify({'success': False, 'message': 'Unknown maintenance action'}), 400
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        logging.error(f"Maintenance action error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Database helper functions (mock implementation)
_user_settings = {}
_system_settings = {
    'max_memory_usage': 80,
    'max_cpu_usage': 80,
    'log_level': 'INFO',
    'log_retention': 30,
    'enable_debug_mode': False,
    'enable_performance_metrics': True
}
_tools_config = {}

def get_user_settings(user_id):
    """Get user settings."""
    default_settings = {
        'general': {
            'timezone': 'UTC',
            'date_format': 'MM/DD/YYYY',
            'theme': 'light',
            'language': 'en',
            'auto_save': True,
            'confirm_actions': True
        },
        'security': {
            'session_timeout': 60,
            'max_login_attempts': 3,
            'enable_audit_log': True,
            'require_strong_password': True,
            'enable_two_factor': False
        },
        'scanning': {
            'default_scan_type': 'quick',
            'max_concurrent_scans': 3,
            'scan_timeout': 30,
            'default_ports': '1-1000',
            'auto_save_results': True,
            'enable_stealth_mode': False
        },
        'reporting': {
            'default_report_format': 'pdf',
            'report_template': 'technical',
            'company_name': '',
            'report_author': '',
            'include_executive_summary': True,
            'include_screenshots': True
        },
        'notifications': {
            'enable_notifications': True,
            'scan_completion_notify': True,
            'vuln_found_notify': True,
            'system_alerts_notify': True,
            'notification_email': '',
            'enable_email_notify': False
        }
    }
    
    return _user_settings.get(user_id, default_settings)

def update_user_settings(user_id, category, settings_update):
    """Update user settings."""
    if user_id not in _user_settings:
        _user_settings[user_id] = get_user_settings(user_id)
    
    if category not in _user_settings[user_id]:
        _user_settings[user_id][category] = {}
    
    _user_settings[user_id][category].update(settings_update)

def reset_all_user_settings(user_id):
    """Reset all user settings."""
    if user_id in _user_settings:
        del _user_settings[user_id]

def reset_category_settings(user_id, category):
    """Reset category settings."""
    if user_id in _user_settings and category in _user_settings[user_id]:
        del _user_settings[user_id][category]

def import_user_settings(user_id, settings):
    """Import user settings."""
    _user_settings[user_id] = settings

def get_system_settings():
    """Get system settings."""
    return _system_settings.copy()

def update_system_settings(settings_update):
    """Update system settings."""
    _system_settings.update(settings_update)

def get_tools_configuration(user_id):
    """Get tools configuration."""
    default_tools = {
        'nmap': True,
        'sqlmap': True,
        'zap': True,
        'nikto': True,
        'metasploit': True,
        'nessus': False,
        'openvas': False,
        'burp': False,
        'hydra': True,
        'john': True
    }
    
    return _tools_config.get(user_id, default_tools)

def update_tools_configuration(user_id, tools_update):
    """Update tools configuration."""
    if user_id not in _tools_config:
        _tools_config[user_id] = get_tools_configuration(user_id)
    
    _tools_config[user_id].update(tools_update)

# Maintenance functions
def clear_application_cache():
    """Clear application cache."""
    # Mock implementation
    pass

def cleanup_old_logs():
    """Clean up old log files."""
    # Mock implementation
    pass

def optimize_database():
    """Optimize database."""
    # Mock implementation
    pass

def backup_system_settings():
    """Backup system settings."""
    # Mock implementation
    return '/tmp/settings_backup.json'