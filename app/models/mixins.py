from datetime import datetime
from app.extensions import db
from flask_login import current_user

class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to models"""
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Save the model instance to the database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model instance from the database"""
        db.session.delete(self)
        db.session.commit()

class PermissionMixin:
    """Mixin for adding permission-based access control to models"""
    
    @classmethod
    def can_view(cls):
        """Check if current user has permission to view this model"""
        if not current_user.is_authenticated:
            return False
        if current_user.is_admin:
            return True
        return current_user.has_permission(f'{cls.__tablename__}_view')
    
    @classmethod
    def can_create(cls):
        """Check if current user has permission to create this model"""
        if not current_user.is_authenticated:
            return False
        if current_user.is_admin:
            return True
        return current_user.has_permission(f'{cls.__tablename__}_create')
    
    def can_edit(self):
        """Check if current user has permission to edit this model instance"""
        if not current_user.is_authenticated:
            return False
        if current_user.is_admin:
            return True
        return current_user.has_permission(f'{self.__tablename__}_edit')
    
    def can_delete(self):
        """Check if current user has permission to delete this model instance"""
        if not current_user.is_authenticated:
            return False
        if current_user.is_admin:
            return True
        return current_user.has_permission(f'{self.__tablename__}_delete') 