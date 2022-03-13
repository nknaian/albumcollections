from flask import Blueprint

bp = Blueprint('pwa', __name__)


from albumcollections.pwa import handlers
