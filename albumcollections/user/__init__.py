"""This module provides an interface to smoothly login/logout users
and save and display their data.

It is entirely tied to Spotify currently, through the `spotipy` oauth
library.
"""

from flask import Blueprint, url_for

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.models import User


bp = Blueprint('user', __name__)


"""JINJA VARIABLE INJECTION"""


@bp.app_context_processor
def inject_user_vars():
    return dict(
        is_user_logged_in=is_user_logged_in
    )


"""PUBLIC FUNCTIONS"""


def is_user_logged_in() -> bool:
    # Check if user is currently authenticated with spotify
    return spotify_user.is_authenticated()


def get_user_id() -> int:
    if is_user_logged_in():
        return User.query.filter_by(spotify_user_id=spotify_user.get_user_id()).first().id

    raise albumcollectionsError("Failed to get user id - user not logged in to spotify", url_for('main.index'))


from albumcollections.user import handlers
