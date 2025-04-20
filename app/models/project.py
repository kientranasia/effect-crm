from datetime import datetime
from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin

# Association table for project team members
project_team_members = db.Table('project_team_members',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role', db.String(50), nullable=False, default='member'),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Project(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False, default='planning')
    priority = db.Column(db.String(20), nullable=False, default='medium')
    budget = db.Column(db.Float)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # Relationships
    created_by = db.relationship('User', backref='created_projects')
    organization = db.relationship('Organization', back_populates='projects')
    team_members = db.relationship('User', secondary=project_team_members,
                                 backref=db.backref('project_teams', lazy='dynamic'))
    contacts = db.relationship('Contact', secondary='project_contacts', back_populates='projects')
    
    # Status choices and their display values
    STATUS_CHOICES = {
        'planning': 'Planning',
        'in_progress': 'In Progress',
        'on_hold': 'On Hold',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }
    
    # Priority choices and their display values
    PRIORITY_CHOICES = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'urgent': 'Urgent'
    }
    
    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)
    
    @property
    def priority_display(self):
        return self.PRIORITY_CHOICES.get(self.priority, self.priority)
    
    @property
    def is_overdue(self):
        if self.end_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.end_date
        return False
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def add_milestone(self, title, due_date, description=None):
        """Add a new milestone to the project"""
        import json
        
        milestone = {
            'id': datetime.utcnow().timestamp(),  # Unique ID for the milestone
            'title': title,
            'due_date': due_date.isoformat() if due_date else None,
            'description': description,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        current_milestones = json.loads(self.milestones) if self.milestones else []
        current_milestones.append(milestone)
        self.milestones = json.dumps(current_milestones)
    
    def update_milestone_status(self, milestone_id, new_status):
        """Update the status of a milestone"""
        import json
        
        if not self.milestones:
            return False
            
        milestones = json.loads(self.milestones)
        for milestone in milestones:
            if milestone['id'] == milestone_id:
                milestone['status'] = new_status
                milestone['updated_at'] = datetime.utcnow().isoformat()
                self.milestones = json.dumps(milestones)
                return True
        return False
    
    def add_team_member(self, user, role=None):
        """Add a team member to the project"""
        if user not in self.team_members:
            self.team_members.append(user)
            # Update the role in the association table
            stmt = project_team_members.update().where(
                db.and_(
                    project_team_members.c.project_id == self.id,
                    project_team_members.c.user_id == user.id
                )
            ).values(role=role)
            db.session.execute(stmt)
    
    def remove_team_member(self, user):
        """Remove a team member from the project"""
        if user in self.team_members:
            self.team_members.remove(user)
    
    def add_team_member(self, user, role=None):
        """Add a team member to the project"""
        if user not in self.team_members:
            self.team_members.append(user)
            # Update the role in the association table
            stmt = project_team_members.update().where(
                db.and_(
                    project_team_members.c.project_id == self.id,
                    project_team_members.c.user_id == user.id
                )
            ).values(role=role)
            db.session.execute(stmt)
    
    def remove_team_member(self, user):
        """Remove a team member from the project"""
        if user in self.team_members:
            self.team_members.remove(user) 