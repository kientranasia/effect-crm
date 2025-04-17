from flask import render_template
from flask_login import login_required
from . import experience_bp

@experience_bp.route('/')
@login_required
def index():
    return render_template('customer_experience/index.html') 