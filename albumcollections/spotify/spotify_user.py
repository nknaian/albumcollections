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
import random
import copy

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from albumcollections.spotify.spotify import Spotify

from albumcollections import spoipy_cache_handler

from .item.spotify_music import SpotifyTrack
from .item.spotify_playlist import SpotifyPlaylist
from .item.spotify_collection import SpotifyCollection


'''CONSTANTS'''


SCOPE = 'playlist-modify-public,user-modify-playback-state,user-read-playback-state'


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


def get_user_collections() -> List[SpotifyCollection]:
    sp = _get_sp_instance()

    playlist_infos = sp.current_user_playlists()

    collections = []
    while playlist_infos:
        for playlist in playlist_infos['items']:
            # Make a collection from the playlist dict
            collection = Spotify().get_collection_from_playlist_dict(playlist)

            # If the collection has albums, add it
            if collection.num_albums:
                collections.append(collection)
        if playlist_infos['next']:
            playlist_infos = sp.next(playlist_infos)
        else:
            playlist_infos = None

    return collections


def create_playlist(name: str) -> SpotifyPlaylist:
    """Create a playlist with the given name

    It will return the created playlist object
    """
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get the current user's id
    user_id = sp.current_user()["id"]

    # Create the playlist with the given name, for the current user.
    sp.user_playlist_create(user_id, name)

    # Make a playlist object for the playlist that was just created
    return SpotifyPlaylist(sp.current_user_playlists()['items'][0])


def add_tracks_to_playlist(playlist_id: str, track_ids: List[str]):
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get the current user's id
    user_id = sp.current_user()["id"]

    # Add tracks in chunks to the playlist
    MAX_CHUNK_SIZE = 100  # 100 is the max number of tracks that can be added at one time via spotify api request
    while len(track_ids):
        if len(track_ids) >= MAX_CHUNK_SIZE:
            chunk_size = MAX_CHUNK_SIZE
        else:
            chunk_size = len(track_ids)

        # Add next chunk of tracks to playlist
        sp.user_playlist_add_tracks(user_id,
                                    playlist_id,
                                    track_ids[:chunk_size])

        # Chop off used chunk
        track_ids = track_ids[chunk_size:]


def remove_album_from_playlist(playlist_id, album_id):
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get list of track ids for tracks in the album
    album_track_ids = [spotify_track["id"] for spotify_track in sp.album_tracks(album_id)["items"]]

    # Remove all instances of these tracks from the playlist
    sp.playlist_remove_all_occurrences_of_items(playlist_id, album_track_ids)


def reorder_collection(playlist_id, moved_album_id, next_album_id):
    """
    Move all tracks in the "moved album" to the position that the
    "next album"'s first track is currently in.

    NOTE: This relies on the collection being constructed as in
    the rules in `_get_collection_albums`

    TODO: Try to utilize cached collection Spotify album tracks to
    reduce spotify api requests. To do this, I think the indices of
    of the albums in the playlist would have to be cached as well, so
    as to account for non-album tracks.
    """
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get the playlist tracks
    playlist_tracks = Spotify().get_playlist_tracks(playlist_id)

    # Iterate through playlist to find current and destination indices for the
    # moving album and num tracks in the album
    moved_album_curr_index = None
    moved_album_dest_index = len(playlist_tracks) if next_album_id is None else None
    moved_album_num_tracks = None
    for index, track in enumerate(playlist_tracks):
        # Look for the first track of the album to be moved
        if moved_album_id == track.album.id and moved_album_curr_index is None:
            # Set the index of the tracks to be moved
            moved_album_curr_index = index

            # Set the number of tracks in the album to be moved
            moved_album_num_tracks = track.album.total_tracks

        # Look for current index of the album that will now be directly after
        # the moved album
        if next_album_id is not None and \
                next_album_id == track.album.id and \
                moved_album_dest_index is None:
            moved_album_dest_index = index

        # Break out of the loop once we have both indices
        if moved_album_curr_index is not None and moved_album_dest_index is not None:
            break

    # Execute the reorder command
    sp.playlist_reorder_items(playlist_id,
                              moved_album_curr_index,
                              moved_album_dest_index,
                              range_length=moved_album_num_tracks)


def play_collection(playlist_id, start_album_id, shuffle_albums: bool, device_id=None):
    """This function attempts to mimic the ability to play songs
    within the context of a playlist.

    Playback will start from the first track of `start_album_id`

    If shuffle_albums is set to true then the list order will be randomized.

    A playlist is created just for playback and then immediately torn down
    after playback starts.

    NOTE: start_album_id must be in the collection or undefined behavior will occur
    """
    # Get the spotify user account instance
    sp = _get_sp_instance()

    # Get a client credentials spotify interface
    sp_cc_iface = Spotify()

    # Turn off user's shuffle (so the albums are actually in order!)
    # NOTE: On some devices this may fail (ex: New web player tab before it has played music)
    # As seen thusfar, when this command fails, the playback would have failed anyways, except silently.
    # So this at least gives some indication that something went wrong (although it would be nice
    # if there was a more clear explanation for the user...I'm just not really the underlying reasoning
    # so I can't accurately add an error message at this time.)
    sp.shuffle(False, device_id)

    # Get the collection (making sure to reload albums if necessary!)
    collection = sp_cc_iface.get_collection_from_playlist_id(playlist_id, reload_albums=True)

    # Get a copy of the collection albums
    collection_albums = copy.deepcopy(collection.albums)

    # Shuffle the albums if specified
    if shuffle_albums:
        random.shuffle(collection_albums)

    # Create temporary playlist to hold playback tracks
    playback_playlist = create_playlist(f"Album Collection: {collection.name}")

    try:
        # If there is a 'start album' then add tracks from the start album to temporary playlist
        if start_album_id is not None:
            add_tracks_to_playlist(
                playback_playlist.id,
                next(album.track_ids for album in collection_albums if album.id == start_album_id))

        # Otherwise just add tracks from the first album in the collection
        else:
            add_tracks_to_playlist(
                playback_playlist.id,
                collection_albums[0].track_ids)

        # Begin playback of the playlist (only one album so far, but that's fine)
        sp.start_playback(device_id=device_id, context_uri=playback_playlist.uri)

        # Get list of tracks from list of albums and mark which track should be played first
        playback_track_ids = []
        start_album_offset = None
        start_album_num_tracks = None
        for album in collection_albums:
            # Record start album information
            if start_album_offset is None and \
                    (start_album_id is None or album.id == start_album_id):
                start_album_offset = len(playback_track_ids)
                start_album_num_tracks = album.total_tracks

            # Add tracks from album to list
            playback_track_ids.extend(album.track_ids)

        # Add tracks from before the start album to the temporary playlist
        add_tracks_to_playlist(playback_playlist.id, playback_track_ids[0:start_album_offset])

        # Put start album in it's correct position at the end of the playlist as it's been built thusfar
        sp.playlist_reorder_items(
            playback_playlist.id,
            0,
            start_album_num_tracks + start_album_offset,
            range_length=start_album_num_tracks)

        # Add remaining tracks to the temporary playlist
        add_tracks_to_playlist(playback_playlist.id, playback_track_ids[start_album_offset+start_album_num_tracks:])

    except Exception as e:
        raise e
    finally:
        # Remove the temporary playlist
        sp.current_user_unfollow_playlist(playback_playlist.id)


def get_devices():
    """Get dictionary of available spotify devices"""
    # Get the spotify user account instance
    sp = _get_sp_instance()

    devices = sp.devices()['devices']

    return {device["name"]: device["id"] for device in devices}


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
