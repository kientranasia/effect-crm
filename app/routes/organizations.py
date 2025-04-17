from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Organization
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.user import User
from datetime import datetime

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/organizations')
@login_required
def index():
    """List all organizations with filtering options"""
    # Get query parameters for filtering
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    sort = request.args.get('sort', 'newest')
    
    # Start with a base query
    query = Organization.query
    
    # Apply filters if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(Organization.name.ilike(search_term))
    if industry:
        query = query.filter(Organization.industry == industry)
    
    # Apply sorting
    if sort == 'newest':
        query = query.order_by(Organization.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(Organization.created_at.asc())
    elif sort == 'name':
        query = query.order_by(Organization.name.asc())
    elif sort == 'leads':
        query = query.outerjoin(Lead).group_by(Organization.id).order_by(db.func.count(Lead.id).desc())
    
    # Paginate results
    organizations = query.paginate(page=page, per_page=10, error_out=False)
    
    # Get unique industries for filter dropdown
    industries = db.session.query(Organization.industry).distinct().all()
    industries = [i[0] for i in industries if i[0]]  # Extract from tuples and filter out None
    
    return render_template('organizations/index.html', 
                         organizations=organizations,
                         industries=industries)

@organizations_bp.route('/organizations/new', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new organization"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        industry = request.form.get('industry')
        website = request.form.get('website')
        status = request.form.get('status', 'active')
        
        # Validate required fields
        if not name:
            flash('Organization name is required.', 'danger')
            return redirect(url_for('organizations.create'))
        
        # Create new organization
        organization = Organization(
            name=name,
            description=description,
            industry=industry,
            website=website,
            status=status
        )
        
        # Save to database
        db.session.add(organization)
        db.session.commit()
        
        flash('Organization created successfully!', 'success')
        return redirect(url_for('organizations.show', id=organization.id))
    
    return render_template('organizations/create.html')

@organizations_bp.route('/organizations/<int:id>')
@login_required
def show(id):
    """Show organization details"""
    organization = Organization.query.get_or_404(id)
    
    # Get related leads and customers
    leads = Lead.query.filter_by(company_name=organization.name).all()
    customers = Customer.query.filter_by(organization_id=organization.id).all()
    
    return render_template('organizations/show.html', 
                          organization=organization,
                          leads=leads,
                          customers=customers)

@organizations_bp.route('/organizations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an organization"""
    organization = Organization.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update organization fields
        organization.name = request.form.get('name')
        organization.description = request.form.get('description')
        organization.industry = request.form.get('industry')
        organization.website = request.form.get('website')
        organization.status = request.form.get('status', 'active')
        organization.updated_at = datetime.utcnow()
        
        # Save changes
        db.session.commit()
        
        flash('Organization updated successfully!', 'success')
        return redirect(url_for('organizations.show', id=organization.id))
    
    return render_template('organizations/edit.html', organization=organization)

@organizations_bp.route('/organizations/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete an organization"""
    organization = Organization.query.get_or_404(id)
    
    # Check if organization has customers
    if organization.customers:
        flash('Cannot delete organization with associated customers.', 'danger')
        return redirect(url_for('organizations.show', id=organization.id))
    
    # Delete organization
    db.session.delete(organization)
    db.session.commit()
    
    flash('Organization deleted successfully!', 'success')
    return redirect(url_for('organizations.index'))

@organizations_bp.route('/organizations/create_from_lead/<int:id>', methods=['POST'])
@login_required
def create_from_lead(id):
    """Create an organization from a lead"""
    lead = Lead.query.get_or_404(id)
    
    # Check if organization already exists
    existing_org = Organization.query.filter_by(name=lead.company_name).first()
    if existing_org:
        flash(f'Organization "{lead.company_name}" already exists.', 'warning')
        return redirect(url_for('leads.show', id=lead.id))
    
    # Create new organization
    organization = Organization(
        name=lead.company_name,
        industry=lead.industry,
        website=lead.website,
        status='active'
    )
    
    # Save to database
    db.session.add(organization)
    db.session.commit()
    
    flash(f'Organization "{organization.name}" created from lead!', 'success')
    return redirect(url_for('organizations.show', id=organization.id))

@organizations_bp.route('/create/ajax', methods=['POST'])
@login_required
def create_ajax():
    """Create a new organization via AJAX request."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
        
    organization = Organization(
        name=data['name'],
        industry=data.get('industry'),
        website=data.get('website'),
        description=data.get('description')
    )
    
    try:
        db.session.add(organization)
        db.session.commit()
        return jsonify({
            'id': organization.id,
            'name': organization.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 