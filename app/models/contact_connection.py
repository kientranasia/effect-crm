from app import db
from datetime import datetime

class ContactConnection(db.Model):
    __tablename__ = 'contact_connections'

    id = db.Column(db.Integer, primary_key=True)
    source_contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    target_contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False, default='Connection')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    source_contact = db.relationship('Contact', foreign_keys=[source_contact_id], backref='outgoing_connections')
    target_contact = db.relationship('Contact', foreign_keys=[target_contact_id], backref='incoming_connections')
    created_by = db.relationship('User', backref='created_connections')

    @property
    def other_contact(self):
        """Returns the contact that is not the current contact"""
        from app.models.contact import Contact
        current_contact = Contact.query.get(self.source_contact_id)
        if current_contact:
            return self.target_contact
        return self.source_contact

    def __repr__(self):
        return f'<ContactConnection {self.id}: {self.source_contact_id} -> {self.target_contact_id}>' 