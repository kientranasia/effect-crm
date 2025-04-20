from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Interaction, Contact, User
from app import db
from datetime import datetime
from marshmallow import Schema, fields, validate

bp = Blueprint('api_interactions', __name__)

class InteractionSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(list(Interaction.TYPE_CHOICES.keys())))
    title = fields.Str(required=True)
    priority = fields.Str(required=True, validate=validate.OneOf(list(Interaction.PRIORITY_CHOICES.keys())))
    description = fields.Str()
    notes = fields.Str()
    location = fields.Str()
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime()
    status = fields.Str(validate=validate.OneOf(list(Interaction.STATUS_CHOICES.keys())))
    outcome = fields.Str()
    next_steps = fields.Str()
    contact_id = fields.Int(required=True)
    assigned_to_id = fields.Int()

@bp.route('/api/interactions', methods=['POST'])
@login_required
def create_interaction():
    schema = InteractionSchema()
    try:
        data = schema.load(request.json)
        
        # Verify contact exists and belongs to user
        contact = Contact.query.filter_by(
            id=data['contact_id'],
            created_by_id=current_user.id
        ).first_or_404()
        
        # Verify assigned user exists if provided
        if data.get('assigned_to_id'):
            User.query.get_or_404(data['assigned_to_id'])
        
        interaction = Interaction(
            contact_id=contact.id,
            type=data['type'],
            title=data['title'],
            priority=data['priority'],
            description=data.get('description'),
            notes=data.get('notes'),
            location=data.get('location'),
            start_date=data['start_date'],
            end_date=data.get('end_date'),
            status=data.get('status', 'scheduled'),
            outcome=data.get('outcome'),
            next_steps=data.get('next_steps'),
            created_by_id=current_user.id,
            assigned_to_id=data.get('assigned_to_id')
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Interaction created successfully',
            'data': {
                'id': interaction.id,
                'type': interaction.type,
                'title': interaction.title,
                'priority': interaction.priority,
                'start_date': interaction.start_date.isoformat(),
                'end_date': interaction.end_date.isoformat() if interaction.end_date else None,
                'location': interaction.location,
                'contact_id': interaction.contact_id,
                'assigned_to_id': interaction.assigned_to_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route('/api/interactions/<int:interaction_id>', methods=['GET'])
@login_required
def get_interaction(interaction_id):
    interaction = Interaction.query.join(Contact).filter(
        Interaction.id == interaction_id,
        Contact.created_by_id == current_user.id
    ).first_or_404()
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': interaction.id,
            'type': interaction.type,
            'title': interaction.title,
            'priority': interaction.priority,
            'description': interaction.description,
            'notes': interaction.notes,
            'location': interaction.location,
            'start_date': interaction.start_date.isoformat(),
            'end_date': interaction.end_date.isoformat() if interaction.end_date else None,
            'status': interaction.status,
            'outcome': interaction.outcome,
            'next_steps': interaction.next_steps,
            'contact_id': interaction.contact_id,
            'assigned_to_id': interaction.assigned_to_id,
            'created_at': interaction.created_at.isoformat(),
            'updated_at': interaction.updated_at.isoformat()
        }
    }) 