from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from . import bp
from app.models import Customer, Organization, Interaction
from app import db
from datetime import datetime
import logging

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    organization_id = request.args.get('organization_id', type=int)
    sort = request.args.get('sort', 'name')

    query = Customer.query.filter_by(assigned_user_id=current_user.id)

    if search:
        query = query.filter(Customer.name.ilike(f'%{search}%'))
    if status:
        query = query.filter_by(status=status)
    if organization_id:
        query = query.filter_by(organization_id=organization_id)

    if sort == 'name':
        query = query.order_by(Customer.name)
    elif sort == 'created_at':
        query = query.order_by(Customer.created_at.desc())
    elif sort == 'last_contact':
        query = query.order_by(Customer.last_contact.desc())

    pagination = query.paginate(page=page, per_page=10)
    customers = pagination.items

    # Get organizations for filter
    organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()

    return render_template('customers/index.html',
                         customers=customers,
                         pagination=pagination,
                         organizations=organizations)

@bp.route('/<int:customer_id>')
@login_required
def show(customer_id):
    customer = Customer.query.filter_by(id=customer_id, assigned_user_id=current_user.id).first_or_404()
    # Get recent interactions, ordered by timestamp
    interactions = Interaction.query.filter_by(customer_id=customer.id).order_by(Interaction.timestamp.desc()).all()
    return render_template('customers/show.html', customer=customer, interactions=interactions)

@bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    customer = Customer.query.filter_by(id=customer_id, assigned_user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('name'):
                flash('Customer name is required.', 'danger')
                return render_template('customers/form.html', customer=customer)

            if not request.form.get('organization_id'):
                flash('Organization is required.', 'danger')
                return render_template('customers/form.html', customer=customer)

            # Verify organization belongs to user's workspace
            organization = Organization.query.filter_by(
                id=request.form.get('organization_id', type=int),
                workspace_id=current_user.workspaces[0].id
            ).first()

            if not organization:
                flash('Invalid organization selected.', 'danger')
                return render_template('customers/form.html', customer=customer)

            # Update customer
            customer.name = request.form.get('name')
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')
            customer.status = request.form.get('status')
            customer.notes = request.form.get('notes')
            customer.last_contact = datetime.utcnow()
            customer.organization_id = organization.id
            
            db.session.commit()
            
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers.show', customer_id=customer.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the customer. Please try again.', 'danger')
            logging.error(f'Error updating customer: {str(e)}')
            return render_template('customers/form.html', customer=customer)
    
    # GET request - show the edit form
    organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()
    return render_template('customers/form.html', customer=customer, organizations=organizations)

@bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    customer = Customer.query.filter_by(id=customer_id, assigned_user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the customer.', 'danger')
        logging.error(f'Error deleting customer: {str(e)}')
        return redirect(url_for('customers.show', customer_id=customer.id))
    
    return redirect(url_for('customers.index'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    organization_id = request.args.get('organization_id', type=int)
    organization = None
    if organization_id:
        organization = Organization.query.filter_by(
            id=organization_id,
            workspace_id=current_user.workspaces[0].id
        ).first_or_404()

    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('name'):
                flash('Customer name is required.', 'danger')
                organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()
                return render_template('customers/form.html', organizations=organizations, organization=organization)

            if not request.form.get('organization_id'):
                flash('Organization is required.', 'danger')
                organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()
                return render_template('customers/form.html', organizations=organizations, organization=organization)

            # Verify organization belongs to user's workspace
            selected_org = Organization.query.filter_by(
                id=request.form.get('organization_id', type=int),
                workspace_id=current_user.workspaces[0].id
            ).first()

            if not selected_org:
                flash('Invalid organization selected.', 'danger')
                organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()
                return render_template('customers/form.html', organizations=organizations, organization=organization)

            # Create new customer
            customer = Customer(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                status=request.form.get('status', 'Lead'),
                notes=request.form.get('notes'),
                organization_id=selected_org.id,
                assigned_user_id=current_user.id,
                workspace_id=current_user.workspaces[0].id,
                created_at=datetime.utcnow(),
                last_contact=datetime.utcnow()
            )
            
            db.session.add(customer)
            db.session.commit()
            
            flash('Customer added successfully!', 'success')
            return redirect(url_for('customers.show', customer_id=customer.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the customer. Please try again.', 'danger')
            logging.error(f'Error creating customer: {str(e)}')
            organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()
            return render_template('customers/form.html', organizations=organizations, organization=organization)
            
    # GET request - show the create form
    organizations = Organization.query.filter_by(workspace_id=current_user.workspaces[0].id).all()
    return render_template('customers/form.html', organizations=organizations, organization=organization) 