"""This module provides an interface to smoothly login/logout users
and save and display their data.

It is entirely tied to Spotify currently, through the `spotipy` oauth
library.

It uses the flask session to store and retrieve information about
what the user was doing before they were sent away for spotify
authentication
The following keys names are used in the 'session' object to enable this:
- "user_referrer_url"
- "user_retry_func"
"""

from flask import Blueprint

from .helpers import is_user_logged_in, get_user_display_name


bp = Blueprint('user', __name__)


@bp.app_context_processor
def inject_user_vars():
    return dict(
        is_user_logged_in=is_user_logged_in,
        get_user_display_name=get_user_display_name,
    )


from musicorg.user import handlers
