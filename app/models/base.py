from datetime import datetime
from app.extensions import db

class BaseModel:
    """Base model class that provides common functionality for all models."""
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Save the model instance to the database."""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model instance from the database."""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by its ID."""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Get all instances of the model."""
        return cls.query.all()
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 