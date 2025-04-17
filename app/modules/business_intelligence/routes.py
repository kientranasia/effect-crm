from flask import render_template
from flask_login import login_required
from . import bi_bp

@bi_bp.route('/')
@login_required
def index():
    return render_template('business_intelligence/index.html') 