from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin
from datetime import datetime

class Task(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), nullable=False, default='medium')
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_tasks')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_tasks')
    project = db.relationship('Project', backref='tasks')
    contact = db.relationship('Contact', backref='tasks')
    organization = db.relationship('Organization', backref='tasks')
    
    # Priority choices and their display values
    PRIORITY_CHOICES = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'urgent': 'Urgent'
    }
    
    # Status choices and their display values
    STATUS_CHOICES = {
        'pending': 'Pending',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'on_hold': 'On Hold'
    }
    
    @property
    def priority_display(self):
        return self.PRIORITY_CHOICES.get(self.priority, self.priority)
    
    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    def __repr__(self):
        return f'<Task {self.title}>' 