from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Contact, Organization, User, Interaction
from collections import defaultdict

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all contacts for the current user
    contacts = Contact.query.filter_by(created_by_id=current_user.id).all()
    
    # Calculate contact statistics
    total_contacts = len(contacts)
    total_customers = sum(1 for c in contacts if c.stage == 'customer')
    total_leads = sum(1 for c in contacts if c.stage == 'lead')
    active_customers = sum(1 for c in contacts if c.stage == 'customer' and c.is_active)
    active_leads = sum(1 for c in contacts if c.stage == 'lead' and c.is_active)
    
    # Get recent activities (combining contacts and interactions)
    recent_activities = []
    
    # Add recent contacts
    recent_contacts = Contact.query.filter_by(
        created_by_id=current_user.id
    ).order_by(Contact.created_at.desc()).limit(5).all()
    recent_activities.extend(recent_contacts)
    
    # Add recent interactions
    contact_ids = [c.id for c in contacts]
    recent_interactions = Interaction.query.filter(
        Interaction.contact_id.in_(contact_ids)
    ).order_by(Interaction.created_at.desc()).limit(5).all()
    recent_activities.extend(recent_interactions)
    
    # Sort activities by creation date
    recent_activities.sort(key=lambda x: x.created_at, reverse=True)
    recent_activities = recent_activities[:10]  # Keep only the 10 most recent
    
    # Get contact stage distribution
    stage_distribution = defaultdict(int)
    for contact in contacts:
        stage = contact.stage or 'unknown'
        stage_distribution[stage] += 1
    
    # Get interactions by type
    interaction_types = defaultdict(int)
    for interaction in Interaction.query.filter(
        Interaction.contact_id.in_(contact_ids)
    ).all():
        interaction_type = interaction.type or 'unknown'
        interaction_types[interaction_type] += 1
    
    # Get contacts by month
    contacts_by_month = defaultdict(int)
    for contact in contacts:
        month = contact.created_at.strftime('%Y-%m')
        contacts_by_month[month] += 1
    
    # Sort months chronologically
    sorted_months = sorted(contacts_by_month.keys())
    
    # Get contacts by source
    contacts_by_source = {}
    sources = ['website', 'referral', 'social', 'email', 'other']
    for source in sources:
        contacts_by_source[source] = sum(1 for c in contacts if c.source == source)
    
    return render_template('dashboard.html',
                         total_contacts=total_contacts,
                         total_customers=total_customers,
                         total_leads=total_leads,
                         active_customers=active_customers,
                         active_leads=active_leads,
                         recent_activities=recent_activities,
                         stage_distribution=dict(stage_distribution),
                         interaction_types=dict(interaction_types),
                         contacts_by_month=contacts_by_month,
                         sorted_months=sorted_months,
                         contacts_by_source=contacts_by_source) 