from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp
from app.models import Interaction, Customer
from app import db
from datetime import datetime
import logging

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    interaction_type = request.args.get('type', '')
    customer_id = request.args.get('customer_id', type=int)
    sort = request.args.get('sort', 'created_at')

    query = Interaction.query.join(Customer).filter(Customer.assigned_to_id == current_user.id)

    if search:
        query = query.filter(Interaction.summary.ilike(f'%{search}%'))
    if interaction_type:
        query = query.filter_by(type=interaction_type)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)

    if sort == 'created_at':
        query = query.order_by(Interaction.created_at.desc())
    elif sort == 'customer':
        query = query.join(Customer).order_by(Customer.full_name)

    pagination = query.paginate(page=page, per_page=10)
    interactions = pagination.items

    # Get customers for filter
    customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()

    return render_template('interactions/index.html',
                         interactions=interactions,
                         pagination=pagination,
                         customers=customers)

@bp.route('/<int:interaction_id>')
@login_required
def show(interaction_id):
    interaction = Interaction.query.join(Customer).filter(
        Interaction.id == interaction_id,
        Customer.assigned_to_id == current_user.id
    ).first_or_404()
    return render_template('interactions/show.html', interaction=interaction)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            # Parse timestamp from form
            created_at_str = request.form.get('created_at')
            if created_at_str:
                created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
            else:
                created_at = datetime.utcnow()

            # Create new interaction
            interaction = Interaction(
                customer_id=request.form.get('customer_id', type=int),
                type=request.form.get('type'),
                summary=request.form.get('summary'),
                notes=request.form.get('notes'),
                outcome=request.form.get('outcome'),
                created_at=created_at,
                created_by_id=current_user.id
            )
            
            # Set follow-up date if provided
            follow_up_date_str = request.form.get('follow_up_date')
            if follow_up_date_str:
                interaction.follow_up_date = datetime.strptime(follow_up_date_str, '%Y-%m-%d').date()
            
            interaction.follow_up_notes = request.form.get('follow_up_notes')
            
            db.session.add(interaction)
            db.session.commit()
            
            flash('Interaction recorded successfully!', 'success')
            return redirect(url_for('customers.show', id=interaction.customer_id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while recording the interaction. Please try again.', 'danger')
            logging.error(f'Error creating interaction: {str(e)}')
            return redirect(url_for('customers.show', id=request.form.get('customer_id', type=int)))

    # GET requests should be redirected to the customer page
    customer_id = request.args.get('customer_id', type=int)
    if customer_id:
        return redirect(url_for('customers.show', id=customer_id))
    return redirect(url_for('customers.index'))

@bp.route('/<int:interaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(interaction_id):
    interaction = Interaction.query.join(Customer).filter(
        Interaction.id == interaction_id,
        Customer.assigned_to_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        try:
            # Validate required fields
            if not request.form.get('type'):
                flash('Interaction type is required.', 'danger')
                customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()
                return render_template('interactions/form.html', interaction=interaction, customers=customers)

            if not request.form.get('summary'):
                flash('Summary is required.', 'danger')
                customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()
                return render_template('interactions/form.html', interaction=interaction, customers=customers)

            if not request.form.get('outcome'):
                flash('Outcome is required.', 'danger')
                customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()
                return render_template('interactions/form.html', interaction=interaction, customers=customers)

            # Parse timestamp from form
            created_at_str = request.form.get('created_at')
            if created_at_str:
                created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
            else:
                created_at = interaction.created_at

            # Parse follow-up date if provided
            follow_up_date = None
            follow_up_date_str = request.form.get('follow_up_date')
            if follow_up_date_str:
                follow_up_date = datetime.strptime(follow_up_date_str, '%Y-%m-%d').date()

            # Update interaction
            interaction.type = request.form.get('type')
            interaction.summary = request.form.get('summary')
            interaction.notes = request.form.get('notes')
            interaction.outcome = request.form.get('outcome')
            interaction.created_at = created_at
            interaction.follow_up_date = follow_up_date
            interaction.follow_up_notes = request.form.get('follow_up_notes')
            
            db.session.commit()
            
            flash('Interaction updated successfully!', 'success')
            return redirect(url_for('interactions.show', interaction_id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the interaction. Please try again.', 'danger')
            logging.error(f'Error updating interaction: {str(e)}')
            customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()
            return render_template('interactions/form.html', interaction=interaction, customers=customers)
    
    # GET request - show the edit form
    customers = Customer.query.filter_by(assigned_to_id=current_user.id).all()
    return render_template('interactions/form.html', interaction=interaction, customers=customers)

@bp.route('/<int:interaction_id>/delete', methods=['POST'])
@login_required
def delete(interaction_id):
    interaction = Interaction.query.join(Customer).filter(
        Interaction.id == interaction_id,
        Customer.assigned_to_id == current_user.id
    ).first_or_404()
    
    try:
        db.session.delete(interaction)
        db.session.commit()
        flash('Interaction deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the interaction.', 'danger')
        logging.error(f'Error deleting interaction: {str(e)}')
        return redirect(url_for('interactions.show', interaction_id=interaction.id))
    
    return redirect(url_for('interactions.index'))

@bp.route('/<int:interaction_id>/analyze', methods=['POST'])
@login_required
def analyze(interaction_id):
    interaction = Interaction.query.join(Customer).filter(
        Interaction.id == interaction_id,
        Customer.assigned_to_id == current_user.id
    ).first_or_404()
    
    try:
        # Here you would integrate with an AI service to analyze the interaction
        # For now, we'll just set a placeholder analysis
        interaction.ai_analysis = "This is a placeholder AI analysis of the interaction."
        db.session.commit()
        flash('Interaction analyzed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while analyzing the interaction.', 'danger')
        logging.error(f'Error analyzing interaction: {str(e)}')
    
    return redirect(url_for('interactions.show', interaction_id=interaction.id)) 