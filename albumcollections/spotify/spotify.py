"""Spotify interface class that uses the spotipy client
credentials authentication method. This class can be used
to interface with spotify for use cases that don't require
access to individual user accounts. So, things like searching
for music, or getting information about music based on a
spotify link.
"""

from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .item.spotify_music import SpotifyAlbum, SpotifyTrack
from .item.spotify_playlist import SpotifyPlaylist


class Spotify:
    """Class to interface with Spotify API through an
    instance of client credentials authenticated spotipy.
    """

    """Public Functions"""

    def init_sp(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    def get_playlist_from_link(self, link):
        """Use spotify playlist link to get `SpotifyPlaylist` object"""
        spotify_playlist = self.sp.playlist(link)
        return SpotifyPlaylist(spotify_playlist)

    def get_playlist_tracks(self, id) -> List[SpotifyTrack]:
        tracks = []

        offset = 0
        while True:
            next_tracks = \
                [SpotifyTrack(track_item["track"])
                 for track_item in self.sp.playlist_tracks(id, limit=100, offset=offset)["items"]]

            if len(next_tracks):
                tracks.extend(next_tracks)
                offset += len(next_tracks)
            else:
                break

        return tracks

    def get_playlist_albums(self, id) -> List[SpotifyAlbum]:
        return list(set([track.album_item for track in self.get_playlist_tracks(id)]))
