from flask import Blueprint

bp = Blueprint('organizations', __name__)

from app.modules.organizations import routes 