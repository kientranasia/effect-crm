from app import db
from datetime import datetime

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(64))
    website = db.Column(db.String(120))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customers = db.relationship('Customer', backref='organization', lazy=True)

    def __repr__(self):
        return f'<Organization {self.name}>' 