from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.contact import Contact
from app.models.organization import Organization
from app.forms import ContactForm
from datetime import datetime
from app.models.user import User
from app.models.interaction import Interaction
from app.utils.decorators import permission_required
from werkzeug.utils import secure_filename
import vobject
import os
from app.models.contact_connection import ContactConnection

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/contacts')
@login_required
@permission_required('contact_view')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    organization_id = request.args.get('organization_id', type=int)
    created_by = request.args.get('created_by', 'all')
    
    # Base query
    query = Contact.query
    
    # Apply filters
    if search:
        query = query.filter(
            (Contact.first_name.ilike(f'%{search}%')) |
            (Contact.last_name.ilike(f'%{search}%')) |
            (Contact.email.ilike(f'%{search}%')) |
            (Contact.company_name.ilike(f'%{search}%')) |
            (Contact.phone.ilike(f'%{search}%')) |
            (Contact.mobile_phone.ilike(f'%{search}%')) |
            (Contact.work_phone.ilike(f'%{search}%')) |
            (Contact.home_phone.ilike(f'%{search}%')) |
            (Contact.alternate_email.ilike(f'%{search}%')) |
            (Contact.linkedin.ilike(f'%{search}%')) |
            (Contact.twitter.ilike(f'%{search}%')) |
            (Contact.facebook.ilike(f'%{search}%')) |
            (Contact.instagram.ilike(f'%{search}%')) |
            (Contact.github.ilike(f'%{search}%'))
        )
    
    if organization_id:
        query = query.filter(Contact.organization_id == organization_id)
    
    if created_by != 'all':
        query = query.filter(Contact.created_by_id == created_by)
    
    # Get paginated results
    contacts = query.order_by(Contact.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Get organizations for filter dropdown
    organizations = Organization.query.all()
    
    # Get users for created_by filter
    users = User.query.all()
    
    return render_template('contacts/index.html',
                         contacts=contacts,
                         organizations=organizations,
                         users=users,
                         search=search,
                         organization_id=organization_id,
                         created_by=created_by)

@contacts_bp.route('/contacts/new', methods=['GET', 'POST'])
@login_required
@permission_required('contact_create')
def new():
    form = ContactForm()
    form.organization_id.choices = [(0, '-- Select Organization (Optional) --')] + [(org.id, org.name) for org in Organization.query.all()]
    
    if form.validate_on_submit():
        contact = Contact()
        form.populate_obj(contact)
        
        # Set the created_by_id to the current user's ID
        contact.created_by_id = current_user.id
        
        db.session.add(contact)
        db.session.commit()
        
        flash('Contact created successfully.', 'success')
        return redirect(url_for('contacts.show', id=contact.id))
    
    return render_template('contacts/new.html', form=form)

@contacts_bp.route('/contacts/<int:id>')
@login_required
def show(id):
    contact = Contact.query.get_or_404(id)
    interactions = list(Interaction.query.filter_by(contact_id=id).order_by(Interaction.date.desc()).all())
    
    # Calculate interaction counts by type
    interaction_counts = {
        'call': len([i for i in interactions if i.type == 'call']),
        'meeting': len([i for i in interactions if i.type == 'meeting']),
        'email': len([i for i in interactions if i.type == 'email']),
        'note': len([i for i in interactions if i.type == 'note']),
        'task': len([i for i in interactions if i.type == 'task'])
    }
    
    # Add total count
    interaction_counts['total'] = len(interactions)
    
    return render_template('contacts/show.html', 
                         contact=contact, 
                         interactions=interactions,
                         interaction_counts=interaction_counts)

@contacts_bp.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('contact_edit')
def edit(id):
    contact = Contact.query.get_or_404(id)
    form = ContactForm(obj=contact)
    form.organization_id.choices = [(0, '-- Select Organization (Optional) --')] + [(org.id, org.name) for org in Organization.query.all()]
    
    if form.validate_on_submit():
        # Handle numeric fields
        if form.deal_value.data == '':
            form.deal_value.data = None
        if form.probability.data == '':
            form.probability.data = None
            
        form.populate_obj(contact)
        contact.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Contact updated successfully.', 'success')
            return redirect(url_for('contacts.show', id=contact.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating contact: {str(e)}', 'error')
    
    return render_template('contacts/edit.html', form=form, contact=contact)

@contacts_bp.route('/contacts/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('contact_delete')
def delete(id):
    contact = Contact.query.get_or_404(id)
    
    # Check for associated records
    has_interactions = contact.interactions.count() > 0
    
    if has_interactions:
        flash(f'Cannot delete contact. It has {contact.interactions.count()} associated interactions. Please delete these records first.', 'error')
        return redirect(url_for('contacts.show', id=contact.id))
    
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting contact. Please try again.', 'error')
    
    return redirect(url_for('contacts.index'))

@contacts_bp.route('/contacts/<int:id>/convert-to-lead', methods=['POST'])
@login_required
def convert_to_lead(id):
    """Convert a contact to a lead status"""
    contact = Contact.query.get_or_404(id)
    
    # Update contact status to lead
    contact.status = 'lead'
    contact.assigned_to_id = current_user.id
    contact.updated_at = datetime.utcnow()
    
    # Save to database
    db.session.commit()
    
    flash('Contact converted to lead successfully.', 'success')
    return redirect(url_for('contacts.show', id=contact.id))

# API endpoints for AJAX operations
@contacts_bp.route('/api/contacts')
@login_required
def api_index():
    contacts = Contact.query.all()
    return jsonify([contact.to_dict() for contact in contacts])

@contacts_bp.route('/api/contacts/<int:id>')
@login_required
def api_show(id):
    contact = Contact.query.get_or_404(id)
    return jsonify(contact.to_dict())

@contacts_bp.route('/contacts/import-vcard', methods=['POST'])
@login_required
def import_vcard():
    if 'vcard_files' not in request.files:
        return jsonify({'success': False, 'message': 'No files uploaded'}), 400

    files = request.files.getlist('vcard_files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({'success': False, 'message': 'No files selected'}), 400

    skip_duplicates = request.form.get('skip_duplicates', 'true') == 'true'
    update_existing = request.form.get('update_existing', 'false') == 'true'
    import_photos = request.form.get('import_photos', 'true') == 'true'

    imported_count = 0
    skipped_count = 0
    updated_count = 0
    errors = []
    processed_files = set()  # Track processed files to avoid duplicates

    for file in files:
        if file.filename == '' or file.filename in processed_files:
            continue

        processed_files.add(file.filename)

        try:
            # Read and decode the file content
            try:
                vcard_data = file.read().decode('utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                vcard_data = file.read().decode('latin-1')
            
            # Normalize line endings and ensure proper vCard format
            vcard_data = vcard_data.replace('\r\n', '\n').replace('\r', '\n')
            
            # Validate vCard format
            if 'BEGIN:VCARD' not in vcard_data or 'END:VCARD' not in vcard_data:
                errors.append(f"Invalid vCard format in {file.filename}: Missing BEGIN:VCARD or END:VCARD tag")
                continue

            # Split the data into individual vCards and validate each entry
            vcard_entries = []
            current_entry = []
            in_vcard = False
            
            for line in vcard_data.split('\n'):
                if line.strip() == 'BEGIN:VCARD':
                    in_vcard = True
                    current_entry = [line]
                elif line.strip() == 'END:VCARD':
                    in_vcard = False
                    current_entry.append(line)
                    vcard_entries.append('\n'.join(current_entry))
                elif in_vcard:
                    current_entry.append(line)
            
            if not vcard_entries:
                errors.append(f"No valid vCard entries found in {file.filename}")
                continue

            for vcard_text in vcard_entries:
                try:
                    # Parse the vCard
                    vcard = vobject.readOne(vcard_text)
                    
                    # Extract basic info
                    email = str(vcard.email.value) if hasattr(vcard, 'email') else None
                    
                    # Check for existing contact
                    existing_contact = Contact.query.filter_by(email=email).first() if email else None
                    
                    if existing_contact:
                        if skip_duplicates:
                            skipped_count += 1
                            continue
                        elif update_existing:
                            contact = existing_contact
                            updated_count += 1
                        else:
                            skipped_count += 1
                            continue
                    else:
                        contact = Contact()
                        contact.created_by_id = current_user.id
                        imported_count += 1

                    # Basic Information - Required fields
                    if hasattr(vcard, 'n'):
                        name_parts = vcard.n.value
                        contact.first_name = str(name_parts.given).strip() if name_parts.given else 'Unknown'
                        contact.last_name = str(name_parts.family).strip() if name_parts.family else 'Contact'
                    elif hasattr(vcard, 'fn'):
                        full_name = str(vcard.fn.value).strip()
                        name_parts = full_name.split()
                        if len(name_parts) >= 2:
                            contact.first_name = name_parts[0]
                            contact.last_name = ' '.join(name_parts[1:])
                        else:
                            contact.first_name = full_name
                            contact.last_name = 'Contact'
                    else:
                        if email:
                            contact.first_name = email.split('@')[0]
                            contact.last_name = 'Contact'
                        else:
                            contact.first_name = 'Unknown'
                            contact.last_name = 'Contact'

                    # Contact Information
                    if email:
                        contact.email = email

                    # Phone numbers
                    if hasattr(vcard, 'tel'):
                        phones = vcard.tel_list if hasattr(vcard, 'tel_list') else [vcard.tel]
                        
                        # Reset phone fields
                        contact.mobile_phone = None
                        contact.work_phone = None
                        contact.home_phone = None
                        contact.phone = None
                        
                        for tel in phones:
                            phone_types = []
                            if hasattr(tel, 'params') and 'TYPE' in tel.params:
                                phone_types = [t.lower() for t in tel.params['TYPE']]
                            elif hasattr(tel, 'type_paramlist'):
                                phone_types = [t.lower() for t in tel.type_paramlist]
                            elif hasattr(tel, 'type_param'):
                                phone_types = [tel.type_param.lower()]
                            
                            phone_value = str(tel.value).strip()
                            phone_value = ''.join(c for c in phone_value if c.isdigit() or c in ['+'])
                            
                            # Map phone types to contact fields
                            if any(t in ['cell', 'mobile'] for t in phone_types):
                                contact.mobile_phone = phone_value
                            elif any(t in ['work', 'office'] for t in phone_types):
                                contact.work_phone = phone_value
                            elif any(t in ['home', 'residence'] for t in phone_types):
                                contact.home_phone = phone_value
                            elif not contact.phone:  # Only set if not already set
                                contact.phone = phone_value

                    # Address Information
                    if hasattr(vcard, 'adr'):
                        adr = vcard.adr.value
                        street_parts = str(adr.street).strip().split('\n') if adr.street else []
                        
                        contact.address_line1 = street_parts[0] if street_parts else ''
                        if len(street_parts) > 1:
                            contact.address_line2 = street_parts[1]
                        
                        if adr.city:
                            contact.city = str(adr.city).strip()
                        if adr.region:
                            contact.state = str(adr.region).strip()
                        if adr.code:
                            contact.postal_code = str(adr.code).strip()
                        if adr.country:
                            contact.country = str(adr.country).strip()

                    # Organization Information
                    if hasattr(vcard, 'org'):
                        contact.company_name = str(vcard.org.value[0]).strip() if vcard.org.value else ''
                    if hasattr(vcard, 'title'):
                        contact.title = str(vcard.title.value).strip()

                    # Notes
                    if hasattr(vcard, 'note'):
                        contact.notes = str(vcard.note.value).strip()

                    db.session.add(contact)

                except Exception as e:
                    errors.append(f"Error processing contact from {file.filename}: {str(e)}")
                    continue

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                errors.append(f"Database error while saving contacts: {str(e)}")

        except Exception as e:
            errors.append(f"Error processing file {file.filename}: {str(e)}")
            continue

    # If we have any successful imports, consider it a success even with some errors
    if imported_count > 0 or updated_count > 0:
        return jsonify({
            'success': True,
            'message': f'Successfully imported {imported_count} contacts, updated {updated_count}, skipped {skipped_count}',
            'data': {
                'imported': imported_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'errors': errors
            }
        })

    # If we have no successful imports but have errors, return error status
    return jsonify({
        'success': False,
        'message': 'Failed to import contacts',
        'data': {
            'imported': imported_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'errors': errors
        }
    }), 400 

@contacts_bp.route('/contacts/<int:id>/connections', methods=['GET'])
@login_required
def get_connections(id):
    contact = Contact.query.get_or_404(id)
    connections = ContactConnection.query.filter(
        db.or_(
            ContactConnection.source_contact_id == id,
            ContactConnection.target_contact_id == id
        )
    ).all()
    
    result = []
    for conn in connections:
        # Determine which contact is the "other" contact
        if conn.source_contact_id == id:
            other_contact = conn.target_contact
        else:
            other_contact = conn.source_contact
            
        result.append({
            'id': conn.id,
            'other_contact': {
                'id': other_contact.id,
                'name': f"{other_contact.first_name} {other_contact.last_name}",
                'avatar': f"{other_contact.first_name[0]}{other_contact.last_name[0]}"
            },
            'relationship_type': conn.relationship_type,
            'notes': conn.notes,
            'created_at': conn.created_at.isoformat()
        })
    
    return jsonify({'connections': result})

@contacts_bp.route('/contacts/<int:id>/connections', methods=['POST'])
@login_required
def add_connection(id):
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    
    target_contact_id = data.get('target_contact_id')
    if not target_contact_id:
        return jsonify({'error': 'Target contact is required'}), 400
        
    target_contact = Contact.query.get_or_404(target_contact_id)
    
    # Check if connection already exists
    existing = ContactConnection.query.filter(
        db.or_(
            db.and_(
                ContactConnection.source_contact_id == id,
                ContactConnection.target_contact_id == target_contact_id
            ),
            db.and_(
                ContactConnection.source_contact_id == target_contact_id,
                ContactConnection.target_contact_id == id
            )
        )
    ).first()
    
    if existing:
        return jsonify({'error': 'Connection already exists'}), 400
    
    connection = ContactConnection(
        source_contact_id=id,
        target_contact_id=target_contact_id,
        relationship_type=data.get('relationship_type', 'Connection'),
        notes=data.get('notes'),
        created_by_id=current_user.id
    )
    
    db.session.add(connection)
    db.session.commit()
    
    return jsonify({
        'message': 'Connection added successfully',
        'connection': {
            'id': connection.id,
            'other_contact': {
                'id': target_contact.id,
                'name': f"{target_contact.first_name} {target_contact.last_name}",
                'avatar': f"{target_contact.first_name[0]}{target_contact.last_name[0]}"
            },
            'relationship_type': connection.relationship_type,
            'notes': connection.notes,
            'created_at': connection.created_at.isoformat()
        }
    })

@contacts_bp.route('/contacts/connections/<int:connection_id>', methods=['DELETE'])
@login_required
def delete_connection(connection_id):
    connection = ContactConnection.query.get_or_404(connection_id)
    
    # Check if user has permission to delete
    if connection.created_by_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(connection)
    db.session.commit()
    
    return jsonify({'message': 'Connection deleted successfully'})

@contacts_bp.route('/contacts/connections/<int:connection_id>', methods=['PUT'])
@login_required
def update_connection(connection_id):
    connection = ContactConnection.query.get_or_404(connection_id)
    
    # Check if user has permission to update
    if connection.created_by_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update connection fields
    if 'relationship_type' in data:
        connection.relationship_type = data['relationship_type']
    if 'notes' in data:
        connection.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Connection updated successfully',
        'connection': {
            'id': connection.id,
            'relationship_type': connection.relationship_type,
            'notes': connection.notes
        }
    })

@contacts_bp.route('/contacts/search')
@login_required
def search():
    search = request.args.get('query', '')
    
    # Base query
    query = Contact.query
    
    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Contact.first_name.ilike(f'%{search}%'),
                Contact.last_name.ilike(f'%{search}%'),
                Contact.email.ilike(f'%{search}%'),
                Contact.phone.ilike(f'%{search}%'),
                Contact.work_phone.ilike(f'%{search}%'),
                Contact.home_phone.ilike(f'%{search}%'),
                # Also search for full name matches
                db.func.concat(Contact.first_name, ' ', Contact.last_name).ilike(f'%{search}%')
            )
        )
    
    contacts = query.all()
    return jsonify({
        'contacts': [{
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'email': contact.email,
            'phone': contact.phone,
            'work_phone': contact.work_phone,
            'home_phone': contact.home_phone
        } for contact in contacts]
    }) 