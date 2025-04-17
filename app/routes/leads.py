from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app import db
from app.models import Lead, Organization, User, Customer
from app.forms import LeadForm
from datetime import datetime

leads_bp = Blueprint('leads', __name__)

class DeleteForm(FlaskForm):
    pass

@leads_bp.route('/leads')
@login_required
def index():
    """List all leads with filtering options"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    assigned_to = request.args.get('assigned_to', 'all')
    form = DeleteForm()
    
    query = Lead.query
    
    if status != 'all':
        query = query.filter(Lead.status == status)
    if assigned_to != 'all':
        try:
            assigned_to_id = int(assigned_to)
            query = query.filter(Lead.assigned_to_id == assigned_to_id)
        except ValueError:
            pass
        
    # Default sort by creation date, newest first
    query = query.order_by(Lead.created_at.desc())
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    leads = pagination.items
    
    # Get all users for the assigned_to filter
    users = User.query.all()
    
    return render_template('leads/index.html', 
                         leads=leads,
                         pagination=pagination,
                         users=users,
                         status_filter=status,
                         assigned_filter=assigned_to,
                         form=form)

@leads_bp.route('/leads/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new lead"""
    if request.method == 'POST':
        lead = Lead(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            job_title=request.form.get('job_title'),
            company_name=request.form.get('company_name'),
            industry=request.form.get('industry'),
            company_size=request.form.get('company_size'),
            website=request.form.get('website'),
            source=request.form.get('source'),
            status=request.form.get('status'),
            notes=request.form.get('notes'),
            assigned_to_id=current_user.id,
            organization_id=request.form.get('organization_id')
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead created successfully.', 'success')
        return redirect(url_for('leads.show', id=lead.id))
    
    organizations = Organization.query.all()
    return render_template('leads/create.html', organizations=organizations)

@leads_bp.route('/leads/<int:id>')
@login_required
def show(id):
    """Show lead details"""
    lead = Lead.query.get_or_404(id)
    return render_template('leads/show.html', lead=lead)

@leads_bp.route('/leads/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a lead"""
    lead = Lead.query.get_or_404(id)
    if request.method == 'POST':
        lead.first_name = request.form.get('first_name')
        lead.last_name = request.form.get('last_name')
        lead.email = request.form.get('email')
        lead.phone = request.form.get('phone')
        lead.job_title = request.form.get('job_title')
        lead.company_name = request.form.get('company_name')
        lead.industry = request.form.get('industry')
        lead.company_size = request.form.get('company_size')
        lead.website = request.form.get('website')
        lead.source = request.form.get('source')
        lead.status = request.form.get('status')
        lead.notes = request.form.get('notes')
        lead.organization_id = request.form.get('organization_id')
        
        db.session.commit()
        flash('Lead updated successfully.', 'success')
        return redirect(url_for('leads.show', id=lead.id))
    
    organizations = Organization.query.all()
    users = User.query.all()
    return render_template('leads/edit.html', lead=lead, organizations=organizations, users=users)

@leads_bp.route('/leads/<int:id>/convert', methods=['POST'])
@login_required
def convert_to_customer(id):
    """Convert a lead to a customer"""
    lead = Lead.query.get_or_404(id)
    
    if lead.converted:
        flash('This lead has already been converted to a customer.', 'warning')
        return redirect(url_for('leads.show', id=lead.id))
    
    # Create new customer from lead
    customer = Customer(
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        phone=lead.phone,
        job_title=lead.job_title,
        company_name=lead.company_name,
        industry=lead.industry,
        company_size=lead.company_size,
        website=lead.website,
        status='active',
        notes=lead.notes,
        assigned_to_id=lead.assigned_to_id,
        organization_id=lead.organization_id,
        converted_from_lead_id=lead.id,
        conversion_notes=request.form.get('notes', '')
    )
    
    db.session.add(customer)
    
    # Update lead status
    lead.converted = True
    lead.converted_date = datetime.utcnow()
    lead.status = 'converted'
    
    db.session.commit()
    
    flash('Lead successfully converted to customer!', 'success')
    return redirect(url_for('customers.show', id=customer.id))

@leads_bp.route('/leads/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    """Update lead status"""
    lead = Lead.query.get_or_404(id)
    lead.status = request.form.get('status')
    db.session.commit()
    flash('Lead status updated successfully!', 'success')
    return redirect(url_for('leads.show', id=lead.id))

@leads_bp.route('/leads/<int:id>/assignment', methods=['POST'])
@login_required
def update_assignment(id):
    """Update lead assignment"""
    lead = Lead.query.get_or_404(id)
    lead.assigned_to_id = request.form.get('assigned_to_id')
    
    if request.form.get('next_follow_up'):
        lead.next_follow_up = datetime.strptime(request.form['next_follow_up'], '%Y-%m-%d')
    
    db.session.commit()
    flash('Lead assignment updated successfully!', 'success')
    return redirect(url_for('leads.show', id=lead.id))

@leads_bp.route('/leads/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a lead"""
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted successfully!', 'success')
    return redirect(url_for('leads.index'))

@leads_bp.route('/leads/import', methods=['GET', 'POST'])
@login_required
def import_leads():
    """Import leads from CSV"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
            
        if file and file.filename.endswith('.csv'):
            # Process CSV file
            # TODO: Implement CSV processing
            flash('Leads imported successfully!', 'success')
            return redirect(url_for('leads.index'))
            
    return render_template('leads/import.html') 