from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Organization, Contact
from app.models.user import User
from datetime import datetime
from app.forms import OrganizationForm
from app.utils.decorators import permission_required

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/organizations')
@login_required
@permission_required('org_view')
def index():
    # Get organizations created by the current user
    organizations = Organization.query.filter_by(created_by_id=current_user.id).all()
    return render_template('organizations/index.html', organizations=organizations)

@organizations_bp.route('/organizations/create', methods=['GET', 'POST'])
@login_required
@permission_required('org_create')
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        organization = Organization(
            name=form.name.data,
            description=form.description.data,
            created_by_id=current_user.id
        )
        db.session.add(organization)
        db.session.commit()
        flash('Organization created successfully.', 'success')
        return redirect(url_for('organizations.index'))
    return render_template('organizations/form.html', form=form, title='Create Organization')

@organizations_bp.route('/organizations/<int:id>')
@login_required
def show(id):
    organization = Organization.query.filter_by(
        id=id,
        created_by_id=current_user.id
    ).first_or_404()
    
    return render_template('organizations/show.html', organization=organization)

@organizations_bp.route('/organizations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('org_edit')
def edit(id):
    organization = Organization.query.filter_by(
        id=id,
        created_by_id=current_user.id
    ).first_or_404()
    
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        organization.name = form.name.data
        organization.description = form.description.data
        db.session.commit()
        flash('Organization updated successfully.', 'success')
        return redirect(url_for('organizations.index'))
    return render_template('organizations/form.html', form=form, title='Edit Organization')

@organizations_bp.route('/organizations/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('org_delete')
def delete(id):
    organization = Organization.query.filter_by(
        id=id,
        created_by_id=current_user.id
    ).first_or_404()
    
    db.session.delete(organization)
    db.session.commit()
    flash('Organization deleted successfully.', 'success')
    return redirect(url_for('organizations.index'))

@organizations_bp.route('/organizations/create_from_contact/<int:id>', methods=['POST'])
@login_required
def create_from_contact(id):
    """Create a new organization from a contact"""
    contact = Contact.query.get_or_404(id)
    
    # Check if organization with same name already exists
    existing_org = Organization.query.filter_by(name=contact.company_name).first()
    if existing_org:
        flash('An organization with this name already exists.', 'warning')
        return redirect(url_for('organizations.show', id=existing_org.id))
    
    # Create new organization
    organization = Organization(
        name=contact.company_name,
        website=contact.website,
        created_by_id=current_user.id
    )
    
    # Save to database
    db.session.add(organization)
    db.session.commit()
    
    # Update contact with organization ID
    contact.organization_id = organization.id
    db.session.commit()
    
    flash('Organization created successfully!', 'success')
    return redirect(url_for('organizations.show', id=organization.id))

@organizations_bp.route('/organizations/create/ajax', methods=['POST'])
@login_required
def create_ajax():
    """Create a new organization via AJAX"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Organization name is required.'}), 400
    
    # Check if organization already exists
    existing_org = Organization.query.filter_by(name=data.get('name')).first()
    if existing_org:
        return jsonify({'error': 'An organization with this name already exists.'}), 400
    
    # Create new organization
    organization = Organization(
        name=data.get('name'),
        industry=data.get('industry'),
        website=data.get('website'),
        created_by_id=current_user.id
    )
    
    # Save to database
    db.session.add(organization)
    db.session.commit()
    
    return jsonify({
        'id': organization.id,
        'name': organization.name
    }) 