from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Organization
from app.models.lead import Lead
from . import bp

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    country = request.args.get('country', '')
    sort = request.args.get('sort', 'name')

    # Check if user has any workspaces
    if not current_user.workspaces:
        flash('You need to be assigned to a workspace to view organizations.', 'warning')
        return redirect(url_for('main.index'))
    
    query = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id)

    if search:
        query = query.filter(Organization.name.ilike(f'%{search}%'))
    if country:
        query = query.filter_by(country=country)

    if sort == 'name':
        query = query.order_by(Organization.name)
    elif sort == 'created_at':
        query = query.order_by(Organization.created_at.desc())
    elif sort == 'customers':
        query = query.order_by(db.func.count(Organization.customers).desc())

    pagination = query.paginate(page=page, per_page=10)
    organizations = pagination.items

    # Get unique countries for filter
    countries = db.session.query(Organization.country).filter(
        Organization.workspace_id == current_user.workspaces[0].id,
        Organization.country.isnot(None)
    ).distinct().all()
    countries = [country[0] for country in countries if country[0]]

    return render_template('organizations/index.html',
                         organizations=organizations,
                         pagination=pagination,
                         countries=countries)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        industry = request.form.get('industry')
        website = request.form.get('website')
        description = request.form.get('description')
        
        organization = Organization(
            name=name,
            industry=industry,
            website=website,
            description=description,
            workspace_id=current_user.workspaces[0].id
        )
        
        db.session.add(organization)
        db.session.commit()
        
        flash('Organization created successfully.', 'success')
        return redirect(url_for('organizations.index'))
    
    return render_template('organizations/create.html')

@bp.route('/<int:id>')
@login_required
def show(id):
    organization = Organization.query.get_or_404(id)
    return render_template('organizations/show.html', organization=organization)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = Organization.query.get_or_404(id)
    
    if request.method == 'POST':
        organization.name = request.form.get('name')
        organization.industry = request.form.get('industry')
        organization.website = request.form.get('website')
        organization.description = request.form.get('description')
        
        db.session.commit()
        flash('Organization updated successfully.', 'success')
        return redirect(url_for('organizations.show', id=organization.id))
    
    return render_template('organizations/edit.html', organization=organization)

@bp.route('/<int:id>/delete', methods=['POST'])
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
        return redirect(url_for('leads.show', id=lead_id))
    
    organization = Organization(
        name=lead.company_name,
        industry=lead.industry,
        website=lead.website,
        workspace_id=current_user.workspaces[0].id
    )
    
    db.session.add(organization)
    db.session.commit()
    
    flash('Organization created successfully from lead.', 'success')
    return redirect(url_for('organizations.show', id=organization.id)) 