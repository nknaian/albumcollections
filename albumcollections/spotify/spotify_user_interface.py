"""An interface to a user's spotify account.

There are module-level functions that handle authorization tasks.

There is a class that assumes the user has already been authenticated, which
provides API functionality.
"""

from typing import Dict, List, Tuple
import random

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from albumcollections.spotify.item.spotify_collection import SpotifyCollection

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_interface as spotify_iface

from albumcollections import spotipy_cache_handler

from .item.spotify_playlist import SpotifyPlaylist

'''CONSTANTS'''


SCOPE = [
    'playlist-modify-public',
    'playlist-modify-private',
    'playlist-read-private',
    'playlist-read-collaborative',
    'user-modify-playback-state',
    'user-read-playback-state'
]

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
    """Class to interface with Spotify API through a user's OAuth instance, in addition to
    client credentials interface.

    This allows operations to be done with user's data, such as viewing, modifying playlists etc.
    """

    def __init__(self):
        """Creates a spotify user interface if user is authorized. Otherwise raises
        an exception
        """
        super().__init__()

        auth_manager = _auth_manager()

        if auth_manager.validate_token(spotipy_cache_handler.get_cached_token()):
            self.sp_user = spotipy.Spotify(auth_manager=auth_manager)
            self.user_id = self.sp_user.me()["id"]
            self.display_name = self.sp_user.me()['display_name']
        else:
            raise Exception("Cannot create Spotify user interface - user not authenticated")

    '''PUBLIC FUNCTIONS'''

    def create_playlist(self, name: str, description: str = "") -> SpotifyPlaylist:
        """Create a playlist for the user, returning the spotify playlist object"""
        # Create the playlist
        self.sp_user.user_playlist_create(self.user_id, name, description=description)

        # Get the playlist that was just created
        playlist = SpotifyPlaylist(self.sp_user.current_user_playlists()['items'][0])

        # Make sure that this playlist is actually the one we just created (maybe it's
        # possible for it not to show up first in the list sometimes...wouldn't want to
        # set one of the user's actual playlists to be the playback playlist and get squashed...)
        # NOTE: This is not a foolproof way of verifying that we didn't get a different playlist
        # since names aren't unique, but I'm not aware of a better method
        assert playlist.name == name

        return playlist

    def remove_playlist(self, id: str):
        self.sp_user.user_playlist_unfollow(self.user_id, id)

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

    def add_items_to_playlist(self, playlist_id: str, items: List[str]):
        """ Add items in chunks to the playlist until all items have been added

        "items" is a list that can contain a combination of track ids and/or
        track/episode uris. Passing an episode id will result in a
        "Payload contains a non-existing ID" error from the API
        """
        MAX_CHUNK_SIZE = 100  # 100 is the max number of tracks that can be added at one time via spotify api request
        while len(items):
            if len(items) >= MAX_CHUNK_SIZE:
                chunk_size = MAX_CHUNK_SIZE
            else:
                chunk_size = len(items)

            # Add next chunk of tracks to playlist
            self.sp_user.playlist_add_items(
                playlist_id,
                items[:chunk_size]
            )

            # Chop off used chunk
            items = items[chunk_size:]

    def add_album_to_collection(self, collection_id, album_id):
        """Add an album to the collection with the given collection id

        Do this so that after the operation is done, there is exactly one
        complete version of the album in the collection, retaining order
        if an incomplete version was there previously.
        """
        # Get the collection for the playlist
        collection = self.get_collection(collection_id)

        # Get list of track ids for tracks in the album
        album_track_ids = self.get_album_track_ids(album_id)

        # If album is already in the collection and is complete, do nothing
        # If album is already in the collection and incomplete, then remove occurences
        # of the incomplete album and then add the full album at the index of the
        # incomplete album in the playlist (index of first track)
        for album in collection.albums:
            if album.id == album_id:
                if not album.complete:
                    self.sp_user.playlist_remove_all_occurrences_of_items(collection_id, album_track_ids)
                    # NOTE: If an album has over 100 tracks, this will return an error
                    self.sp_user.playlist_add_items(collection_id, album_track_ids, album.playlist_index)
                return

        # Add tracks of new album to the playllst
        self.add_items_to_playlist(collection_id, album_track_ids)

    def remove_album_from_playlist(self, playlist_id, album_id):
        # Get list of track ids for tracks in the album
        album_track_ids = self.get_album_track_ids(album_id)

        # Remove all instances of these tracks from the playlist
        self.sp_user.playlist_remove_all_occurrences_of_items(playlist_id, album_track_ids)

    def reorder_collection(self, playlist_id, moved_album_id, next_album_id):
        """
        Move all tracks in the "moved album" to the position that the
        "next album"'s first track is currently in.
        """
        # Get the collection for the playlist
        collection = self.get_collection(playlist_id)

        # Set indices and album length information, based on saved collection album info
        curr_index = None
        dest_index = collection.total_tracks if next_album_id is None else None
        num_tracks = None
        for album in collection.albums:
            if album.id == moved_album_id:
                assert album.complete
                curr_index = album.playlist_index
                num_tracks = album.total_tracks

            if album.id == next_album_id:
                dest_index = album.playlist_index

            # Break out of the loop once we have both indices
            if curr_index is not None and dest_index is not None:
                break

        # Execute the reorder command
        self.sp_user.playlist_reorder_items(
            playlist_id,
            curr_index,
            dest_index,
            range_length=num_tracks
        )

    def shuffle_collection(
        self,
        spotify_collection: SpotifyCollection
    ):
        """Shuffles the spotify playlist underlying the given collection
        by rearranging its albums.

        Assumes that there are at least two items in the playlist (with one it's pointless
        obviously but also the random.choices() function would fail)
        """
        # Create a list of tracks that will comprise the shuffled collection
        shuffled_collection_tracks = []

        # Shuffle the albums in the collection (local copy, this doesn't change the spotify playlist)
        random.shuffle(spotify_collection.albums)

        for album in spotify_collection.albums:
            shuffled_collection_tracks.extend(album.track_ids)

        # Replace the previous playlist with the new order
        # NOTE: This means that any non-track items in the playlist (ex: podcasts) will be removed
        self.sp_user.user_playlist_replace_tracks(self.user_id, spotify_collection.id, [])
        self.add_items_to_playlist(spotify_collection.id, shuffled_collection_tracks)

    def fill_collection_missing_tracks(self, source_collection: SpotifyCollection, destination_playlist_id: str):
        """Replace the destination playlist with tracks that include the full list of tracks for
        every album in the source collection. The previously incomplete album tracks are inserted
        where the first track was encountered for that album in the source collection.

        TODO: This is a good candidate for trying out with unit testing first - maybe
        """
        # Create a dictionary of album id to album for the incomplete albums in the collection
        incomplete_albums = {album.id: album for album in source_collection.albums if not album.complete}

        # Make API requests to record the full list of track ids for each
        # of the currently incomplete albums
        for album in incomplete_albums.values():
            album.track_ids = self.get_album_track_ids(album.id)

        # Build a list of items to replace the current playlist.
        # Iterate through the current playlist. When the first track from an
        # incomplete albums is encountered, add it's newfound full track id list
        # in-place to the playlist. When a track that is from a complete album
        # or is not included in the collection at all (ex: podcase episodes) is
        # encountered, simply add it's uri to the list to retain its presence in
        # the playlist.
        new_playlist_items = []
        for playlist_track in self.get_playlist_tracks(source_collection.id):
            if playlist_track.album.id in incomplete_albums:
                incomplete_album = incomplete_albums[playlist_track.album.id]
                if not incomplete_album.complete:
                    new_playlist_items.extend(incomplete_album.track_ids)
                    incomplete_album.complete = True
                else:
                    # Ignore subsequent tracks from this incomplete album
                    pass
            else:
                new_playlist_items.append(playlist_track.uri)

        # Clear the playlist of it's current track list
        self.sp_user.user_playlist_replace_tracks(self.user_id, destination_playlist_id, [])

        # Add the new list of items to the playlist
        self.add_items_to_playlist(destination_playlist_id, new_playlist_items)

    '''SPOTIPY WRAPPER FUNCTIONS'''

    def _playlist(self, playlist_id: str) -> Dict:
        """Call spotipy playlist method with User OAuth interface

        This overrides the parent method
        """
        return self.sp_user.playlist(playlist_id)

    def _playlist_tracks(self, playlist_id, track_offset: int, track_limit: int) -> Dict:
        """Call spotipy playlist_tracks method with User OAuth interface

        This overrides the parent method
        """
        return self.sp_user.playlist_tracks(playlist_id, limit=track_limit, offset=track_offset)


"""HELPER FUNCTIONS"""


def _track_uri_from_id(id: str) -> str:
    return f"spotify:track:{id}"
