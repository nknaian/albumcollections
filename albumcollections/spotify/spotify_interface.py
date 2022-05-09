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

from .item.spotify_music import SpotifyAlbum


class SpotifyInterface:
    """Class to interface with Spotify API through an
    instance of client credentials authenticated spotipy.
    """

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    '''PUBLIC FUNCTIONS'''

    def get_album_track_ids(self, spotify_album: SpotifyAlbum) -> List[str]:
        """Get the list of track ids that comprise the given spotify album"""
        track_items = self.sp.album(spotify_album.id)["tracks"]["items"]
        if len(track_items):
            return [track_item["id"] for track_item in track_items]
        else:
            return []
