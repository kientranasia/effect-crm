from datetime import datetime
from app.extensions import db
from app.models.mixins import TimestampMixin, PermissionMixin

class Interaction(db.Model, TimestampMixin, PermissionMixin):
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # call, meeting, email, note, task
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high, urgent
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)  # pending, in_progress, completed, cancelled
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    next_steps = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ai_analysis = db.Column(db.Text)  # Store AI-generated analysis of the interaction

    # Relationships
    contact = db.relationship('Contact', back_populates='interactions')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_interactions')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_interactions')

    # Type choices and their display values
    TYPE_CHOICES = {
        'call': 'Call',
        'meeting': 'Meeting',
        'email': 'Email',
        'note': 'Note',
        'task': 'Task'
    }

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
        'cancelled': 'Cancelled'
    }

    # Type colors for UI
    TYPE_COLORS = {
        'call': 'primary',
        'email': 'info',
        'meeting': 'success',
        'note': 'warning',
        'task': 'danger'
    }

    # Priority colors for UI
    PRIORITY_COLORS = {
        'low': 'success',
        'medium': 'info',
        'high': 'warning',
        'urgent': 'danger'
    }

    # Status colors for UI
    STATUS_COLORS = {
        'pending': 'primary',
        'in_progress': 'info',
        'completed': 'success',
        'cancelled': 'danger'
    }

    # Type icons for UI
    TYPE_ICONS = {
        'call': 'phone',
        'email': 'envelope',
        'meeting': 'calendar',
        'note': 'sticky-note',
        'task': 'tasks'
    }

    @property
    def type_display(self):
        return self.TYPE_CHOICES.get(self.type, self.type)

    @property
    def priority_display(self):
        return self.PRIORITY_CHOICES.get(self.priority, self.priority)

    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status)

    @property
    def type_color(self):
        return self.TYPE_COLORS.get(self.type, 'secondary')

    @property
    def priority_color(self):
        return self.PRIORITY_COLORS.get(self.priority, 'secondary')

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def type_icon(self):
        return self.TYPE_ICONS.get(self.type, 'question-circle')

    def __repr__(self):
        return f'<Interaction {self.type} with {self.contact.full_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type_display,
            'priority': self.priority_display,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status_display,
            'location': self.location,
            'notes': self.notes,
            'next_steps': self.next_steps,
            'contact': self.contact.full_name,
            'created_by': self.created_by.full_name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 