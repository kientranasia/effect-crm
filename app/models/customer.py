from datetime import datetime
from app import db
from app.models.mixins import TimestampMixin

class Customer(db.Model, TimestampMixin):
    __tablename__ = 'customers'

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
    
    # Customer Details
    status = db.Column(db.String(20), default='active')  # active, inactive, lost
    notes = db.Column(db.Text)
    
    # Relationships
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.relationship('User', backref=db.backref('assigned_customers', lazy=True))
    
    # Organization relationship
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Conversion Information
    converted_from_lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    converted_from_lead = db.relationship('Lead', backref=db.backref('converted_customer', uselist=False))
    conversion_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Customer {self.company_name}>'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'company_name': self.company_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'assigned_to': self.assigned_to.full_name if self.assigned_to else None
        } 