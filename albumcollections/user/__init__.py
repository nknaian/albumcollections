"""This module provides an interface to smoothly login/logout users
and save and display their data.

It is entirely tied to Spotify currently, through the `spotipy` oauth
library.
"""
from typing import Union

from flask import Blueprint

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.models import AcUser

from albumcollections import db

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


def get_user() -> AcUser:
    """Get the user's database entry.

    This function must be called within a try block to catch
    exceptions
    """
    if is_user_logged_in():
        return AcUser.query.filter_by(spotify_user_id=spotify_user_iface.SpotifyUserInterface().user_id).first()

    raise Exception("Failed to get user id - user not logged in to spotify")


def get_user_id() -> int:
    """Get the user's database id.

    This function must be called within a try block to catch
    exceptions
    """
    return get_user().id


def get_user_playback_playlist_id() -> Union[str, None]:
    """Get the user's playback playlist id

    This function must be called within a try block to catch
    exceptions
    """
    return get_user().playback_playlist_id


def set_user_playback_playlist_id(id: str):
    """Set the user's playback playlist id in their db entry

    This function must be called within a try block to catch
    exceptions
    """
    user = get_user()
    user.playback_playlist_id = id
    db.session.commit()


from albumcollections.user import handlers
