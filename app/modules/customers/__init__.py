from flask import Blueprint

bp = Blueprint('customers', __name__)

from . import routes 