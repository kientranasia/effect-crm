from flask import render_template
from flask_login import login_required
from . import analytics_bp

@analytics_bp.route('/')
@login_required
def index():
    return render_template('analytics/index.html') 