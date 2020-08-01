from flask import Blueprint

bp = Blueprint("closet", __name__)

from project.closet import routes
