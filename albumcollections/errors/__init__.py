from flask import Blueprint

bp = Blueprint('errors', __name__)

from albumcollections.errors import handlers
