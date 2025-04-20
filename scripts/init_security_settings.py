from app import create_app
from app.extensions import db
from app.models.security_settings import SecuritySettings

def init_security_settings():
    """Initialize default security settings."""
    app = create_app()
    with app.app_context():
        # Check if security settings already exist
        existing_settings = SecuritySettings.query.first()
        if existing_settings:
            print("Security settings already exist. Skipping initialization.")
            return

        # Create default security settings
        settings = SecuritySettings(
            min_password_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_numbers=True,
            require_special_chars=True,
            password_expiry_days=90,
            max_login_attempts=5,
            lockout_duration_minutes=30,
            session_timeout_minutes=30,
            remember_me_days=30
        )

        db.session.add(settings)
        db.session.commit()
        print("Security settings initialized successfully.")

if __name__ == '__main__':
    init_security_settings() 