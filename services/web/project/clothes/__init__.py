from flask import Blueprint

bp = Blueprint("clothes", __name__)

from project.clothes import routes
