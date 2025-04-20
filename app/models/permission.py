from datetime import datetime
from app.extensions import db

# Association table for Role-Permission many-to-many relationship
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Permission(db.Model):
    """Model for storing system permissions"""
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Many-to-many relationship with roles
    assigned_roles = db.relationship('Role', secondary=role_permissions,
                                   backref=db.backref('assigned_permissions', lazy='dynamic'))

    def __repr__(self):
        return f'<Permission {self.name}>' 