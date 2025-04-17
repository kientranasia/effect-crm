from flask import Blueprint

experience_bp = Blueprint('customer_experience', __name__, url_prefix='/experience')

from . import routes 