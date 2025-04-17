from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user
from app.models import Customer, Interaction
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Show landing page for non-authenticated users, redirect to dashboard for authenticated users"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html', now=datetime.utcnow())

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Show the dashboard with summary statistics"""
    # Get all customers for the current user
    customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()
    
    # Calculate customer statistics
    total_customers = len(customers)
    active_customers = sum(1 for c in customers if c.status == 'Active')
    lead_customers = sum(1 for c in customers if c.status == 'Lead')
    lost_customers = sum(1 for c in customers if c.status == 'Lost')
    
    # Get recent customers (last 5)
    recent_customers = Customer.query.filter_by(assigned_to_id=current_user.id).order_by(Customer.created_at.desc()).limit(5).all()
    
    # Get all interactions for the current user's customers
    customer_ids = [c.id for c in customers]
    recent_interactions = Interaction.query.filter(Interaction.customer_id.in_(customer_ids)).order_by(Interaction.created_at.desc()).limit(5).all()
    
    # Get customer status distribution
    status_distribution = {}
    for customer in customers:
        status = customer.status
        if status in status_distribution:
            status_distribution[status] += 1
        else:
            status_distribution[status] = 1
    
    # Get interactions by type
    interaction_types = {}
    for interaction in Interaction.query.filter(Interaction.customer_id.in_(customer_ids)).all():
        interaction_type = interaction.type
        if interaction_type in interaction_types:
            interaction_types[interaction_type] += 1
        else:
            interaction_types[interaction_type] = 1
    
    return render_template('main/dashboard.html',
                          customers=customers,
                          total_customers=total_customers,
                          active_customers=active_customers,
                          lead_customers=lead_customers,
                          lost_customers=lost_customers,
                          recent_customers=recent_customers,
                          recent_interactions=recent_interactions,
                          status_distribution=status_distribution,
                          interaction_types=interaction_types) 