from typing import Union

from musicorg.spotify import spotify_user
from musicorg.database.helpers import lookup_user_in_db, add_user_to_db


"""PUBLIC FUNCTIONS"""


def login_or_register_user() -> None:
    # Get current user's spotify user id
    spotify_user_id = spotify_user.get_user_id()

    # Look up user by spotify user id
    user = lookup_user_in_db(spotify_user_id)

    # Add new user to database if they are not found
    if user is None:
        add_user_to_db(spotify_user_id, spotify_user.get_user_display_name())


def is_user_logged_in() -> bool:
    # Check if user is currently authenticated with spotify
    if spotify_user.is_authenticated():
        # Look up user by spotify user id
        user = lookup_user_in_db(spotify_user.get_user_id())

        # If user is in the database, return True
        if user is not None:
            return True

    return False


def current_user_id() -> Union[int, None]:
    if is_user_logged_in():
        return lookup_user_in_db(spotify_user.get_user_id()).id

    return None


def get_user_display_name() -> str:
    if is_user_logged_in():
        return lookup_user_in_db(spotify_user.get_user_id()).display_name

    return None
