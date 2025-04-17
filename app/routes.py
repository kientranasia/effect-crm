from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, login_user
from app import db
from app.models import Customer, Interaction, User, Role, Workspace
from collections import defaultdict
from werkzeug.security import generate_password_hash

def init_app(app):
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # Redirect to the auth blueprint's register route
        return redirect(url_for('auth.register'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get user's workspaces
        workspaces = current_user.workspaces
        if not workspaces:
            flash('Please join or create a workspace first.', 'warning')
            return redirect(url_for('workspace.create'))
            
        # Use the first workspace for now (you might want to add workspace switching later)
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
        
        # Get recent customers (last 5)
        recent_customers = Customer.query.filter(
            (Customer.workspace_id == current_workspace.id) &
            ((Customer.assigned_user_id == current_user.id) | 
             (Workspace.owner_id == current_user.id))
        ).join(Workspace).order_by(Customer.created_at.desc()).limit(5).all()
        
        # Get all interactions for the current user's customers
        customer_ids = [c.id for c in customers]
        recent_interactions = Interaction.query.filter(
            (Interaction.customer_id.in_(customer_ids)) &
            ((Interaction.created_by_id == current_user.id) |
             (Customer.workspace_id == current_workspace.id))
        ).join(Customer).order_by(Interaction.timestamp.desc()).limit(5).all()
        
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
        for interaction in Interaction.query.filter(
            (Interaction.customer_id.in_(customer_ids)) &
            ((Interaction.created_by_id == current_user.id) |
             (Customer.workspace_id == current_workspace.id))
        ).join(Customer).all():
            interaction_type = interaction.type
            if interaction_type in interaction_types:
                interaction_types[interaction_type] += 1
            else:
                interaction_types[interaction_type] = 1
        
        # Get customers by month (for chart)
        customers_by_month = defaultdict(int)
        for customer in customers:
            month = customer.created_at.strftime('%Y-%m')
            customers_by_month[month] += 1
        
        # Sort months chronologically
        sorted_months = sorted(customers_by_month.keys())
        
        return render_template('dashboard.html', 
                            customers=customers,
                            total_customers=total_customers,
                            active_customers=active_customers,
                            lead_customers=lead_customers,
                            lost_customers=lost_customers,
                            recent_customers=recent_customers,
                            recent_interactions=recent_interactions,
                            status_distribution=status_distribution,
                            interaction_types=interaction_types,
                            customers_by_month=customers_by_month,
                            sorted_months=sorted_months,
                            current_workspace=current_workspace)

    @app.route('/interaction/<int:interaction_id>')
    @login_required
    def interaction_detail(interaction_id):
        interaction = Interaction.query.get_or_404(interaction_id)
        customer = Customer.query.get_or_404(interaction.customer_id)
        
        # Check if the interaction belongs to the current user's workspace
        if customer.workspace_id not in [w.id for w in current_user.workspaces]:
            flash('Unauthorized access', 'error')
            return redirect(url_for('main.dashboard'))
        
        return render_template('interaction_detail.html', 
                             interaction=interaction, 
                             customer=customer) 