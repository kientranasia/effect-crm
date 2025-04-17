from datetime import datetime
from app import db
from app.models.mixins import TimestampMixin

class Lead(db.Model, TimestampMixin):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    job_title = db.Column(db.String(100))
    
    # Company Information
    company_name = db.Column(db.String(120))
    industry = db.Column(db.String(64))
    company_size = db.Column(db.String(50))  # e.g., "1-10", "11-50", "51-200", etc.
    website = db.Column(db.String(120))
    
    # Lead Details
    source = db.Column(db.String(50))  # website, referral, cold call, etc.
    status = db.Column(db.String(20), default='new')  # new, contacted, qualified, converted, lost
    notes = db.Column(db.Text)
    interested_in = db.Column(db.String(255))  # Products/services they're interested in
    requirements = db.Column(db.Text)
    budget = db.Column(db.String(50))  # Budget range
    timeline = db.Column(db.String(50))  # When they want to make a decision
    
    # Follow-up
    next_follow_up = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.relationship('User', backref=db.backref('assigned_leads', lazy=True))
    
    # Organization relationship
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    org = db.relationship('Organization')
    
    # Conversion Information
    converted = db.Column(db.Boolean, default=False)
    converted_date = db.Column(db.DateTime)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __repr__(self):
        return f'<Lead {self.company_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'company_name': self.company_name,
            'status': self.status,
            'source': self.source,
            'score': self.score,
            'created_at': self.created_at.isoformat(),
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'next_follow_up': self.next_follow_up.isoformat() if self.next_follow_up else None,
            'assigned_to': self.assigned_to.name if self.assigned_to else None
        } 