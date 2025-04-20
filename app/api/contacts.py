from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.contact import Contact

bp = Blueprint('api_contacts', __name__)

@bp.route('/contacts/<int:contact_id>/stage', methods=['PUT'])
@login_required
def update_stage(contact_id):
    """Update a contact's stage"""
    contact = Contact.query.get_or_404(contact_id)
    data = request.get_json()
    
    if 'stage' not in data:
        return jsonify({'error': 'Stage is required'}), 400
        
    new_stage = data['stage']
    if new_stage not in contact.STAGE_CHOICES:
        return jsonify({'error': 'Invalid stage'}), 400
    
    try:
        contact.update_stage(new_stage, current_user.id)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Contact stage updated to {contact.stage_display}',
            'stage': contact.stage,
            'stage_display': contact.stage_display,
            'stage_color': contact.stage_color
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 