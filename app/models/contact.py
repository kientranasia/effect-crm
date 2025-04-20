from datetime import datetime
from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin

# Association table for Contact-Project many-to-many relationship
project_contacts = db.Table('project_contacts',
    db.Column('contact_id', db.Integer, db.ForeignKey('contacts.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Contact(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Personal Information
    birthday = db.Column(db.Date)
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Social Media
    linkedin = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    github = db.Column(db.String(200))
    
    # Additional Information
    interests = db.Column(db.String(500))
    tags = db.Column(db.String(500))
    
    # Pipeline Information
    stage = db.Column(db.String(50), default='lead')
    deal_value = db.Column(db.Float)
    probability = db.Column(db.Integer)
    expected_close_date = db.Column(db.Date)
    
    # Relationships
    organization = db.relationship('Organization', back_populates='contacts')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_contacts')
    interactions = db.relationship('Interaction', back_populates='contact', lazy='dynamic')
    projects = db.relationship('Project', secondary=project_contacts, back_populates='contacts')
    
    # Stage choices and their display values
    STAGE_CHOICES = {
        'lead': 'Lead',
        'prospect': 'Prospect',
        'qualified': 'Qualified',
        'proposal': 'Proposal',
        'negotiation': 'Negotiation',
        'closed_won': 'Closed Won',
        'closed_lost': 'Closed Lost'
    }
    
    @property
    def stage_display(self):
        return self.STAGE_CHOICES.get(self.stage, self.stage)
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def __repr__(self):
        return f'<Contact {self.full_name}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'organization': self.organization.name if self.organization else None,
            'created_at': self.created_at.isoformat(),
            'stage': self.stage_display
        }

    # Pipeline tracking
    stage_changed_at = db.Column(db.DateTime)
    stage_history = db.Column(db.Text)  # JSON array of stage changes with timestamps
    
    # Customer specific fields
    customer_since = db.Column(db.DateTime)
    lifetime_value = db.Column(db.Float)
    customer_status = db.Column(db.String(50))  # active, inactive, churned
    
    # Deal tracking
    budget = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    interested_in = db.Column(db.String(255))
    
    # Source tracking
    source = db.Column(db.String(50))
    source_origin = db.Column(db.String(100))
    source_channel = db.Column(db.String(100))
    
    # Follow-up
    next_follow_up = db.Column(db.DateTime)
    last_contact_date = db.Column(db.DateTime)
    
    # Personal information
    middle_name = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    gender = db.Column(db.String(20))
    marital_status = db.Column(db.String(20))
    language = db.Column(db.String(10))
    
    # Contact information
    work_phone = db.Column(db.String(20))
    home_phone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    alternate_email = db.Column(db.String(120))
    
    # Professional information
    company_name = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    # Additional metadata
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)  # Comma-separated skills
    education = db.Column(db.Text)  # JSON string of education history
    work_history = db.Column(db.Text)  # JSON string of work history
    preferences = db.Column(db.Text)  # JSON string of contact preferences
    custom_fields = db.Column(db.Text)  # JSON string of custom fields
    
    # Stage colors for UI
    STAGE_COLORS = {
        'lead': 'info',
        'qualified': 'primary',
        'proposal': 'warning',
        'negotiation': 'danger',
        'customer': 'success'
    }
    
    @property
    def stage_color(self):
        return self.STAGE_COLORS.get(self.stage, 'secondary')
    
    def update_stage(self, new_stage, user_id):
        """Update the contact's stage and record the change in history"""
        import json
        from datetime import datetime
        
        if new_stage != self.stage:
            # Create stage history entry
            history_entry = {
                'from_stage': self.stage,
                'to_stage': new_stage,
                'changed_at': datetime.utcnow().isoformat(),
                'changed_by': user_id
            }
            
            # Update stage history
            current_history = json.loads(self.stage_history) if self.stage_history else []
            current_history.append(history_entry)
            self.stage_history = json.dumps(current_history)
            
            # Update stage and timestamp
            self.stage = new_stage
            self.stage_changed_at = datetime.utcnow()
            
            # If becoming a customer, set customer_since
            if new_stage == 'customer' and not self.customer_since:
                self.customer_since = datetime.utcnow()
                self.customer_status = 'active'
    
    def __repr__(self):
        return f"<Contact {self.full_name}>" 