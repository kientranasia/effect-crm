from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Interaction, Contact
from app.forms import InteractionForm
from app import db
from app.utils.decorators import permission_required

interactions_bp = Blueprint('interactions', __name__)

@interactions_bp.route('/interactions')
@login_required
@permission_required('interaction_view')
def index():
    interactions = Interaction.query.all()
    return render_template('interactions/index.html', interactions=interactions)

@interactions_bp.route('/interactions/create', methods=['GET', 'POST'])
@login_required
@permission_required('interaction_create')
def create():
    contact_id = request.args.get('contact_id', type=int)
    if not contact_id:
        flash('Contact ID is required.', 'error')
        return redirect(url_for('contacts.index'))
    
    contact = Contact.query.get_or_404(contact_id)
    form = InteractionForm()
    
    # Pre-populate the form with contact_id and interaction type if provided
    if request.method == 'GET':
        form.contact_id.data = contact_id
        form.type.data = request.args.get('type', 'note')
    
    if form.validate_on_submit():
        # Create new interaction
        interaction = Interaction(
            contact_id=form.contact_id.data,
            type=form.type.data,
            title=form.title.data,
            description=form.description.data,
            date=form.start_date.data,
            priority=form.priority.data,
            status=form.status.data,
            notes=form.notes.data,
            next_steps=form.next_steps.data,
            created_by_id=current_user.id
        )
        
        # Handle end date/time for meetings
        if form.type.data == 'meeting' and form.end_date.data:
            interaction.end_date = form.end_date.data
        
        db.session.add(interaction)
        db.session.commit()
        
        flash('Interaction created successfully.', 'success')
        return redirect(url_for('contacts.show', id=contact_id))
    
    return render_template('interactions/form.html', 
                         form=form, 
                         title='Create Interaction',
                         contact=contact,
                         Interaction=Interaction)

@interactions_bp.route('/interactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('interaction_edit')
def edit(id):
    interaction = Interaction.query.get_or_404(id)
    form = InteractionForm(obj=interaction)
    if form.validate_on_submit():
        interaction.contact_id = form.contact_id.data
        interaction.type = form.type.data
        interaction.description = form.description.data
        interaction.date = form.date.data
        db.session.commit()
        flash('Interaction updated successfully.', 'success')
        return redirect(url_for('interactions.index'))
    return render_template('interactions/form.html', 
                         form=form, 
                         title='Edit Interaction',
                         interaction=interaction,
                         Interaction=Interaction)

@interactions_bp.route('/interactions/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('interaction_delete')
def delete(id):
    interaction = Interaction.query.get_or_404(id)
    db.session.delete(interaction)
    db.session.commit()
    flash('Interaction deleted successfully.', 'success')
    return redirect(url_for('interactions.index')) 