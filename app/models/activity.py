from datetime import datetime
from app import db
from app.models.mixins import TimestampMixin

class Activity(db.Model, TimestampMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    
    # Activity details
    type = db.Column(db.String(50), nullable=False)  # call, email, meeting, note
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False)
    lead = db.relationship('Lead', backref=db.backref('activities', lazy='dynamic', cascade='all, delete-orphan'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Activity {self.type} for Lead {self.lead_id}>'
    
    @classmethod
    def create(cls, lead_id, user_id, activity_type, description):
        """Create a new activity and update the lead's last contact date"""
        activity = cls(
            lead_id=lead_id,
            user_id=user_id,
            type=activity_type,
            description=description
        )
        
        db.session.add(activity)
        
        # Update lead's last contact date
        from app.models.lead import Lead
        lead = Lead.query.get(lead_id)
        if lead:
            lead.last_contact_date = datetime.utcnow()
        
        db.session.commit()
        return activity 