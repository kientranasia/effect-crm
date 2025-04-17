from flask import render_template
from flask_login import login_required
from . import process_bp

@process_bp.route('/')
@login_required
def index():
    return render_template('process_management/index.html') 