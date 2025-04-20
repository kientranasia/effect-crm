from app.extensions import db

class SecuritySettings(db.Model):
    __tablename__ = 'security_settings'

    id = db.Column(db.Integer, primary_key=True)
    min_password_length = db.Column(db.Integer, nullable=False, default=8)
    require_uppercase = db.Column(db.Boolean, nullable=False, default=True)
    require_lowercase = db.Column(db.Boolean, nullable=False, default=True)
    require_numbers = db.Column(db.Boolean, nullable=False, default=True)
    require_special_chars = db.Column(db.Boolean, nullable=False, default=True)
    password_expiry_days = db.Column(db.Integer, nullable=False, default=90)
    max_login_attempts = db.Column(db.Integer, nullable=False, default=5)
    lockout_duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    session_timeout_minutes = db.Column(db.Integer, nullable=False, default=30)
    remember_me_days = db.Column(db.Integer, nullable=False, default=30)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<SecuritySettings id={self.id}>' 