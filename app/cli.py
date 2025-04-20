import click
from flask.cli import with_appcontext
from app import db
from app.models import User, Role, Permission
from werkzeug.security import generate_password_hash
from datetime import datetime

def register_commands(app):
    """Register CLI commands with the Flask application."""
    app.cli.add_command(create_test_user)
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_admin_password)

@click.command('init-db')
@click.option('--admin-email', prompt='Admin email', help='Email for the admin account')
@click.option('--admin-password', prompt='Admin password', hide_input=True, confirmation_prompt=True, help='Password for the admin account')
@click.option('--admin-name', prompt='Admin name', help='Full name for the admin account')
@with_appcontext
def init_db_command(admin_email, admin_password, admin_name):
    """Initialize the database with an admin account."""
    # Create tables
    db.create_all()
    
    # Check if admin role exists
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator with full access')
        db.session.add(admin_role)
        db.session.commit()
    
    # Check if admin user exists
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            first_name=admin_name.split()[0] if ' ' in admin_name else admin_name,
            last_name=admin_name.split()[1] if ' ' in admin_name else '',
            is_active=True,
            is_admin=True,
            is_approved=True,
            role_id=admin_role.id,
            created_at=datetime.utcnow()
        )
        db.session.add(admin_user)
        db.session.commit()
        click.echo(f'Admin account created: {admin_email}')
    else:
        click.echo(f'Admin account already exists: {admin_email}')
    
    click.echo('Database initialized successfully!')

@click.command('create-test-user')
@click.option('--email', default='test@example.com', help='Email for the test user')
@click.option('--password', default='password123', help='Password for the test user')
@with_appcontext
def create_test_user(email, password):
    """Create a test user with the given email and password."""
    user = User.query.filter_by(email=email).first()
    if user:
        click.echo(f'User {email} already exists')
        return

    user = User(
        email=email,
        first_name='Test',
        last_name='User'
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    click.echo(f'Created test user {email} with password {password}')

@click.command('reset-admin-password')
@click.argument('email')
@click.argument('new_password')
@with_appcontext
def reset_admin_password(email, new_password):
    """Reset admin user password."""
    user = User.query.filter_by(email=email).first()
    if not user:
        click.echo(f'User with email {email} not found.')
        return
    
    # Set the new password using the User model's method
    user.set_password(new_password)
    
    # Ensure user is active and approved
    user.is_active = True
    user.is_approved = True
    
    try:
        db.session.commit()
        click.echo(f'Password reset successful for user {email}')
        click.echo('User status:')
        click.echo(f'- Active: {user.is_active}')
        click.echo(f'- Approved: {user.is_approved}')
        click.echo(f'- Admin: {user.is_admin}')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error resetting password: {str(e)}')
        return 