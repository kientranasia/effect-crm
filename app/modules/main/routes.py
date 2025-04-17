from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from app.models import Customer, Interaction, Workspace
from datetime import datetime, timedelta
from collections import defaultdict

@bp.route('/main')
@login_required
def index():
    return render_template('index.html')

@bp.route('/main/dashboard')
@login_required
def dashboard():
    # Get user's workspaces
    workspaces = current_user.workspaces
    if not workspaces:
        flash('Please join or create a workspace first.', 'warning')
        return redirect(url_for('workspace.create'))
        
    # Use the first workspace for now
    current_workspace = workspaces[0]
    
    # Get all customers for the current workspace where user is assigned or is workspace owner
    customers = Customer.query.filter(
        (Customer.workspace_id == current_workspace.id) &
        ((Customer.assigned_user_id == current_user.id) | 
         (Workspace.owner_id == current_user.id))
    ).join(Workspace).all()
    
    # Calculate customer statistics
    total_customers = len(customers)
    active_customers = sum(1 for c in customers if c.status == 'Active')
    lead_customers = sum(1 for c in customers if c.status == 'Lead')
    lost_customers = sum(1 for c in customers if c.status == 'Lost')
    
    # Get recent customers
    recent_customers = Customer.query.filter(
        (Customer.workspace_id == current_workspace.id) &
        ((Customer.assigned_user_id == current_user.id) | 
         (Workspace.owner_id == current_user.id))
    ).join(Workspace).order_by(Customer.created_at.desc()).limit(5).all()
    
    # Get recent interactions
    recent_interactions = Interaction.query.filter(
        Interaction.customer_id.in_([c.id for c in customers])
    ).order_by(Interaction.timestamp.desc()).limit(5).all()
    
    # Calculate customer growth by month
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    customers_by_month = defaultdict(int)
    for customer in customers:
        if customer.created_at >= six_months_ago:
            month = customer.created_at.strftime('%Y-%m')
            customers_by_month[month] += 1
    
    # Sort months for the chart
    sorted_months = sorted(customers_by_month.keys())
    
    return render_template('dashboard.html',
                         customers=customers,
                         total_customers=total_customers,
                         active_customers=active_customers,
                         lead_customers=lead_customers,
                         lost_customers=lost_customers,
                         recent_customers=recent_customers,
                         recent_interactions=recent_interactions,
                         customers_by_month=customers_by_month,
                         sorted_months=sorted_months,
                         current_workspace=current_workspace)

@bp.route('/privacy-policy')
def privacy_policy():
    return render_template('main/privacy_policy.html')

@bp.route('/terms')
def terms():
    return render_template('main/terms.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html') 