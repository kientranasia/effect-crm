from app import db
from datetime import datetime

# Association table for workspace users
workspace_users = db.Table('workspace_users',
    db.Column('workspace_id', db.Integer, db.ForeignKey('workspaces.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Workspace(db.Model):
    __tablename__ = 'workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    
    # Relationships
    organization = db.relationship('Organization', backref=db.backref('workspaces', lazy=True))
    users = db.relationship('User', secondary=workspace_users, backref=db.backref('workspaces', lazy=True))

    def __repr__(self):
        return f'<Workspace {self.name}>' 