from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import Workspace, User
from datetime import datetime

bp = Blueprint('workspace', __name__)

@bp.route('/workspace/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Workspace name is required.', 'error')
            return render_template('workspace/create.html')
            
        workspace = Workspace(
            name=name,
            description=description,
            owner_id=current_user.id,
            created_at=datetime.utcnow()
        )
        
        # Add the current user to the workspace
        workspace.users.append(current_user)
        
        db.session.add(workspace)
        db.session.commit()
        
        flash('Workspace created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('workspace/create.html')

@bp.route('/workspace/<int:workspace_id>')
@login_required
def view(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if workspace not in current_user.workspaces:
        flash('You do not have access to this workspace.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('workspace/view.html', workspace=workspace)

@bp.route('/workspace/<int:workspace_id>/settings', methods=['GET', 'POST'])
@login_required
def settings(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if workspace.owner_id != current_user.id:
        flash('Only workspace owner can modify settings.', 'error')
        return redirect(url_for('workspace.view', workspace_id=workspace_id))
        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Workspace name is required.', 'error')
            return render_template('workspace/settings.html', workspace=workspace)
            
        workspace.name = name
        workspace.description = description
        db.session.commit()
        
        flash('Workspace settings updated successfully!', 'success')
        return redirect(url_for('workspace.view', workspace_id=workspace_id))
        
    return render_template('workspace/settings.html', workspace=workspace) 