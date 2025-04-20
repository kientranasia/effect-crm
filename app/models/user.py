from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Foreign keys
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.role and self.role.name == role_name

    def has_permission(self, permission_name):
        """Check if user has a specific permission"""
        if self.is_admin:
            return True
        if not self.role:
            return False
        return any(p.name == permission_name for p in self.role.permissions)

    def has_any_permission(self, permission_names):
        """Check if user has any of the specified permissions"""
        if self.is_admin:
            return True
        if not self.role:
            return False
        return any(p.name in permission_names for p in self.role.permissions)

    def has_all_permissions(self, permission_names):
        """Check if user has all specified permissions"""
        if self.is_admin:
            return True
        if not self.role:
            return False
        user_permissions = {p.name for p in self.role.permissions}
        return all(name in user_permissions for name in permission_names)

    def __repr__(self):
        return f'<User {self.email}>' 