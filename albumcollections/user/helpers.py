from typing import Union, List

from albumcollections.spotify import spotify_user
from albumcollections.spotify.item.spotify_music import SpotifyAlbum

from albumcollections import spotify_iface

"""PUBLIC FUNCTIONS"""


def is_user_logged_in() -> bool:
    # Check if user is currently authenticated with spotify
    return spotify_user.is_authenticated()


def get_user_display_name() -> str:
    if is_user_logged_in():
        return spotify_user.get_user_display_name()

    return None
