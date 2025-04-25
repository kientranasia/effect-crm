from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin
from datetime import datetime

class Task(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), nullable=False, default='medium')
    status = db.Column(db.String(20), nullable=False, default='todo')
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    project = db.relationship('Project', back_populates='tasks')
    assigned_to = db.relationship('User', 
                                foreign_keys=[assigned_to_id],
                                backref=db.backref('assigned_tasks', lazy=True))
    created_by = db.relationship('User', 
                               foreign_keys=[created_by_id],
                               backref=db.backref('created_tasks', lazy=True))
    
    # Priority choices and their display values
    PRIORITY_CHOICES = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'urgent': 'Urgent'
    }
    
    # Priority colors for UI
    PRIORITY_COLORS = {
        'low': 'success',
        'medium': 'info',
        'high': 'warning',
        'urgent': 'danger'
    }
    
    # Status choices and their display values
    STATUS_CHOICES = {
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'on_hold': 'On Hold',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }
    
    @property
    def priority_display(self):
        return self.PRIORITY_CHOICES.get(self.priority, self.priority)
    
    @property
    def priority_color(self):
        return self.PRIORITY_COLORS.get(self.priority, 'secondary')
    
    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False
    
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        if not self.position:
            last_task = Task.query.filter_by(project_id=self.project_id, status=self.status).order_by(Task.position.desc()).first()
            self.position = (last_task.position + 1) if last_task else 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'position': self.position,
            'project_id': self.project_id,
            'assigned_to': self.assigned_to.to_dict() if self.assigned_to else None,
            'created_by': self.created_by.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Task {self.title}>' 