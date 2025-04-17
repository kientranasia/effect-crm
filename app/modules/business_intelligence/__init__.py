from flask import Blueprint

bi_bp = Blueprint('business_intelligence', __name__, url_prefix='/bi')

from . import routes 