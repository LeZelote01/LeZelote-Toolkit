#!/usr/bin/env python3
"""
Authentication Routes for Pentest-USB Toolkit Web Interface
===========================================================

Handles user authentication, session management, and security.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
import logging

# Create blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Default credentials (should be changed in production)
DEFAULT_USERS = {
    'admin': {
        'password_hash': generate_password_hash('pentest123'),
        'role': 'admin',
        'full_name': 'Administrator',
        'email': 'admin@pentest-usb.local'
    },
    'demo': {
        'password_hash': generate_password_hash('demo'),
        'role': 'demo',
        'full_name': 'Demo User',
        'email': 'demo@pentest-usb.local'
    }
}

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'GET':
        # If already authenticated, redirect to dashboard
        if session.get('authenticated'):
            return redirect(url_for('index'))
        return render_template('login.html')
    
    # Handle POST request
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    remember_me = request.form.get('remember_me') == 'on'
    
    if not username or not password:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': 'Username and password are required'})
        flash('Username and password are required', 'error')
        return render_template('login.html')
    
    # Check credentials
    user_info = DEFAULT_USERS.get(username.lower())
    if user_info and check_password_hash(user_info['password_hash'], password):
        # Successful authentication
        session_id = secrets.token_hex(32)
        
        session['authenticated'] = True
        session['user_id'] = username.lower()
        session['username'] = user_info['full_name']
        session['role'] = user_info['role']
        session['email'] = user_info['email']
        session['session_id'] = session_id
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = datetime.now().isoformat()
        
        if remember_me:
            session.permanent = True
        
        # Log successful login
        logging.info(f"User {username} logged in successfully from {request.remote_addr}")
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'redirect': url_for('index')
            })
        
        flash('Login successful! Welcome back.', 'success')
        return redirect(url_for('index'))
    
    else:
        # Failed authentication
        logging.warning(f"Failed login attempt for user {username} from {request.remote_addr}")
        
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': 'Invalid username or password'})
        
        flash('Invalid username or password', 'error')
        return render_template('login.html')

@bp.route('/demo-login', methods=['POST'])
def demo_login():
    """Handle demo user login."""
    try:
        # Set up demo session
        session_id = secrets.token_hex(32)
        
        session['authenticated'] = True
        session['user_id'] = 'demo'
        session['username'] = 'Demo User'
        session['role'] = 'demo'
        session['email'] = 'demo@pentest-usb.local'
        session['session_id'] = session_id
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = datetime.now().isoformat()
        session['demo_mode'] = True
        
        # Demo sessions are shorter
        session.permanent = False
        
        logging.info(f"Demo user logged in from {request.remote_addr}")
        
        return jsonify({
            'success': True,
            'message': 'Demo access granted',
            'redirect': url_for('index')
        })
        
    except Exception as e:
        logging.error(f"Demo login error: {e}")
        return jsonify({'success': False, 'message': 'Demo login failed'}), 500

@bp.route('/logout')
def logout():
    """Handle user logout."""
    username = session.get('username', 'Unknown')
    
    # Clear session
    session.clear()
    
    logging.info(f"User {username} logged out")
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests."""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    email = request.form.get('email', '').strip()
    
    if not email:
        flash('Email address is required', 'error')
        return render_template('forgot_password.html')
    
    # In a real application, send password reset email
    # For now, just show default credentials
    flash('Password reset instructions sent! Default credentials: admin/pentest123', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile')
def profile():
    """Show user profile page."""
    if not session.get('authenticated'):
        return redirect(url_for('auth.login'))
    
    user_info = {
        'username': session.get('username'),
        'email': session.get('email'),
        'role': session.get('role'),
        'login_time': session.get('login_time'),
        'session_id': session.get('session_id'),
        'demo_mode': session.get('demo_mode', False)
    }
    
    return render_template('profile.html', user=user_info)

@bp.route('/change-password', methods=['POST'])
def change_password():
    """Handle password change requests."""
    if not session.get('authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    if session.get('role') == 'demo':
        return jsonify({'success': False, 'message': 'Password changes not allowed in demo mode'}), 403
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    if len(new_password) < 8:
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters long'}), 400
    
    # In a real application, verify current password and update
    # For now, just simulate success
    logging.info(f"Password changed for user {session.get('username')}")
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@bp.route('/check-session')
def check_session():
    """Check if session is still valid."""
    if not session.get('authenticated'):
        return jsonify({'authenticated': False})
    
    # Update last activity
    session['last_activity'] = datetime.now().isoformat()
    
    return jsonify({
        'authenticated': True,
        'username': session.get('username'),
        'role': session.get('role'),
        'demo_mode': session.get('demo_mode', False)
    })

@bp.route('/extend-session', methods=['POST'])
def extend_session():
    """Extend user session."""
    if not session.get('authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    # Update last activity and extend session
    session['last_activity'] = datetime.now().isoformat()
    session.permanent = True
    
    return jsonify({'success': True, 'message': 'Session extended'})

# Session management utilities
def is_authenticated():
    """Check if user is authenticated."""
    return session.get('authenticated', False)

def require_auth(f):
    """Decorator to require authentication."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(role):
    """Decorator to require specific role."""
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role')
            if user_role != role and user_role != 'admin':
                if request.headers.get('Content-Type') == 'application/json':
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('Insufficient permissions', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Context processor to make auth functions available in templates
@bp.app_context_processor
def inject_auth_functions():
    """Inject authentication functions into template context."""
    return {
        'is_authenticated': is_authenticated,
        'current_user_role': session.get('role'),
        'is_demo_mode': session.get('demo_mode', False)
    }