from flask import Blueprint

from albumcollections import cache

bp = Blueprint('main', __name__)


from albumcollections.main import handlers
