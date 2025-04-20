from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import bp
from app.models import Lead
from app import db

@bp.route('/leads')
@login_required
def index():
    query = Lead.query
    leads = query.all()
    return render_template('leads/index.html', leads=leads)

@bp.route('/leads/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        lead = Lead(
            name=request.form['name'],
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            company=request.form.get('company'),
            status=request.form.get('status', 'New'),
            source=request.form.get('source'),
            notes=request.form.get('notes'),
            created_by=current_user.id
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead created successfully.', 'success')
        return redirect(url_for('leads.index'))
    return render_template('leads/create.html')

@bp.route('/leads/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'POST':
        lead.name = request.form['name']
        lead.email = request.form.get('email')
        lead.phone = request.form.get('phone')
        lead.company = request.form.get('company')
        lead.status = request.form.get('status')
        lead.source = request.form.get('source')
        lead.notes = request.form.get('notes')
        db.session.commit()
        flash('Lead updated successfully.', 'success')
        return redirect(url_for('leads.index'))
    return render_template('leads/edit.html', lead=lead)

@bp.route('/leads/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead deleted successfully.', 'success')
    return redirect(url_for('leads.index')) 