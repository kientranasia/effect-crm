from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import bp
from app.models import User, Role, db
import logging

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Login attempt for email: {email}")  # Debug print
        
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"User found: {user.username}, is_active: {user.is_active}")  # Debug print
            if user.check_password(password):
                print("Password check passed")  # Debug print
                login_user(user, remember=True)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            else:
                print("Password check failed")  # Debug print
        else:
            print("User not found")  # Debug print
            
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('auth/register.html')
            
        # Get or create user role
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='Regular user')
            db.session.add(user_role)
            db.session.commit()
            
        user = User(
            username=username,
            email=email,
            role_id=user_role.id,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 