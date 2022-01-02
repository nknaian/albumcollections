from flask import Blueprint

bp = Blueprint('errors', __name__)

from musicorg.errors import handlers
