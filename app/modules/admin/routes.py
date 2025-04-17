from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Role
from datetime import datetime
from functools import wraps

bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You need to be an administrator to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin')
@login_required
def index():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    roles = Role.query.all()
    
    return render_template('admin/index.html', users=users, roles=roles)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
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

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role_id = request.form.get('role_id', type=int)
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.create_user'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('admin.create_user'))
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating user', 'danger')
            return redirect(url_for('admin.create_user'))
    
    roles = Role.query.all()
    return render_template('admin/user_form.html', roles=roles)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role_id = request.form.get('role_id', type=int)
        is_active = request.form.get('is_active') == 'on'
        new_password = request.form.get('password')
        
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
            
        # Check if email is taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('Email already exists', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        try:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.role_id = role_id
            user.is_active = is_active
            
            if new_password:
                user.set_password(new_password)
            
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating user', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
    
    roles = Role.query.all()
    return render_template('admin/user_form.html', user=user, roles=roles)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user', 'danger')
    
    return redirect(url_for('admin.users')) 