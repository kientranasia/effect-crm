from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Organization
from app.models.lead import Lead
from . import bp

@bp.route('/organizations')
@login_required
def index():
    # Get all organizations with their relationships
    organizations = Organization.query.order_by(Organization.created_at.desc()).all()
    return render_template('organizations/index.html', organizations=organizations)

@bp.route('/organizations/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        organization = Organization(
            name=request.form['name'],
            description=request.form.get('description'),
            website=request.form.get('website'),
            industry=request.form.get('industry'),
            size=request.form.get('size'),
            created_by=current_user.id
        )
        db.session.add(organization)
        db.session.commit()
        flash('Organization created successfully.', 'success')
        return redirect(url_for('organizations.index'))
    return render_template('organizations/create.html')

@bp.route('/organizations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = Organization.query.get_or_404(id)
    if request.method == 'POST':
        organization.name = request.form['name']
        organization.description = request.form.get('description')
        organization.website = request.form.get('website')
        organization.industry = request.form.get('industry')
        organization.size = request.form.get('size')
        db.session.commit()
        flash('Organization updated successfully.', 'success')
        return redirect(url_for('organizations.index'))
    return render_template('organizations/edit.html', organization=organization)

@bp.route('/organizations/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    organization = Organization.query.get_or_404(id)
    db.session.delete(organization)
    db.session.commit()
    flash('Organization deleted successfully.', 'success')
    return redirect(url_for('organizations.index'))

@bp.route('/create_from_lead/<int:lead_id>', methods=['POST'])
@login_required
def create_from_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    
    if not lead.company_name:
        flash('Cannot create organization: Lead has no company name.', 'error')
        return redirect(url_for('contacts.show', id=lead_id))
    
    organization = Organization(
        name=lead.company_name,
        industry=lead.industry,
        website=lead.website,
        created_by_id=current_user.id
    )
    
    db.session.add(organization)
    db.session.commit()
    
    flash('Organization created successfully from lead.', 'success')
    return redirect(url_for('organizations.show', id=organization.id))

@bp.route('/api/<int:id>', methods=['GET'])
@login_required
def get_organization(id):
    organization = Organization.query.get_or_404(id)
    return jsonify({
        'id': organization.id,
        'name': organization.name,
        'industry': organization.industry,
        'company_size': organization.company_size,
        'website': organization.website
    })

@bp.route('/create_ajax', methods=['POST'])
@login_required
def create_ajax():
    data = request.get_json()
    
    organization = Organization(
        name=data.get('name'),
        industry=data.get('industry'),
        company_size=data.get('company_size'),
        website=data.get('website'),
        description=data.get('description'),
        created_by_id=current_user.id
    )
    
    db.session.add(organization)
    db.session.commit()
    
    return jsonify({
        'id': organization.id,
        'name': organization.name,
        'industry': organization.industry,
        'company_size': organization.company_size,
        'website': organization.website
    }) 