from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role, Permission
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
            
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_approved=False,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/first-time-setup', methods=['GET', 'POST'])
def first_time_setup():
    # Check if any user exists
    if User.query.first():
        flash('Setup has already been completed.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if not all([email, password, confirm_password, first_name, last_name]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.first_time_setup'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.first_time_setup'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.first_time_setup'))
            
        # Create admin role if it doesn't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(
                name='admin',
                description='Administrator with full access'
            )
            db.session.add(admin_role)
            db.session.commit()
            
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=True,
            role_id=admin_role.id
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Admin account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/first_time_setup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    # Check if any user exists, if not redirect to first-time setup
    if not User.query.first():
        return redirect(url_for('auth.first_time_setup'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_active:
            flash('Your account is inactive. Please contact an administrator.', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_approved:
            flash('Your account is pending approval. Please wait for administrator approval.', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        
        # Get the next page from the query parameters
        next_page = request.args.get('next')
        # Make sure the next URL is safe (relative to our domain)
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
            
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index')) 