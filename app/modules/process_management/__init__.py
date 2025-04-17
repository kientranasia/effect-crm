from flask import Blueprint

process_bp = Blueprint('process_management', __name__, url_prefix='/process')

from . import routes 