"""Handles the album collection webpages"""


from flask import Blueprint


bp = Blueprint('collection', __name__)


from albumcollections.collection import handlers
