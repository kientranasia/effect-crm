from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Contact, Organization, User, Interaction, Task, Project, Activity
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import func
from app.utils.filters import parse_datetime

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
    contact_ids = [c.id for c in contacts]
    
    # Calculate basic statistics
    total_contacts = len(contacts)
    total_interactions = Interaction.query.filter(
        Interaction.contact_id.in_(contact_ids)
    ).count()
    pending_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status != 'completed'
    ).count()
    active_projects = Project.query.filter(
        Project.created_by_id == current_user.id,
        Project.status == 'active'
    ).count()
    
    # Get recent activities
    recent_activities = Activity.query.filter(
        Activity.user_id == current_user.id
    ).order_by(Activity.created_at.desc()).limit(5).all()
    
    # Get upcoming tasks
    upcoming_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status != 'completed',
        Task.due_date >= datetime.now()
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    # Get recent interactions
    recent_interactions = Interaction.query.filter(
        Interaction.contact_id.in_(contact_ids)
    ).order_by(Interaction.created_at.desc()).limit(5).all()
    
    # Get interaction trends for the chart
    last_30_days = datetime.now() - timedelta(days=30)
    interaction_trends = Interaction.query.filter(
        Interaction.contact_id.in_(contact_ids),
        Interaction.created_at >= last_30_days
    ).with_entities(
        func.date(Interaction.created_at).label('date'),
        func.count(Interaction.id).label('count')
    ).group_by(
        func.date(Interaction.created_at)
    ).order_by(
        func.date(Interaction.created_at)
    ).all()
    
    # Format data for the chart
    interaction_dates = [parse_datetime(trend.date).strftime('%Y-%m-%d') for trend in interaction_trends]
    interaction_counts = [trend.count for trend in interaction_trends]
    
    # Get all users for task assignment
    users = User.query.all()
    
    return render_template('dashboard.html',
                         total_contacts=total_contacts,
                         total_interactions=total_interactions,
                         pending_tasks=pending_tasks,
                         active_projects=active_projects,
                         recent_activities=recent_activities,
                         upcoming_tasks=upcoming_tasks,
                         recent_interactions=recent_interactions,
                         interaction_dates=interaction_dates,
                         interaction_counts=interaction_counts,
                         contacts=contacts,
                         users=users) 