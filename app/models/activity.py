from datetime import datetime
from app.extensions import db
from app.models.mixins import TimestampMixin

class Activity(db.Model, TimestampMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    
    # Activity details
    type = db.Column(db.String(50), nullable=False)  # call, email, meeting, note
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = db.relationship('Contact', backref=db.backref('activities', lazy='dynamic', cascade='all, delete-orphan'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Activity {self.type} for Contact {self.contact_id}>'
    
    @classmethod
    def create(cls, contact_id, user_id, activity_type, description):
        """Create a new activity and update the contact's last contact date"""
        activity = cls(
            contact_id=contact_id,
            user_id=user_id,
            type=activity_type,
            description=description
        )
        
        db.session.add(activity)
        
        # Update contact's last contact date
        from app.models.contact import Contact
        contact = Contact.query.get(contact_id)
        if contact:
            contact.last_contact_date = datetime.utcnow()
        
        db.session.commit()
        return activity 