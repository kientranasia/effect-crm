"""
Flask application factory module.
"""
import os
from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager, csrf, mail
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .utils.filters import timeago

def create_app(config_name='default'):
    """Create and configure the Flask application.
    
    Args:
        config_name: The name of the configuration to use. Defaults to 'default'.
        
    Returns:
        The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'Please login again to confirm your identity.'
    login_manager.needs_refresh_message_category = 'info'
    
    # Register Jinja filters
    app.jinja_env.filters['timeago'] = timeago
    
    # Register blueprints
    from app.routes import main, auth, admin, organizations, contacts, interactions
    app.register_blueprint(main.main_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(organizations.organizations_bp)
    app.register_blueprint(contacts.contacts_bp)
    app.register_blueprint(interactions.interactions_bp)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import (
        User, Contact, Organization, Interaction, Activity,
        AuditLog, Permission, Role, Setting, SecuritySetting,
        Project
    )
    
    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Add datetime filter
    @app.template_filter('datetime')
    def format_datetime(value):
        if value is None:
            return ""
        return value.strftime('%Y-%m-%d %H:%M')
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user given the ID.
        
        Args:
            user_id: The ID of the user to load.
            
        Returns:
            The user object if found, None otherwise.
        """
        return User.query.get(int(user_id))
    
    # Add context processor for menu and datetime
    from app.utils.menu import get_user_menu
    @app.context_processor
    def inject_utils():
        return {
            'get_user_menu': get_user_menu,
            'now': datetime.now
        }
    
    return app 