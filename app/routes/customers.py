from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.customer import Customer
from app.models.user import User
from app.models import Organization

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
@login_required
def index():
    """List all customers with filtering options"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    assigned_to = request.args.get('assigned_to', 'all')
    search = request.args.get('search', '')
    
    query = Customer.query
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Customer.first_name.ilike(search_term),
                Customer.last_name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.company_name.ilike(search_term)
            )
        )
    
    # Apply status filter
    if status != 'all':
        query = query.filter(Customer.status == status)
    
    # Apply assigned_to filter
    if assigned_to != 'all':
        query = query.filter(Customer.assigned_to_id == assigned_to)
        
    # Default sort by creation date, newest first
    query = query.order_by(Customer.created_at.desc())
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    customers = pagination.items
    
    # Get all users for the assigned_to filter
    users = User.query.all()
    
    return render_template('customers/index.html', 
                         customers=customers,
                         pagination=pagination,
                         users=users,
                         status_filter=status,
                         assigned_filter=assigned_to)

@customers_bp.route('/customers/<int:id>')
@login_required
def show(id):
    """Show customer details"""
    customer = Customer.query.get_or_404(id)
    
    # Get recent activities if any
    activities = []  # You can add activity tracking later
    
    return render_template('customers/show.html', customer=customer)

@customers_bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a customer"""
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.first_name = request.form.get('first_name')
        customer.last_name = request.form.get('last_name')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.job_title = request.form.get('job_title')
        customer.company_name = request.form.get('company_name')
        customer.industry = request.form.get('industry')
        customer.company_size = request.form.get('company_size')
        customer.website = request.form.get('website')
        customer.status = request.form.get('status')
        customer.notes = request.form.get('notes')
        customer.organization_id = request.form.get('organization_id')
        
        db.session.commit()
        flash('Customer updated successfully.', 'success')
        return redirect(url_for('customers.show', id=customer.id))
    
    organizations = Organization.query.all()
    return render_template('customers/edit.html', customer=customer, organizations=organizations)

@customers_bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new customer"""
    if request.method == 'POST':
        try:
            # Check if email already exists
            existing_customer = Customer.query.filter_by(email=request.form.get('email')).first()
            if existing_customer:
                flash('A customer with this email already exists.', 'danger')
                organizations = Organization.query.all()
                return render_template('customers/create.html', 
                                     organizations=organizations,
                                     form=request.form)

            customer = Customer(
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                job_title=request.form.get('job_title'),
                company_name=request.form.get('company_name'),
                industry=request.form.get('industry'),
                company_size=request.form.get('company_size'),
                website=request.form.get('website'),
                status=request.form.get('status', 'active'),
                notes=request.form.get('notes'),
                assigned_to_id=request.form.get('assigned_to_id', current_user.id),
                organization_id=request.form.get('organization_id')
            )
            
            db.session.add(customer)
            db.session.commit()
            
            flash('Customer created successfully.', 'success')
            return redirect(url_for('customers.show', id=customer.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the customer. Please try again.', 'danger')
            organizations = Organization.query.all()
            return render_template('customers/create.html', 
                                 organizations=organizations,
                                 form=request.form)
    
    organizations = Organization.query.all()
    users = User.query.all()
    return render_template('customers/create.html', 
                         organizations=organizations,
                         users=users)

@customers_bp.route('/customers/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a customer"""
    customer = Customer.query.get_or_404(id)
    
    # Delete the customer
    db.session.delete(customer)
    db.session.commit()
    
    flash('Customer deleted successfully.', 'success')
    return redirect(url_for('customers.index')) 