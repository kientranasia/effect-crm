from app import db
from datetime import datetime

class Interaction(db.Model):
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # call, email, meeting, note
    summary = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    outcome = db.Column(db.String(50), nullable=False)  # completed, follow_up, no_response
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    customer = db.relationship('Customer', backref=db.backref('interactions', lazy=True))
    created_by = db.relationship('User', backref=db.backref('interactions', lazy=True))

    def __repr__(self):
        return f'<Interaction {self.type} with {self.customer.full_name}>' 