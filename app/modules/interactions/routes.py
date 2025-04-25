from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp
from app.models import Interaction, Contact, User
from app import db
from datetime import datetime, time
import logging
from .forms import InteractionForm
from app.utils.decorators import permission_required

# Exported constants for use in other modules
INTERACTION_TYPES = list(Interaction.TYPE_CHOICES.items())
INTERACTION_PRIORITIES = list(Interaction.PRIORITY_CHOICES.items())
INTERACTION_STATUSES = list(Interaction.STATUS_CHOICES.items())

@bp.route('/')
@login_required
@permission_required('interaction_view')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    interaction_type = request.args.get('type', '')
    contact_id = request.args.get('contact_id', type=int)
    sort = request.args.get('sort', 'created_at')

    # Base query - get interactions for contacts created by the current user
    query = Interaction.query.join(Contact).filter(Contact.created_by_id == current_user.id)

    if search:
        query = query.filter(Interaction.title.ilike(f'%{search}%'))
    if interaction_type:
        query = query.filter(Interaction.type == interaction_type)
    if contact_id:
        query = query.filter(Interaction.contact_id == contact_id)

    if sort == 'created_at':
        query = query.order_by(Interaction.created_at.desc())
    elif sort == 'contact':
        query = query.join(Contact).order_by(Contact.first_name, Contact.last_name)

    pagination = query.paginate(page=page, per_page=10)
    interactions = pagination.items

    # Get contacts for filter
    contacts = Contact.query.filter_by(created_by_id=current_user.id).all()

    return render_template('interactions/index.html',
                         interactions=interactions,
                         pagination=pagination,
                         contacts=contacts,
                         interaction_types=Interaction.TYPE_CHOICES,
                         Interaction=Interaction)

@bp.route('/timeline/<int:contact_id>')
@login_required
@permission_required('interaction_view')
def timeline(contact_id):
    """Show the contact journey timeline with all interactions"""
    contact = Contact.query.filter_by(id=contact_id, created_by_id=current_user.id).first_or_404()
    
    # Get all interactions for this contact, ordered by date (newest first)
    interactions = Interaction.query.filter_by(contact_id=contact_id).order_by(Interaction.date.desc()).all()
    
    return render_template('interactions/timeline.html',
                         contact=contact,
                         interactions=interactions)

@bp.route('/<int:interaction_id>')
@login_required
@permission_required('interaction_view')
def show(interaction_id):
    interaction = Interaction.query.join(Contact).filter(
        Interaction.id == interaction_id,
        Contact.created_by_id == current_user.id
    ).first_or_404()
    return render_template('interactions/detail.html', interaction=interaction, Interaction=Interaction)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('interaction_create')
def create():
    form = InteractionForm()
    contact_id = request.args.get('contact_id', type=int)
    contact = Contact.query.filter_by(id=contact_id, created_by_id=current_user.id).first_or_404() if contact_id else None

    if form.validate_on_submit():
        try:
            interaction = Interaction(
                contact_id=contact_id,
                type=form.type.data,
                title=form.title.data,
                description=form.description.data,
                date=datetime.combine(form.date.data, time.min) if form.date.data else None,
                status=form.status.data,
                priority=form.priority.data,
                next_steps=form.next_steps.data,
                created_by_id=current_user.id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(interaction)
            db.session.commit()
            
            flash('Interaction recorded successfully!', 'success')
            return redirect(url_for('contacts.show', id=interaction.contact_id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while recording the interaction. Please try again.', 'danger')
            logging.error(f'Error creating interaction: {str(e)}')
            return render_template('interactions/form.html', form=form, contact=contact, interaction=None, Interaction=Interaction)

    # GET request or form validation failed
    return render_template('interactions/form.html', form=form, contact=contact, interaction=None, Interaction=Interaction)

@bp.route('/<int:interaction_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('interaction_edit')
def edit(interaction_id):
    interaction = Interaction.query.join(Contact).filter(
        Interaction.id == interaction_id,
        Contact.created_by_id == current_user.id
    ).first_or_404()
    
    form = InteractionForm(obj=interaction)
    
    if form.validate_on_submit():
        try:
            interaction.type = form.type.data
            interaction.title = form.title.data
            interaction.description = form.description.data
            interaction.date = datetime.combine(form.date.data, time.min) if form.date.data else None
            interaction.status = form.status.data
            interaction.priority = form.priority.data
            interaction.next_steps = form.next_steps.data
            
            db.session.commit()
            
            flash('Interaction updated successfully!', 'success')
            return redirect(url_for('interactions.show', interaction_id=interaction.id))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the interaction. Please try again.', 'danger')
            logging.error(f'Error updating interaction: {str(e)}')
            return render_template('interactions/form.html', form=form, contact=interaction.contact, interaction=interaction, Interaction=Interaction)
    
    # GET request - populate date fields only
    if interaction.date:
        form.date.data = interaction.date.date()
    
    return render_template('interactions/form.html', form=form, contact=interaction.contact, interaction=interaction, Interaction=Interaction)

@bp.route('/<int:interaction_id>/delete', methods=['POST'])
@login_required
@permission_required('interaction_delete')
def delete(interaction_id):
    interaction = Interaction.query.join(Contact).filter(
        Interaction.id == interaction_id,
        Contact.created_by_id == current_user.id
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
@permission_required('interaction_edit')
def analyze(interaction_id):
    interaction = Interaction.query.join(Contact).filter(
        Interaction.id == interaction_id,
        Contact.created_by_id == current_user.id
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