from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Task, Project, User
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

bp = Blueprint('tasks', __name__)

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed')
    ], validators=[DataRequired()])
    assigned_to_id = SelectField('Assigned To', coerce=int, validators=[Optional()])

@bp.route('/projects/<int:project_id>/tasks/new', methods=['GET', 'POST'])
@login_required
def create(project_id):
    project = Project.query.get_or_404(project_id)
    form = TaskForm()
    form.assigned_to_id.choices = [(user.id, user.full_name) for user in User.query.all()]
    
    if form.validate_on_submit():
        # Get the maximum position for the current status
        max_position = db.session.query(db.func.max(Task.position)).filter_by(
            project_id=project_id,
            status=form.status.data
        ).scalar() or 0
        
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            status=form.status.data,
            position=max_position + 1,
            project_id=project_id,
            assigned_to_id=form.assigned_to_id.data,
            created_by_id=current_user.id
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully.', 'success')
        return redirect(url_for('projects.show', id=project_id))
    
    return render_template('tasks/form.html', form=form, project=project, title='New Task')

@bp.route('/tasks/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = Task.query.get_or_404(id)
    form = TaskForm(obj=task)
    form.assigned_to_id.choices = [(user.id, user.full_name) for user in User.query.all()]
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.status = form.status.data
        task.assigned_to_id = form.assigned_to_id.data
        
        db.session.commit()
        flash('Task updated successfully.', 'success')
        return redirect(url_for('projects.show', id=task.project_id))
    
    return render_template('tasks/form.html', form=form, task=task, project=task.project, title='Edit Task')

@bp.route('/tasks/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('projects.show', id=project_id))

@bp.route('/tasks/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    
    if 'status' in data:
        # Get the maximum position for the new status
        max_position = db.session.query(db.func.max(Task.position)).filter_by(
            project_id=task.project_id,
            status=data['status']
        ).scalar() or 0
        
        task.status = data['status']
        task.position = max_position + 1
        db.session.commit()
        
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400

@bp.route('/tasks/<int:id>/update-position', methods=['POST'])
@login_required
def update_position(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    
    if 'position' in data:
        task.position = data['position']
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 400 