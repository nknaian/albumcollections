"""An interface to a user's spotify account.

There are module-level functions that handle authorization tasks.

There is a class that assumes the user has already been authenticated, which
provides API functionality.
"""

from typing import Dict, List, Tuple
import random
import copy

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_interface as spotify_iface

from albumcollections import spotipy_cache_handler

from .item.spotify_playlist import SpotifyPlaylist


'''CONSTANTS'''


SCOPE = 'playlist-modify-public,user-modify-playback-state,user-read-playback-state'


'''PUBLIC AUTH FUNCTIONS'''


def auth_user(code):
    """Give user an access token to authenticate them"""
    _auth_manager().get_access_token(code)


def unauth_user():
    """Remove the cache token for this user. This doesn't 'unauthenticate'
    the user, but it will force an `SpotifyUserAuthFailure` the next time
    that `_get_sp_instance` is called.
    """
    spotipy_cache_handler.remove_cached_token()


def is_auth():
    """Check whether thte user is authenticated with a spotify"""
    if _auth_manager().validate_token(spotipy_cache_handler.get_cached_token()):
        return True
    else:
        return False


def get_auth_url():
    return _auth_manager(show_dialog=True).get_authorize_url()


'''PRIVATE AUTH FUNCTIONS'''


def _auth_manager(show_dialog=False):
    return SpotifyOAuth(scope=SCOPE, cache_handler=spotipy_cache_handler, show_dialog=show_dialog)


'''USER SPOTIFY INTERFACE CLASS'''


class SpotifyUserInterface(spotify_iface.SpotifyInterface):
    """Creates a spotify user interface if user is authorized. Otherwise raises
    an exception
    """
    def __init__(self):
        super().__init__()

        auth_manager = _auth_manager()

        if auth_manager.validate_token(spotipy_cache_handler.get_cached_token()):
            self.sp_user = spotipy.Spotify(auth_manager=auth_manager)
            self.user_id = self.sp_user.me()["id"]
            self.display_name = self.sp_user.me()['display_name']
        else:
            raise Exception("Cannot create Spotify user interface - user not authenticated")

    '''PUBLIC FUNCTIONS'''

    def get_playlists(self) -> Tuple[List[SpotifyPlaylist], List[str]]:
        """Get the user's spotify playlists.

        This gets playlists according to authorized SCOPE. So as of this writing,
        that means that it only gets public playlists.

        This function should not be able to raise an exception because it is necessary
        to have some valid (or empty) data for the application to run. It will attempt
        to load as many playlists as possible, handling exceptions for each case.
        """
        playlists = []
        errors = []

        try:
            playlist_infos = self.sp_user.current_user_playlists()

            while playlist_infos:
                for playlist in playlist_infos['items']:
                    try:
                        playlists.append(SpotifyPlaylist(playlist))
                    except Exception as e:
                        errors.append(f"Failed to create SpotifyPlaylist for playlist dictionary {playlist}: {e}")
                if playlist_infos['next']:
                    playlist_infos = self.sp_user.next(playlist_infos)
                else:
                    playlist_infos = None
        except Exception as e:
            errors.append(str(e))

        return (playlists, errors)

    def get_devices(self) -> Dict[str, str]:
        """Get dictionary of available spotify devices"""
        devices = self.sp_user.devices()['devices']

        return {device["name"]: device["id"] for device in devices}

    def reorder_collection(self, playlist_id, moved_album_id, next_album_id):
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
        # Get the playlist tracks
        playlist_tracks = self.get_playlist_tracks(playlist_id)

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
        self.sp_user.playlist_reorder_items(
            playlist_id,
            moved_album_curr_index,
            moved_album_dest_index,
            range_length=moved_album_num_tracks
        )

    def play_collection(self, playlist_id, start_album_id, shuffle_albums: bool, device_id=None):
        """This function attempts to mimic the ability to play songs
        within the context of a playlist.

        Playback will start from the first track of `start_album_id`

        If shuffle_albums is set to true then the list order will be randomized.

        A playlist is created just for playback and then immediately torn down
        after playback starts.

        NOTE: start_album_id must be in the collection or undefined behavior will occur
        """
        # Turn off user's shuffle (so the albums are actually in order!)
        # NOTE: On some devices this may fail (ex: New web player tab before it has played music)
        # As seen thusfar, when this command fails, the playback would have failed anyways, except silently.
        # So this at least gives some indication that something went wrong (although it would be nice
        # if there was a more clear explanation for the user...I'm just not really the underlying reasoning
        # so I can't accurately add an error message at this time.)
        self.sp_user.shuffle(False, device_id)

        # Get the collection
        collection = self.get_collection(playlist_id)

        # Get a copy of the collection albums
        collection_albums = copy.deepcopy(collection.albums)

        # Shuffle the albums if specified
        if shuffle_albums:
            random.shuffle(collection_albums)

        # Create temporary playlist to hold playback tracks
        playback_playlist = self._create_playlist(f"Album Collection: {collection.name}")

        try:
            # If there is a 'start album' then add tracks from the start album to temporary playlist
            if start_album_id is not None:
                self._add_tracks_to_playlist(
                    playback_playlist.id,
                    next(album.track_ids for album in collection_albums if album.id == start_album_id))

            # Otherwise just add tracks from the first album in the collection
            else:
                self._add_tracks_to_playlist(
                    playback_playlist.id,
                    collection_albums[0].track_ids)

            # Begin playback of the playlist (only one album so far, but that's fine)
            self.sp_user.start_playback(device_id=device_id, context_uri=playback_playlist.uri)

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
            self._add_tracks_to_playlist(playback_playlist.id, playback_track_ids[0:start_album_offset])

            # Put start album in it's correct position at the end of the playlist as it's been built thusfar
            self.sp_user.playlist_reorder_items(
                playback_playlist.id,
                0,
                start_album_num_tracks + start_album_offset,
                range_length=start_album_num_tracks)

            # Add remaining tracks to the temporary playlist
            self._add_tracks_to_playlist(
                playback_playlist.id,
                playback_track_ids[start_album_offset+start_album_num_tracks:]
            )

        except Exception as e:
            raise e
        finally:
            # Remove the temporary playlist
            self.sp_user.current_user_unfollow_playlist(playback_playlist.id)

    """PRIVATE FUNCTIONS"""

    def _add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]):
        # Add tracks in chunks to the playlist
        MAX_CHUNK_SIZE = 100  # 100 is the max number of tracks that can be added at one time via spotify api request
        while len(track_ids):
            if len(track_ids) >= MAX_CHUNK_SIZE:
                chunk_size = MAX_CHUNK_SIZE
            else:
                chunk_size = len(track_ids)

            # Add next chunk of tracks to playlist
            self.sp_user.user_playlist_add_tracks(
                self.user_id,
                playlist_id,
                track_ids[:chunk_size]
            )

            # Chop off used chunk
            track_ids = track_ids[chunk_size:]

    def _create_playlist(self, name: str) -> SpotifyPlaylist:
        """Create a playlist with the given name

        It will return the created playlist object
        """
        # Create the playlist with the given name, for the current user.
        self.sp_user.user_playlist_create(self.user_id, name)

        # Make a playlist object for the playlist that was just created
        return SpotifyPlaylist(self.sp_user.current_user_playlists()['items'][0])
