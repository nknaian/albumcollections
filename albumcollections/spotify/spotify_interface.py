"""Spotify interface class that uses the spotipy client
credentials authentication method. This class can be used
to interface with spotify for use cases that don't require
access to individual user accounts. So, things like searching
for music, or getting information about music based on a
spotify link.
"""

from typing import Dict, List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

from albumcollections.spotify.item.spotify_collection import SpotifyCollection
from albumcollections.spotify import collection_albums
from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist

from .item.spotify_music import SpotifyAlbum, SpotifyTrack


class SpotifyInterface:
    """Class to interface with Spotify API through an
    instance of client credentials authenticated spotipy.
    """

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    '''PUBLIC FUNCTIONS'''

    def playlist_exists(self, id) -> bool:
        """Attempts to get the playlist. If it cannot be retrieved then return
        False. Otherwise return True
        """
        try:
            self._playlist(id)
            return True
        except SpotifyException as e:
            # NOTE: There are more reasons besides the playlist not existing that a 404
            # can be returned but I'm not sure of any way to definitely tell that it doesn't
            # exist from the code or any other information returned
            if e.http_status != 404:
                raise e

        return False

    def get_playlist(self, id) -> SpotifyPlaylist:
        """Gets the spotify playlist object from the id."""
        return SpotifyPlaylist(self._playlist(id))

    def get_album_track_ids(self, album_id) -> List[str]:
        """Get the list of track ids that comprise the given spotify album"""
        return [spotify_track["id"] for spotify_track in self.sp.album_tracks(album_id)["items"]]

    def get_playlist_tracks(self, id) -> List[SpotifyTrack]:
        """Get all tracks in the given playlist, retaining track order"""
        tracks = []

        offset = 0
        while True:
            # Get next tracks in playlist.
            next_tracks = self._playlist_spotify_tracks(id, offset)

            if len(next_tracks):
                tracks.extend(next_tracks)
                offset += len(next_tracks)
            else:
                break

        return tracks

    def get_collection(self, playlist_id) -> SpotifyCollection:
        """Get `SpotifyCollection` item based on a database collection entry

        The `SpotifyCollection` class makes use of caching
        to store albums so they don't always have to be loaded again.
        """
        playlist = self._playlist(playlist_id)
        spotify_collection = SpotifyCollection(playlist)

        # Load the albums in the spotify_collection if they're not already
        # available
        if spotify_collection.albums is None:
            # Make iterator of tracks in playlist
            playlist_tracks_iter = iter(self.get_playlist_tracks(spotify_collection.id))
            # Set the list of albums in the collection based on the playlist tracks
            spotify_collection.albums = collection_albums.get(playlist_tracks_iter)

        return spotify_collection

    '''SPOTIPY WRAPPER FUNCTIONS'''

    def _playlist(self, playlist_id: str) -> Dict:
        """Call spotipy playlist method with client credentials interface"""
        return self.sp.playlist(playlist_id)

    def _playlist_tracks(self, playlist_id, track_offset: int, track_limit: int) -> Dict:
        """Call spotipy playlist_tracks method with client credentials interface"""
        return self.sp.playlist_tracks(playlist_id, limit=track_limit, offset=track_offset)

    '''PRIVATE FUNCTIONS'''

    def _playlist_spotify_tracks(
        self,
        playlist_id: str,
        track_offset: int,
        track_limit: int = 100
    ) -> List[SpotifyTrack]:
        """Get tracks from the playlist as `SpotifyTrack` objects

        Ignore anything that's not a track (if podcast/s are included
        in a playlist, the podcast items will turn up in the search,
        as well as what looks like a 'user object'?)
        """
        return [
            SpotifyTrack(track_item["track"])
            for track_item in self._playlist_tracks(playlist_id, track_offset, track_limit)["items"]
        ]
