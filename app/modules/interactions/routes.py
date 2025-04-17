from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import interactions_bp
from app.models import Interaction, Customer
from app import db
from datetime import datetime
import logging

@interactions_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get filter parameters
    search = request.args.get('search', '')
    interaction_type = request.args.get('type', '')
    sort = request.args.get('sort', 'timestamp')
    order = request.args.get('order', 'desc')
    
    # Get all customers for the current user
    customer_ids = [c.id for c in Customer.query.filter_by(user_id=current_user.id).all()]
    
    # Base query
    query = Interaction.query.filter(Interaction.customer_id.in_(customer_ids))
    
    # Apply filters
    if search:
        query = query.filter(
            (Interaction.summary.ilike(f'%{search}%')) |
            (Interaction.details.ilike(f'%{search}%'))
        )
    
    if interaction_type:
        query = query.filter(Interaction.type == interaction_type)
    
    # Apply sorting
    if sort == 'timestamp':
        query = query.order_by(Interaction.timestamp.desc() if order == 'desc' else Interaction.timestamp.asc())
    elif sort == 'type':
        query = query.order_by(Interaction.type.desc() if order == 'desc' else Interaction.type.asc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    interactions = pagination.items
    
    # Get unique interaction types for filter dropdown
    interaction_types = db.session.query(Interaction.type).distinct().all()
    interaction_types = [t[0] for t in interaction_types]
    
    return render_template('interactions/index.html', 
                          interactions=interactions, 
                          pagination=pagination,
                          search=search,
                          interaction_type=interaction_type,
                          sort=sort,
                          order=order,
                          interaction_types=interaction_types)

@interactions_bp.route('/<int:interaction_id>')
@login_required
def detail(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    # Check if the interaction belongs to the current user's customer
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions.index'))
    
    return render_template('interactions/detail.html', 
                         interaction=interaction, 
                         customer=customer)

@interactions_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('customer_id'):
                flash('Customer is required.', 'danger')
                return render_template('interactions/create.html')
            
            if not request.form.get('type'):
                flash('Interaction type is required.', 'danger')
                return render_template('interactions/create.html')
            
            if not request.form.get('summary'):
                flash('Summary is required.', 'danger')
                return render_template('interactions/create.html')
            
            # Create new interaction
            interaction = Interaction(
                customer_id=request.form.get('customer_id'),
                type=request.form.get('type'),
                summary=request.form.get('summary'),
                details=request.form.get('details'),
                timestamp=datetime.utcnow()
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            flash('Interaction created successfully!', 'success')
            return redirect(url_for('interactions.detail', interaction_id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the interaction. Please try again.', 'danger')
            logging.error(f'Error creating interaction: {str(e)}')
            return render_template('interactions/create.html')
    
    # Get all customers for the current user
    customers = Customer.query.filter_by(user_id=current_user.id).all()
    
    return render_template('interactions/create.html', customers=customers)

@interactions_bp.route('/<int:interaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    # Check if the interaction belongs to the current user's customer
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions.index'))
    
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('type'):
                flash('Interaction type is required.', 'danger')
                return render_template('interactions/edit.html', interaction=interaction)
            
            if not request.form.get('summary'):
                flash('Summary is required.', 'danger')
                return render_template('interactions/edit.html', interaction=interaction)
            
            # Update interaction
            interaction.type = request.form.get('type')
            interaction.summary = request.form.get('summary')
            interaction.details = request.form.get('details')
            
            db.session.commit()
            
            flash('Interaction updated successfully!', 'success')
            return redirect(url_for('interactions.detail', interaction_id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the interaction. Please try again.', 'danger')
            logging.error(f'Error updating interaction: {str(e)}')
            return render_template('interactions/edit.html', interaction=interaction)
    
    return render_template('interactions/edit.html', interaction=interaction)

@interactions_bp.route('/<int:interaction_id>/delete', methods=['POST'])
@login_required
def delete(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    # Check if the interaction belongs to the current user's customer
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions.index'))
    
    try:
        db.session.delete(interaction)
        db.session.commit()
        flash('Interaction deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the interaction. Please try again.', 'danger')
        logging.error(f'Error deleting interaction: {str(e)}')
    
    return redirect(url_for('interactions.index'))

@interactions_bp.route('/<int:interaction_id>/analyze', methods=['POST'])
@login_required
def analyze(interaction_id):
    interaction = Interaction.query.get_or_404(interaction_id)
    customer = Customer.query.get_or_404(interaction.customer_id)
    
    # Check if the interaction belongs to the current user's customer
    if customer.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('interactions.index'))
    
    try:
        # Get analysis type from form
        analysis_type = request.form.get('analysis_type', 'general')
        
        # Get text to analyze
        text = f"{interaction.summary}\n\n{interaction.details or ''}"
        
        # Analyze with LLM
        from app import analyze_with_llm
        analysis = analyze_with_llm(text, analysis_type)
        
        # Update interaction with analysis
        interaction.ai_analysis = analysis
        db.session.commit()
        
        flash('Analysis completed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while analyzing the interaction. Please try again.', 'danger')
        logging.error(f'Error analyzing interaction: {str(e)}')
    
    return redirect(url_for('interactions.detail', interaction_id=interaction.id)) 