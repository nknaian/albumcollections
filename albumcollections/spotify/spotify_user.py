"""A collection of functions to interface with a user's spotify
account, using the spotipy authorization code flow.

If a function is called that requires user authentication, then
the 'SpotifyUserAuthFailure' exception shall be raised, containing
the authorization url that should be visited to log the user in
to spotify and authorize the albumcollections app. It is the caller's
responsibility to catch this exception and redirect to the authorization
url and then direct back towards what the user was trying to do.
"""

from typing import List

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from albumcollections import spoipy_cache_handler

from .item.spotify_music import SpotifyTrack
from .item.spotify_playlist import SpotifyPlaylist


'''CONSTANTS'''


SCOPE = 'playlist-modify-public'


'''EXCEPTIONS'''


class SpotifyUserAuthFailure(Exception):
    def __init__(self, auth_url) -> None:
        self.__auth_url = auth_url

    @property
    def auth_url(self):
        return self.__auth_url

    @auth_url.setter
    def auth_url(self, auth_url):
        self.__auth_url = auth_url


'''PUBLIC AUTH FUNCTIONS'''


def get_auth_url(show_dialog=False):
    """Get url for user to visit to sign in to spotify
    and give permission to albumcollections. Permission is only
    asked for on first authentication from a user by default. To
    show the dialog box (which also shows the "not you" button),
    then set `show_dialog` to True.
    """
    return _get_auth_manager(show_dialog=show_dialog).get_authorize_url()


def auth_new_user(code):
    """Give user an access token to authenticate them"""
    _get_auth_manager().get_access_token(code)


def logout():
    """Remove the cache token for this user. This doesn't 'unauthenticate'
    the user, but it will force an `SpotifyUserAuthFailure` the next time
    that `_get_sp_instance` is called.
    """
    # Remove cache code for this user
    spoipy_cache_handler.remove_cached_token()


'''PUBLIC FUNCTIONS'''


def is_authenticated():
    """Check whether thte user is authenticated with a spotify"""
    try:
        _get_sp_instance()
    except SpotifyUserAuthFailure:
        return False

    return True


def get_user_id():
    return _get_sp_instance().me()["id"]


def get_current_track():
    """Return information about the track the user is currently playing
    """
    track_info = _get_sp_instance().current_user_playing_track()
    if track_info is not None:
        return SpotifyTrack(track_info['item'])
    return "No track currently playing."


def get_user_display_name():
    return _get_sp_instance().me()['display_name']


def get_user_playlists() -> List[SpotifyPlaylist]:
    sp = _get_sp_instance()

    playlist_infos = sp.current_user_playlists()

    playlists = []
    while playlist_infos:
        for playlist in playlist_infos['items']:
            playlists.append(SpotifyPlaylist(playlist))
        if playlist_infos['next']:
            playlist_infos = sp.next(playlist_infos)
        else:
            playlist_infos = None

    return playlists


def create_playlist(name: str, tracks: List[SpotifyTrack]) -> SpotifyPlaylist:
    """Create a playlist of the passed in tracks with the given name

    It will return the spotify link of the created playlist.
    """
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get the current user's id
    user_id = sp.current_user()["id"]

    # Create the playlist with the given name, for the current user.
    sp.user_playlist_create(user_id, name)

    # Make a playlist object for the playlist that was just created
    new_playlist = SpotifyPlaylist(sp.current_user_playlists()['items'][0])

    # Add the given tracks to the new playlist
    sp.user_playlist_add_tracks(user_id,
                                new_playlist.id,
                                [track.id for track in tracks])

    # Return the new playlist
    return new_playlist


def remove_album_from_playlist(playlist_id, album_id):
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get list of track ids for tracks in the album
    album_track_ids = [spotify_track["id"] for spotify_track in sp.album_tracks(album_id)["items"]]

    # Remove all instances of these tracks from the playlist
    sp.playlist_remove_all_occurrences_of_items(playlist_id, album_track_ids)


'''PRIVATE FUNCTIONS'''


def _get_sp_instance():
    """Create an spotify auth_manager and check whether the current user has
    a token (has been authorized already). If the user has a token, then they
    are authenticated -- return their spotipy instance. If the user does not have
    a token, then they are not authenticated -- raise an exception
    """
    auth_manager = _get_auth_manager()

    if auth_manager.validate_token(spoipy_cache_handler.get_cached_token()):
        return spotipy.Spotify(auth_manager=auth_manager)
    else:
        raise SpotifyUserAuthFailure(get_auth_url(show_dialog=True))


def _get_auth_manager(show_dialog=False):
    return SpotifyOAuth(scope=SCOPE,
                        cache_handler=spoipy_cache_handler,
                        show_dialog=show_dialog)
