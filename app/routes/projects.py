from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.models.organization import Organization
from app.extensions import db
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Optional
from app.utils.decorators import permission_required

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])

bp = Blueprint('projects', __name__)

@bp.route('/projects')
@login_required
@permission_required('project_view')
def index():
    """List all projects"""
    projects = Project.query.all()
    return render_template('projects/index.html', projects=projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
@permission_required('project_create')
def create():
    """Create a new project"""
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            created_by_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully.', 'success')
        return redirect(url_for('projects.show', id=project.id))
    
    return render_template('projects/form.html', form=form, title='New Project')

@bp.route('/projects/<int:id>')
@login_required
@permission_required('project_view')
def show(id):
    """Show project details"""
    project = Project.query.get_or_404(id)
    tasks_by_status = {
        'todo': Task.query.filter_by(project_id=id, status='todo').order_by(Task.position).all(),
        'in_progress': Task.query.filter_by(project_id=id, status='in_progress').order_by(Task.position).all(),
        'on_hold': Task.query.filter_by(project_id=id, status='on_hold').order_by(Task.position).all(),
        'completed': Task.query.filter_by(project_id=id, status='completed').order_by(Task.position).all()
    }
    users = User.query.all()
    organizations = Organization.query.filter_by(created_by_id=current_user.id).all()
    
    # Import Contact model and get all contacts
    from app.models.contact import Contact
    contacts = Contact.query.all()
    
    return render_template('projects/show.html', 
                         project=project, 
                         tasks_by_status=tasks_by_status, 
                         users=users, 
                         organizations=organizations,
                         contacts=contacts,
                         Task=Task)

@bp.route('/projects/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('project_edit')
def edit(id):
    """Edit a project"""
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.start_date = form.start_date.data
        project.end_date = form.end_date.data
        project.status = form.status.data
        
        db.session.commit()
        flash('Project updated successfully.', 'success')
        return redirect(url_for('projects.show', id=project.id))
    
    return render_template('projects/form.html', form=form, project=project, title='Edit Project')

@bp.route('/projects/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('project_delete')
def delete(id):
    """Delete a project"""
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully.', 'success')
    return redirect(url_for('projects.index'))

@bp.route('/projects/<int:id>/add_milestone', methods=['POST'])
@login_required
@permission_required('project_edit')
def add_milestone(id):
    project = Project.query.get_or_404(id)
    milestone = {
        'title': request.form['title'],
        'description': request.form.get('description'),
        'due_date': datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form.get('due_date') else None,
        'status': 'pending'
    }
    project.milestones.append(milestone)
    db.session.commit()
    flash('Milestone added successfully.', 'success')
    return redirect(url_for('projects.show', id=project.id))

@bp.route('/projects/<int:id>/add_team_member_form', methods=['POST'])
@login_required
@permission_required('project_edit')
def add_team_member_form(id):
    """Add a team member to the project using form submission"""
    project = Project.query.get_or_404(id)
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('User ID is required', 'error')
        return redirect(url_for('projects.show', id=id))
        
    user = User.query.get_or_404(user_id)
    
    if user in project.team_members:
        flash('User is already a team member', 'error')
        return redirect(url_for('projects.show', id=id))
    
    try:
        project.team_members.append(user)
        db.session.commit()
        flash('Team member added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding team member: {str(e)}', 'error')
    
    return redirect(url_for('projects.show', id=id))

@bp.route('/projects/<int:id>/remove_team_member_form/<int:user_id>', methods=['POST'])
@login_required
@permission_required('project_edit')
def remove_team_member_form(id, user_id):
    """Remove a team member from the project using form submission"""
    project = Project.query.get_or_404(id)
    user = User.query.get_or_404(user_id)
    
    # Check if user is a team member
    if user not in project.team_members:
        flash('User is not a team member', 'error')
        return redirect(url_for('projects.show', id=id))
    
    try:
        # Use the Project model's remove_team_member method
        project.remove_team_member(user)
        flash('Team member removed successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing team member: {str(e)}', 'error')
    
    return redirect(url_for('projects.show', id=id))

@bp.route('/projects/<int:id>/link-organization', methods=['POST'])
@login_required
@permission_required('project_edit')
def link_organization(id):
    """Link an organization to a project"""
    project = Project.query.get_or_404(id)
    data = request.get_json()
    
    if not data or 'organization_id' not in data:
        return jsonify({'success': False, 'message': 'Organization ID is required'}), 400
        
    organization = Organization.query.get_or_404(data['organization_id'])
    
    # Check if user has access to the organization
    if organization.created_by_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        project.organization_id = organization.id
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Organization linked successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/projects/<int:id>/unlink-organization', methods=['POST'])
@login_required
@permission_required('project_edit')
def unlink_organization(id):
    """Unlink an organization from a project"""
    project = Project.query.get_or_404(id)
    
    try:
        project.organization_id = None
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Organization unlinked successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 