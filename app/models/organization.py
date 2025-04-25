from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin
from datetime import datetime
import json
from sqlalchemy import func
from app.models.contact import Contact

class Organization(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'organizations'
    
    # Normal Flow Fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    annual_revenue = db.Column(db.Float)
    founded_year = db.Column(db.Integer)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Contact Information (Normal Flow)
    primary_email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    
    # Address Information (Normal Flow)
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    
    # Status and Classification (Normal Flow)
    status = db.Column(db.String(50), default='active')
    segment_tags = db.Column(db.Text)  # Stored as JSON string
    
    # Custom Fields (Normal Flow)
    custom_fields = db.Column(db.Text)  # Stored as JSON string
    
    # AI-Driven Fields
    clv = db.Column(db.Float)  # Customer Lifetime Value
    engagement_score = db.Column(db.Integer)  # 0-100 score
    churn_risk = db.Column(db.Float)  # 0-1 probability
    upsell_potential = db.Column(db.String(50))  # Low, Medium, High
    next_best_action = db.Column(db.String(200))
    last_interaction = db.Column(db.DateTime)
    
    # Relationships
    contacts = db.relationship('Contact', back_populates='organization', lazy='dynamic')
    organization_projects = db.relationship('Project', back_populates='organization')
    created_by = db.relationship('User', backref='created_organizations')
    
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
    
    # Status choices
    STATUS_CHOICES = {
        'active': 'Active',
        'inactive': 'Inactive',
        'pending': 'Pending',
        'lead': 'Lead',
        'customer': 'Customer'
    }
    
    # Upsell potential choices
    UPSELL_CHOICES = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High'
    }
    
    @property
    def industry_display(self):
        return self.INDUSTRY_CHOICES.get(self.industry, self.industry)
    
    @property
    def size_display(self):
        return self.SIZE_CHOICES.get(self.size, self.size)
    
    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)
    
    @property
    def upsell_potential_display(self):
        return self.UPSELL_CHOICES.get(self.upsell_potential, self.upsell_potential)
    
    @property
    def segment_tags_list(self):
        if not self.segment_tags:
            return []
        try:
            return json.loads(self.segment_tags)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @segment_tags_list.setter
    def segment_tags_list(self, value):
        if value is None:
            self.segment_tags = None
        else:
            self.segment_tags = json.dumps(value)
    
    @property
    def custom_fields_dict(self):
        if not self.custom_fields:
            return {}
        try:
            return json.loads(self.custom_fields)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @custom_fields_dict.setter
    def custom_fields_dict(self, value):
        if value is None:
            self.custom_fields = None
        else:
            self.custom_fields = json.dumps(value)
    
    @property
    def contacts_count(self):
        """Return the total number of contacts for this organization."""
        return db.session.query(func.count(Contact.id)).filter_by(organization_id=self.id).scalar() or 0
    
    def __repr__(self):
        return f'<Organization {self.name}>'
        
    def to_dict(self):
        """Convert organization to dictionary with both normal flow and AI-driven values."""
        return {
            # Normal Flow Values
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'industry': self.industry,
            'industry_display': self.industry_display,
            'size': self.size,
            'size_display': self.size_display,
            'annual_revenue': self.annual_revenue,
            'founded_year': self.founded_year,
            'primary_email': self.primary_email,
            'phone': self.phone,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'postal_code': self.postal_code,
                'country': self.country
            },
            'status': self.status,
            'status_display': self.status_display,
            'segment_tags': self.segment_tags_list,
            'custom_fields': self.custom_fields_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by.full_name if self.created_by else None,
            'contacts_count': self.contacts_count,
            
            # AI-Driven Values
            'clv': self.clv,
            'engagement_score': self.engagement_score,
            'churn_risk': self.churn_risk,
            'upsell_potential': self.upsell_potential,
            'upsell_potential_display': self.upsell_potential_display,
            'next_best_action': self.next_best_action,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None
        } 