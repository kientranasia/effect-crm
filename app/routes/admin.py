from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.models import User, Role, Permission, Setting, AuditLog
from app import db
from app.decorators import admin_required
from datetime import datetime, timedelta
from functools import wraps
import csv
import io
import ipaddress
from app.utils import log_audit
import os
from werkzeug.utils import secure_filename
from PIL import Image
import time
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import UserForm, RoleForm
from app.utils.decorators import permission_required

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@permission_required('user_view')
def index():
    """Admin dashboard with system overview"""
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_roles': Role.query.count()
    }
    
    # Define colors for different actions
    action_colors = {
        'create': 'success',
        'update': 'info',
        'delete': 'danger',
        'approve': 'primary',
        'suspend': 'warning',
        'login': 'secondary',
        'logout': 'secondary'
    }
    
    # Get recent activity logs
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    
    # Define admin navigation structure
    admin_nav = {
        'user_management': {
            'title': 'User Management',
            'icon': 'users',
            'url': url_for('admin.users')
        },
        'role_management': {
            'title': 'Role Management',
            'icon': 'user-shield',
            'url': url_for('admin.roles')
        },
        'system_settings': {
            'title': 'System Settings',
            'icon': 'cogs',
            'url': url_for('admin.settings'),
            'description': 'Configure system settings, email, and integration credentials'
        }
    }
    
    return render_template('admin/index.html', 
                         stats=stats, 
                         recent_logs=recent_logs,
                         action_colors=action_colors,
                         admin_nav=admin_nav,
                         active_page='dashboard')

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Admin settings page"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Update email settings
            Setting.set_value('smtp_server', data.get('smtp_server', ''))
            Setting.set_value('smtp_port', int(data.get('smtp_port', 587)))
            Setting.set_value('smtp_username', data.get('smtp_username', ''))
            Setting.set_value('smtp_password', data.get('smtp_password', ''))
            Setting.set_value('smtp_use_tls', data.get('smtp_use_tls', True))
            
            # Update API keys and credentials
            Setting.set_value('anthropic_api_key', data.get('anthropic_api_key', ''))
            Setting.set_value('openai_api_key', data.get('openai_api_key', ''))
            
            # Update credentials for 3rd party integrations
            credentials = data.get('credentials', {})
            for cred_name, cred_data in credentials.items():
                Setting.set_value(f'credential_{cred_name}', cred_data)
            
            db.session.commit()
            
            # Log the settings update
            log_audit(
                current_user.id,
                'update_settings',
                'Settings',
                None,
                'Updated system settings and credentials'
            )
            
            return jsonify({'status': 'success'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    # Get current settings
    settings = {
        'smtp_server': Setting.get_value('smtp_server', ''),
        'smtp_port': Setting.get_value('smtp_port', 587),
        'smtp_username': Setting.get_value('smtp_username', ''),
        'smtp_password': Setting.get_value('smtp_password', ''),
        'smtp_use_tls': Setting.get_value('smtp_use_tls', True),
        'anthropic_api_key': Setting.get_value('anthropic_api_key', ''),
        'openai_api_key': Setting.get_value('openai_api_key', ''),
        'credentials': {}
    }
    
    # Get all credential settings
    credential_settings = Setting.query.filter(Setting.key.startswith('credential_')).all()
    for cred in credential_settings:
        cred_name = cred.key.replace('credential_', '')
        settings['credentials'][cred_name] = cred.value
    
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/settings/system', methods=['POST'])
@login_required
@admin_required
def update_system_settings():
    """Update system configuration settings"""
    try:
        data = request.json
        
        # Update email settings
        Setting.set_value('smtp_server', data.get('smtp_server', ''))
        Setting.set_value('smtp_port', int(data.get('smtp_port', 587)))
        Setting.set_value('smtp_username', data.get('smtp_username', ''))
        Setting.set_value('smtp_password', data.get('smtp_password', ''))
        Setting.set_value('smtp_use_tls', data.get('use_tls', True))
        
        # Update API keys
        Setting.set_value('anthropic_api_key', data.get('anthropic_api_key', ''))
        Setting.set_value('openai_api_key', data.get('openai_api_key', ''))
        
        # Update credentials for 3rd party integrations
        credentials = data.get('credentials', {})
        for cred_name, cred_config in credentials.items():
            Setting.set_value(f'credential_{cred_name}', {
                'name': cred_config.get('name', ''),
                'type': cred_config.get('type', ''),
                'properties': cred_config.get('properties', {}),
                'oauth': cred_config.get('oauth', {}),
                'baseUrl': cred_config.get('baseUrl', ''),
                'authUrl': cred_config.get('authUrl', ''),
                'accessTokenUrl': cred_config.get('accessTokenUrl', ''),
                'clientId': cred_config.get('clientId', ''),
                'clientSecret': cred_config.get('clientSecret', ''),
                'scope': cred_config.get('scope', []),
                'authentication': cred_config.get('authentication', {}),
                'custom_fields': cred_config.get('custom_fields', {})
            })
        
        db.session.commit()
        
        # Log the action
        log_audit(
            user_id=current_user.id,
            action='update',
            entity_type='system_settings',
            entity_id=None,
            details='Updated system settings and credentials'
        )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/admin/roles')
@login_required
@permission_required('role_view')
def roles():
    """Role management page"""
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('admin/roles.html', roles=roles, permissions=permissions)

@admin_bp.route('/permissions')
@login_required
@admin_required
def permissions():
    """Permission management page"""
    permissions = Permission.query.all()
    return render_template('admin/permissions.html', permissions=permissions)

@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View audit logs with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    entity_type = request.args.get('entity_type')
    date_range = request.args.get('date_range')
    
    # Build query
    query = AuditLog.query
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if date_range:
        try:
            start_date, end_date = date_range.split(' - ')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(AuditLog.created_at.between(start_date, end_date))
        except:
            pass
    
    # Order by most recent first
    query = query.order_by(AuditLog.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page)
    logs = pagination.items
    
    # Get all users for filter dropdown
    users = User.query.all()
    
    return render_template('admin/audit_logs.html', 
                         logs=logs, 
                         pagination=pagination,
                         users=users)

@admin_bp.route('/roles/<int:role_id>')
@login_required
@admin_required
def get_role(role_id):
    """Get role details"""
    role = Role.query.get_or_404(role_id)
    return jsonify({
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'permissions': [p.id for p in role.permissions]
    })

@admin_bp.route('/admin/roles/create', methods=['GET', 'POST'])
@login_required
@permission_required('role_create')
def create_role():
    """Create a new role"""
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(role)
        db.session.commit()
        
        # Add permissions if provided
        if form.permissions.data:
            permissions = Permission.query.filter(Permission.id.in_(form.permissions.data)).all()
            role.permissions = permissions
            db.session.commit()
        
        flash('Role created successfully.', 'success')
        return redirect(url_for('admin.roles'))
    return render_template('admin/role_form.html', form=form, title='Create Role')

@admin_bp.route('/admin/roles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('role_edit')
def edit_role(id):
    """Edit an existing role"""
    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    form.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        # Update permissions
        if form.permissions.data:
            permissions = Permission.query.filter(Permission.id.in_(form.permissions.data)).all()
            role.permissions = permissions
        else:
            role.permissions = []
        db.session.commit()
        flash('Role updated successfully.', 'success')
        return redirect(url_for('admin.roles'))
    return render_template('admin/role_form.html', form=form, role=role, permissions=Permission.query.all(), title='Edit Role')

@admin_bp.route('/roles', methods=['POST'])
@login_required
@admin_required
def create_role_api():
    """Create a new role via API"""
    data = request.json
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'status': 'error', 'message': 'Role name is required'}), 400
        
    # Check if role name already exists
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'status': 'error', 'message': 'Role name already exists'}), 400
    
    try:
        role = Role(
            name=data['name'],
            description=data.get('description', ''),
        )
        db.session.add(role)
        db.session.commit()
        
        # Add permissions if provided
        if data.get('permissions'):
            permissions = Permission.query.filter(Permission.id.in_(data['permissions'])).all()
            role.permissions = permissions
            db.session.commit()
        
        # Log the action
        log_audit(
            user_id=current_user.id,
            action='create',
            entity_type='role',
            entity_id=role.id,
            details=f'Created role {role.name}'
        )
        
        return jsonify({
            'status': 'success',
            'role': {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': [p.id for p in role.permissions]
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/roles/<int:role_id>', methods=['PUT'])
@login_required
@admin_required
def update_role(role_id):
    """Update an existing role"""
    role = Role.query.get_or_404(role_id)
    data = request.json
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'status': 'error', 'message': 'Role name is required'}), 400
        
    # Check if new name already exists (excluding current role)
    existing_role = Role.query.filter_by(name=data['name']).first()
    if existing_role and existing_role.id != role_id:
        return jsonify({'status': 'error', 'message': 'Role name already exists'}), 400
    
    try:
        role.name = data['name']
        role.description = data.get('description', role.description)
        
        # Update permissions if provided
        if 'permissions' in data:
            permissions = Permission.query.filter(Permission.id.in_(data['permissions'])).all()
            role.permissions = permissions
        
        db.session.commit()
        
        # Log the action
        log_audit(
            user_id=current_user.id,
            action='update',
            entity_type='role',
            entity_id=role.id,
            details=f'Updated role {role.name}'
        )
        
        return jsonify({
            'status': 'success',
            'role': {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': [p.id for p in role.permissions]
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_role(role_id):
    """Delete a role"""
    role = Role.query.get_or_404(role_id)
    
    # Don't allow deleting the admin role
    if role.name == 'admin':
        return jsonify({'status': 'error', 'message': 'Cannot delete the admin role'}), 400
    
    try:
        # First remove all permissions from the role
        role.permissions = []
        db.session.commit()
        
        # Log the action before deletion
        log_audit(
            user_id=current_user.id,
            action='delete',
            entity_type='role',
            entity_id=role.id,
            details=f'Deleted role {role.name}'
        )
        
        # Now delete the role
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/api-keys', methods=['POST'])
@login_required
@admin_required
def generate_api_key():
    """Generate a new API key"""
    # Implementation for API key generation
    pass

@admin_bp.route('/api-keys/<key_id>', methods=['DELETE'])
@login_required
@admin_required
def revoke_api_key(key_id):
    """Revoke an API key"""
    # Implementation for API key revocation
    pass

@admin_bp.route('/webhooks', methods=['POST'])
@login_required
@admin_required
def create_webhook():
    """Create a new webhook"""
    # Implementation for webhook creation
    pass

@admin_bp.route('/webhooks/<webhook_id>', methods=['PUT'])
@login_required
@admin_required
def update_webhook(webhook_id):
    """Update an existing webhook"""
    # Implementation for webhook update
    pass

@admin_bp.route('/webhooks/<webhook_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_webhook(webhook_id):
    """Delete a webhook"""
    # Implementation for webhook deletion
    pass

@admin_bp.route('/admin/users')
@login_required
@permission_required('user_view')
def users():
    """User management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.email.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%'))
        )
    
    if role_filter:
        query = query.filter(User.role_id == role_filter)
    
    pagination = query.paginate(page=page, per_page=10)
    users = pagination.items
    roles = Role.query.all()
    
    return render_template('admin/users.html', 
                         users=users,
                         pagination=pagination,
                         roles=roles)

@admin_bp.route('/admin/users/create', methods=['GET', 'POST'])
@login_required
@permission_required('user_create')
def create_user():
    roles = Role.query.all()
    form = UserForm(is_create=True)
    form.role_id.choices = [(role.id, role.name.title()) for role in roles]
    if form.validate_on_submit():
        # Check for duplicate email
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/user_form.html', form=form, roles=roles, title='Create User')
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role_id=form.role_id.data,
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, roles=roles, title='Create User')

@admin_bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('user_edit')
def edit_user(id):
    """Edit an existing user"""
    user = User.query.get_or_404(id)
    roles = Role.query.all()
    form = UserForm(obj=user, is_create=False)
    form.role_id.choices = [(role.id, role.name.title()) for role in roles]
    if form.validate_on_submit():
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role_id = form.role_id.data
        user.is_active = bool(form.is_active.data)
        user.is_approved = bool(form.is_approved.data)
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, user=user, roles=roles, title='Edit User')

@admin_bp.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('user_delete')
def delete_user(id):
    """Delete a user"""
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    """Approve a user"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.is_approved = True
        db.session.commit()
        log_audit(
            user_id=current_user.id,
            action='approve',
            entity_type='user',
            entity_id=user.id,
            details={'email': user.email}
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Update admin settings"""
    try:
        data = request.json
        
        # Update user approval settings
        Setting.set_value('user_approval_required', data.get('user_approval_required', True))
        
        db.session.commit()
        log_audit(
            user_id=current_user.id,
            action='update',
            entity_type='settings',
            entity_id=0,
            details=data
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/security-settings')
@login_required
@admin_required
def security_settings():
    """Security settings page"""
    settings = {
        'password_min_length': Setting.get_value('password_min_length', 8),
        'password_require_uppercase': Setting.get_value('password_require_uppercase', True),
        'password_require_lowercase': Setting.get_value('password_require_lowercase', True),
        'password_require_number': Setting.get_value('password_require_number', True),
        'password_require_special': Setting.get_value('password_require_special', True),
        'password_expiry_days': Setting.get_value('password_expiry_days', 90),
        'account_lockout_enabled': Setting.get_value('account_lockout_enabled', True),
        'account_lockout_attempts': Setting.get_value('account_lockout_attempts', 5),
        'account_lockout_duration': Setting.get_value('account_lockout_duration', 30),
        'session_timeout': Setting.get_value('session_timeout', 30),
        'require_2fa': Setting.get_value('require_2fa', False),
        'allowed_ip_ranges': Setting.get_value('allowed_ip_ranges', ''),
    }
    
    return render_template('admin/security_settings.html', 
                         settings=settings,
                         active_page='security_settings',
                         active_section='security')

@admin_bp.route('/security-settings/update', methods=['POST'])
@login_required
@admin_required
def update_security_settings():
    try:
        data = request.get_json()
        
        # Validate numeric fields
        numeric_fields = {
            'password_min_length': (8, 32),
            'password_expiry_days': (0, None),
            'account_lockout_attempts': (1, None),
            'account_lockout_duration': (1, None),
            'session_timeout': (5, None)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            value = int(data.get(field, 0))
            if value < min_val or (max_val and value > max_val):
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid value for {field}. Must be between {min_val} and {max_val if max_val else "unlimited"}'
                }), 400
        
        # Validate IP ranges if provided
        ip_ranges = data.get('allowed_ip_ranges', '').strip()
        if ip_ranges:
            for ip_range in ip_ranges.split('\n'):
                ip_range = ip_range.strip()
                if ip_range:
                    try:
                        ipaddress.ip_network(ip_range)
                    except ValueError:
                        return jsonify({
                            'status': 'error',
                            'message': f'Invalid IP range format: {ip_range}'
                        }), 400
        
        # Update settings in database
        settings = {
            'password_min_length': int(data['password_min_length']),
            'password_expiry_days': int(data['password_expiry_days']),
            'password_require_uppercase': bool(data['password_require_uppercase']),
            'password_require_lowercase': bool(data['password_require_lowercase']),
            'password_require_number': bool(data['password_require_number']),
            'password_require_special': bool(data['password_require_special']),
            'account_lockout_enabled': bool(data['account_lockout_enabled']),
            'account_lockout_attempts': int(data['account_lockout_attempts']),
            'account_lockout_duration': int(data['account_lockout_duration']),
            'session_timeout': int(data['session_timeout']),
            'require_2fa': bool(data['require_2fa']),
            'allowed_ip_ranges': data['allowed_ip_ranges']
        }
        
        # Update each setting in the database
        for key, value in settings.items():
            Setting.query.filter_by(key=key).update({'value': str(value)})
            
        db.session.commit()
        
        # Log the security settings update
        log_audit(
            current_user.id,
            'update_security_settings',
            'SecuritySettings',
            None,
            'Updated security settings'
        )
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'update_profile':
                # Update basic info
                current_user.first_name = request.form.get('first_name')
                current_user.last_name = request.form.get('last_name')
                current_user.email = request.form.get('email')
                
                db.session.commit()
                
                log_audit(
                    user_id=current_user.id,
                    action='update_profile',
                    entity_type='user',
                    entity_id=current_user.id,
                    details='Updated profile information'
                )
                
                flash('Profile updated successfully.', 'success')
                
            elif action == 'change_password':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect.', 'error')
                    return redirect(url_for('admin.profile'))
                
                if new_password != confirm_password:
                    flash('New passwords do not match.', 'error')
                    return redirect(url_for('admin.profile'))
                
                current_user.set_password(new_password)
                db.session.commit()
                
                log_audit(
                    user_id=current_user.id,
                    action='change_password',
                    entity_type='user',
                    entity_id=current_user.id,
                    details='Changed password'
                )
                
                flash('Password changed successfully.', 'success')
                
            elif action == 'upload_avatar':
                if 'avatar' not in request.files:
                    flash('No file uploaded.', 'error')
                    return redirect(url_for('admin.profile'))
                
                avatar = request.files['avatar']
                if avatar.filename == '':
                    flash('No file selected.', 'error')
                    return redirect(url_for('admin.profile'))
                
                if avatar and allowed_file(avatar.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                    filename = secure_filename(f"avatar_{current_user.id}_{int(time.time())}{os.path.splitext(avatar.filename)[1]}")
                    filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars', filename)
                    
                    # Save and resize image
                    try:
                        img = Image.open(avatar)
                        img.thumbnail((200, 200))  # Resize to max 200x200 while maintaining aspect ratio
                        img.save(filepath)
                        
                        # Update user's avatar in database
                        current_user.avatar = filename
                        db.session.commit()
                        
                        flash('Avatar updated successfully', 'success')
                        log_audit(current_user.id, 'update_avatar', 'user', current_user.id, 
                                 {'filename': filename}, request.remote_addr, request.user_agent.string)
                    except Exception as e:
                        flash('Error processing image', 'error')
                        current_app.logger.error(f"Avatar upload error: {str(e)}")
                    
                    return redirect(url_for('admin.profile'))
                else:
                    flash('Invalid file type', 'error')
            
            return redirect(url_for('admin.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            return redirect(url_for('admin.profile'))
    
    return render_template('admin/profile.html')

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions 

@admin_bp.route('/update-account-settings', methods=['GET', 'POST'])
@login_required
def update_account_settings():
    """Update user account settings"""
    if request.method == 'GET':
        return render_template('admin/account_settings.html', active_page='account_settings')
        
    try:
        # Update profile information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        # Check if email is being changed and if it already exists
        if email != current_user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Email address is already in use.', 'danger')
                return redirect(url_for('admin.update_account_settings'))
        
        # Update user information
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        
        # Handle password change if requested
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            # Verify current password
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('admin.update_account_settings'))
            
            # Verify new password matches confirmation
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('admin.update_account_settings'))
            
            # Update password
            current_user.set_password(new_password)
            
            # Log the password change
            log_audit(
                current_user.id,
                'change_password',
                'User',
                current_user.id,
                'Changed password'
            )
            
            flash('Password updated successfully.', 'success')
            return redirect(url_for('auth.logout'))
        
        # Save changes
        db.session.commit()
        
        # Log the profile update
        log_audit(
            current_user.id,
            'update_profile',
            'User',
            current_user.id,
            'Updated profile information'
        )
        
        flash('Account settings updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating account settings: {str(e)}', 'danger')
    
    return redirect(url_for('admin.update_account_settings'))

@admin_bp.route('/setup', methods=['GET', 'POST'])
def setup_admin():
    """Initial setup to create the first admin user"""
    # Check if any admin user exists
    if User.query.filter_by(is_admin=True).first():
        flash('Admin user already exists.', 'warning')
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if not email or not password or not name:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin.setup_admin'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('admin.setup_admin'))
            
        user = User(
            email=email,
            name=name,
            password=generate_password_hash(password),
            is_admin=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Admin user created successfully.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('admin/setup.html')

@admin_bp.route('/admin/users/bulk_action', methods=['POST'])
@login_required
@permission_required('user_edit')
def bulk_user_action():
    data = request.get_json()
    action = data.get('action')
    user_ids = data.get('user_ids', [])
    if not action or not user_ids:
        return jsonify({'status': 'error', 'message': 'No action or users selected.'}), 400
    try:
        users = User.query.filter(User.id.in_(user_ids)).all()
        count = 0
        for user in users:
            if user.id == current_user.id:
                continue  # Prevent self-action
            if action == 'activate':
                user.is_active = True
                count += 1
            elif action == 'deactivate':
                user.is_active = False
                count += 1
            elif action == 'delete':
                db.session.delete(user)
                count += 1
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'{count} users updated.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500 

@admin_bp.route('/admin/users/<int:id>')
@login_required
@permission_required('user_view')
def user_detail(id):
    user = User.query.get_or_404(id)
    audit_logs = AuditLog.query.filter_by(entity_type='user', entity_id=user.id).order_by(AuditLog.created_at.desc()).limit(20).all()
    return render_template('admin/user_detail.html', user=user, audit_logs=audit_logs) 