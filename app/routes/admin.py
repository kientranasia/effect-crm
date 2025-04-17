from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Role
from app import db
from app.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def index():
    """Redirect to admin settings page"""
    return redirect(url_for('admin.settings'))

@admin_bp.route('/admin/settings')
@login_required
@admin_required
def settings():
    # Get all users and roles
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/settings.html', users=users, roles=roles)

@admin_bp.route('/admin/users/approve/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'User {user.email} has been approved.', 'success')
    return redirect(url_for('admin.settings'))

@admin_bp.route('/admin/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    role_id = request.form.get('role_id')
    
    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'danger')
        return redirect(url_for('admin.settings'))
    
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role_id=role_id,
        is_approved=True,
        is_active=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash(f'User {email} has been created.', 'success')
    return redirect(url_for('admin.settings')) 