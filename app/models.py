from flask_login import UserMixin
from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

# Association tables for many-to-many relationships
workspace_users = db.Table('workspace_users',
    db.Column('workspace_id', db.Integer, db.ForeignKey('workspace.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

team_users = db.Table('team_users',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Workspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    users = db.relationship('User', secondary=workspace_users, lazy='subquery',
                          backref=db.backref('workspaces', lazy=True))
    teams = db.relationship('Team', backref='workspace', lazy=True)
    organizations = db.relationship('Organization', backref='workspace', lazy=True)
    customers = db.relationship('Customer', backref='workspace', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', secondary=team_users, lazy='subquery',
                          backref=db.backref('teams', lazy=True))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships for owned items
    owned_workspaces = db.relationship('Workspace', backref='owner', lazy=True,
                                     foreign_keys='Workspace.owner_id')
    assigned_customers = db.relationship('Customer', backref='assigned_user', lazy=True,
                                       foreign_keys='Customer.assigned_user_id')
    created_interactions = db.relationship('Interaction', backref='created_by', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
        
    @property
    def is_admin(self):
        return self.role.name == 'admin'
        
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(200))
    overview = db.Column(db.Text)
    country = db.Column(db.String(100))
    labels = db.Column(db.String(200))  # Comma-separated labels
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    customers = db.relationship('Customer', backref='organization', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    status = db.Column(db.String(20), default='Lead')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_contact = db.Column(db.DateTime)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    interactions = db.relationship('Interaction', backref='customer', lazy=True, cascade="all, delete-orphan")

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)
    notes = db.Column(db.Text)  # Additional notes field
    outcome = db.Column(db.String(50))  # Positive, Neutral, Negative, Pending
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    follow_up_date = db.Column(db.Date)  # Date for follow-up
    follow_up_notes = db.Column(db.Text)  # Notes for follow-up
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ai_analysis = db.Column(db.Text) 