"""This module is used for unit testing purposes to mock
external urls.

The blueprint should only be registered when testing.
"""

from flask import Blueprint

bp = Blueprint('test', __name__)

from albumcollections.test import handlers
