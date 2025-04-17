from flask import Blueprint

bp = Blueprint('interactions', __name__)

from . import routes 