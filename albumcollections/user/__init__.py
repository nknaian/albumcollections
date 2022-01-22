"""This module provides an interface to smoothly login/logout users
and save and display their data.

It is entirely tied to Spotify currently, through the `spotipy` oauth
library.
"""

from flask import Blueprint

from albumcollections import spotify_iface

from .helpers import is_user_logged_in, get_user_display_name


bp = Blueprint('user', __name__)


@bp.app_context_processor
def inject_user_vars():
    return dict(
        is_user_logged_in=is_user_logged_in,
        get_user_display_name=get_user_display_name
    )


from albumcollections.user import handlers
