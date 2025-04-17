from datetime import datetime
from app import db

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