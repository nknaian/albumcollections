"""This module provides an interface to smoothly login/logout users
and save and display their data.

It is entirely tied to Spotify currently, through the `spotipy` oauth
library.
"""

from flask import Blueprint, url_for

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

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
    return spotify_user_iface.is_auth()


def get_user_id() -> int:
    """Get the user's database id.

    This function must be called within a try block to catch
    exceptions
    """
    if is_user_logged_in():
        return User.query.filter_by(spotify_user_id=spotify_user_iface.SpotifyUserInterface().user_id).first().id

    raise Exception("Failed to get user id - user not logged in to spotify")


from albumcollections.user import handlers
