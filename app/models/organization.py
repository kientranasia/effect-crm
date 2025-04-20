from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin
from datetime import datetime

class Organization(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    annual_revenue = db.Column(db.Float)
    founded_year = db.Column(db.Integer)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', backref='created_organizations')
    contacts = db.relationship('Contact', back_populates='organization', lazy='dynamic')
    projects = db.relationship('Project', back_populates='organization', lazy='dynamic')
    
    # Industry choices and their display values
    INDUSTRY_CHOICES = {
        'technology': 'Technology',
        'healthcare': 'Healthcare',
        'finance': 'Finance',
        'retail': 'Retail',
        'manufacturing': 'Manufacturing',
        'education': 'Education',
        'government': 'Government',
        'nonprofit': 'Non-Profit',
        'other': 'Other'
    }
    
    # Size choices and their display values
    SIZE_CHOICES = {
        '1-10': '1-10 employees',
        '11-50': '11-50 employees',
        '51-200': '51-200 employees',
        '201-500': '201-500 employees',
        '501-1000': '501-1000 employees',
        '1000+': '1000+ employees'
    }
    
    @property
    def industry_display(self):
        return self.INDUSTRY_CHOICES.get(self.industry, self.industry)
    
    @property
    def size_display(self):
        return self.SIZE_CHOICES.get(self.size, self.size)
    
    def __repr__(self):
        return f'<Organization {self.name}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'size': self.size,
            'website': self.website,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by.full_name if self.created_by else None
        } 