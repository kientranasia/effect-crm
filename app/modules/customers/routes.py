from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import customers_bp
from app.models import Customer
from app import db
from datetime import datetime
import logging

@customers_bp.route('/')
@login_required
def index():
    customers = Customer.query.filter_by(user_id=current_user.id).order_by(Customer.created_at.desc()).all()
    return render_template('customers/index.html', customers=customers)

@customers_bp.route('/<int:customer_id>')
@login_required
def show(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    return render_template('customers/show.html', customer=customer)

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('name'):
                flash('Customer name is required.', 'danger')
                return render_template('customers/edit.html', customer=customer)

            # Update customer
            customer.name = request.form.get('name')
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')
            customer.status = request.form.get('status')
            customer.notes = request.form.get('notes')
            customer.last_contact = datetime.utcnow()
            
            db.session.commit()
            
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers.show', customer_id=customer.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the customer. Please try again.', 'danger')
            logging.error(f'Error updating customer: {str(e)}')
            return render_template('customers/edit.html', customer=customer)
    
    # GET request - show the edit form
    return render_template('customers/edit.html', customer=customer)

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id):
    customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first_or_404()
    
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

@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('name'):
                flash('Customer name is required.', 'danger')
                return render_template('customers/create.html')

            # Create new customer
            customer = Customer(
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                status=request.form.get('status', 'Lead'),
                notes=request.form.get('notes'),
                user_id=current_user.id,
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
            return render_template('customers/create.html')
            
    # GET request - show the create form
    return render_template('customers/create.html') 