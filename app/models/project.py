from datetime import datetime, date
from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin
from sqlalchemy.types import TypeDecorator, Date
from sqlalchemy.dialects.postgresql import JSONB

# Custom date type that handles string conversion
class FlexibleDate(TypeDecorator):
    impl = Date
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                try:
                    # Try parsing with strptime
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return None
        if isinstance(value, (int, float)):
            try:
                # Handle timestamp values
                return datetime.fromtimestamp(value).date()
            except (ValueError, TypeError):
                return None
        return None
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                return None
        return value

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
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(FlexibleDate)
    end_date = db.Column(FlexibleDate)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    priority = db.Column(db.String(20), nullable=False, default='medium')
    budget = db.Column(db.Float)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # Relationships
    tasks = db.relationship('Task', back_populates='project', lazy='dynamic')
    team_members = db.relationship('User', secondary='project_team_members', lazy='subquery',
        backref=db.backref('member_projects', lazy=True))
    created_by = db.relationship('User', backref='created_projects')
    organization = db.relationship('Organization', back_populates='organization_projects')
    contacts = db.relationship('Contact', secondary='project_contacts', back_populates='projects')
    
    # Status choices and their display values
    STATUS_CHOICES = {
        'active': 'Active',
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
        """Return the formatted status display value"""
        return self.STATUS_CHOICES.get(self.status, self.status.replace('_', ' ').title())
    
    @property
    def priority_display(self):
        return self.PRIORITY_CHOICES.get(self.priority, self.priority)
    
    @property
    def formatted_start_date(self):
        """Safely format the start date"""
        if self.start_date:
            try:
                return self.start_date.strftime('%b %d')
            except (AttributeError, ValueError):
                return None
        return None
    
    @property
    def formatted_end_date(self):
        """Safely format the end date"""
        if self.end_date:
            try:
                return self.end_date.strftime('%b %d')
            except (AttributeError, ValueError):
                return None
        return None
    
    @property
    def progress(self):
        """Calculate project progress based on completed tasks"""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        
        completed_tasks = self.tasks.filter_by(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if self.end_date and datetime.now().date() > self.end_date:
            return True
        return False
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def add_team_member(self, user, role=None):
        """Add a team member to the project"""
        if role:
            db.session.execute(
                project_team_members.insert().values(
                    project_id=self.id,
                    user_id=user.id,
                    role=role
                )
            )
        else:
            db.session.execute(
                project_team_members.insert().values(
                    project_id=self.id,
                    user_id=user.id
                )
            )
        db.session.commit()
    
    def remove_team_member(self, user):
        """Remove a team member from the project"""
        db.session.execute(
            project_team_members.delete().where(
                db.and_(
                    project_team_members.c.project_id == self.id,
                    project_team_members.c.user_id == user.id
                )
            )
        )
        db.session.commit() 