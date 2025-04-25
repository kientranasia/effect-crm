from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Organization, Contact
from app.models.user import User
from datetime import datetime
from app.forms import OrganizationForm
from app.utils.decorators import permission_required
from sqlalchemy import func

organizations_bp = Blueprint('organizations', __name__, url_prefix='/organizations')

@organizations_bp.route('/')
@login_required
@permission_required('org_view')
def index():
    organizations = Organization.query.filter_by(created_by_id=current_user.id).all()
    
    # Calculate industry counts
    industry_counts = {}
    for industry, label in Organization.INDUSTRY_CHOICES.items():
        count = Organization.query.filter_by(
            created_by_id=current_user.id,
            industry=industry
        ).count()
        if count > 0:  # Only include industries that have organizations
            industry_counts[industry] = {
                'label': label,
                'count': count
            }
    
    # Calculate size counts
    size_counts = {}
    for size, label in Organization.SIZE_CHOICES.items():
        count = Organization.query.filter_by(
            created_by_id=current_user.id,
            size=size
        ).count()
        if count > 0:  # Only include sizes that have organizations
            size_counts[size] = {
                'label': label,
                'count': count
            }
    
    return render_template('organizations/index.html',
                         organizations=organizations,
                         industry_counts=industry_counts,
                         size_counts=size_counts)

@organizations_bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('org_create')
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        organization = Organization(
            name=form.name.data,
            description=form.description.data,
            industry=form.industry.data,
            website=form.website.data,
            status=form.status.data,
            size=form.size.data,
            annual_revenue=form.annual_revenue.data,
            founded_year=form.founded_year.data,
            primary_email=form.primary_email.data,
            phone=form.phone.data,
            address_line1=form.address_line1.data,
            address_line2=form.address_line2.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            segment_tags=form.segment_tags.data,
            custom_fields=form.custom_fields.data,
            created_by_id=current_user.id
        )
        db.session.add(organization)
        db.session.commit()
        flash('Organization created successfully.', 'success')
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        return redirect(url_for('organizations.index'))
    return render_template('organizations/create.html', form=form)

@organizations_bp.route('/<int:id>')
@login_required
def show(id):
    organization = Organization.query.filter_by(
        id=id,
        created_by_id=current_user.id
    ).first_or_404()
    
    return render_template('organizations/show.html', organization=organization)

@organizations_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('org_edit')
def edit(id):
    organization = Organization.query.filter_by(
        id=id,
        created_by_id=current_user.id
    ).first_or_404()
    
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        form.populate_obj(organization)
        db.session.commit()
        flash('Organization updated successfully.', 'success')
        return_url = request.args.get('return_url')
        if return_url:
            return redirect(return_url)
        return redirect(url_for('organizations.show', id=organization.id))
    return render_template('organizations/edit.html', form=form, organization=organization)

@organizations_bp.route('/<int:id>/delete', methods=['POST'])
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

@organizations_bp.route('/create_from_contact/<int:id>', methods=['POST'])
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

@organizations_bp.route('/create/ajax', methods=['POST'])
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