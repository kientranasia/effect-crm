from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
import os
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Handle both string config names and config class objects
    if isinstance(config_class, str):
        from config import config
        app.config.from_object(config[config_class])
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.main import main_bp
    from app.routes.leads import leads_bp
    from app.routes.organizations import organizations_bp
    from app.routes.customers import customers_bp
    from app.modules import interactions

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(interactions.bp, url_prefix='/interactions')

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Custom Jinja2 filters
    @app.template_filter('timeago')
    def timeago(date):
        """Convert a datetime to a human-readable time ago string."""
        if not date:
            return ""
            
        now = datetime.utcnow()
        diff = now - date
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif seconds < 31536000:
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years != 1 else ''} ago"

    return app

from app.models import User 