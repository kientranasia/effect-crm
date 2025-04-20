from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from . import bp
from app.models import Customer, Organization, Interaction
from app import db
from datetime import datetime
import logging

@bp.route('/customers')
@login_required
def index():
    query = Customer.query
    customers = query.all()
    return render_template('customers/index.html', customers=customers)

@bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        customer.company = request.form.get('company')
        db.session.commit()
        flash('Customer updated successfully.', 'success')
        return redirect(url_for('customers.index'))
    return render_template('customers/edit.html', customer=customer)

@bp.route('/customers/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully.', 'success')
    return redirect(url_for('customers.index'))

@bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            company=request.form.get('company'),
            created_by=current_user.id
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer created successfully.', 'success')
        return redirect(url_for('customers.index'))
    return render_template('customers/create.html')

@bp.route('/<int:customer_id>')
@login_required
def show(customer_id):
    customer = Customer.query.filter_by(id=customer_id, assigned_user_id=current_user.id).first_or_404()
    # Get recent interactions, ordered by timestamp
    interactions = Interaction.query.filter_by(customer_id=customer.id).order_by(Interaction.timestamp.desc()).all()
    return render_template('customers/show.html', customer=customer, interactions=interactions) 