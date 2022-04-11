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

from .item.spotify_music import SpotifyAlbum, SpotifyTrack, AlbumType
from .item.spotify_playlist import SpotifyPlaylist
from .item.spotify_collection import SpotifyCollection


class Spotify:
    """Class to interface with Spotify API through an
    instance of client credentials authenticated spotipy.
    """

    """Public Functions"""

    def __init__(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    def get_playlist_from_link(self, link):
        """Use spotify playlist link to get `SpotifyPlaylist` object"""
        spotify_playlist = self.sp.playlist(link)
        return SpotifyPlaylist(spotify_playlist)

    def get_collection(self, playlist_id, load_albums=False):
        """Get `SpotifyCollection` item based on a database collection entry

        The `SpotifyCollection` class makes use of caching
        to store albums so they don't always have to be loaded again.
        """
        spotify_collection = SpotifyCollection(self.sp.playlist(playlist_id))

        # Load the albums in the spotify_collection
        if load_albums and spotify_collection.albums is None:
            spotify_collection.albums = self._get_collection_albums(spotify_collection.id)

        return spotify_collection

    def get_playlist_tracks(self, id) -> List[SpotifyTrack]:
        """Get all tracks in the given playlist, retaining track order"""
        tracks = []

        offset = 0
        while True:
            # Get next 100 (or remainder) tracks in playlist.
            # Ignore anything that's not a track (if podcast/s are included
            # in a playlist, the podcast items will turn up in the search,
            # as well as what looks like a 'user object'?)
            next_tracks = [
                    SpotifyTrack(track_item["track"])
                    for track_item in self.sp.playlist_tracks(id, limit=100, offset=offset)["items"]
                    if track_item["track"] is not None
                ]

            if len(next_tracks):
                tracks.extend(next_tracks)
                offset += len(next_tracks)
            else:
                break

        return tracks

    def get_album_track_ids(self, spotify_album: SpotifyAlbum) -> List[str]:
        """Get the list of track ids that comprise the given spotify album"""
        track_items = self.sp.album(spotify_album.id)["tracks"]["items"]
        if len(track_items):
            return [track_item["id"] for track_item in track_items]
        else:
            return []

    def _get_collection_albums(self, playlist_id) -> List[SpotifyAlbum]:
        """Get all valid albums in the given playlist.
        Albums will only be valid if the tracks are in the correct
        sequential order, not separated from eachother by tracks
        from other albums, and only occur once

        NOTE: albums should be returned in the playlist order as long
        as python version is 3.7+ because dictionaries retain insertion
        order

        NOTE: I'm making this a 'private' function to signify that it really
        shouldn't be used outside of the scope of getting the albums for a
        SpotifyCollection item. This does a lot of expensive spotify api requests,
        so it should only be used if the playlist was changed or if the album items
        in the cache have expired.
        """
        # Create dictionary to hold albums
        album_entries = {}

        # Make iterator of tracks in playlist
        playlist_iter = iter(self.get_playlist_tracks(playlist_id))

        try:
            # Get the first track in playlist
            playlist_track = next(playlist_iter)

            # Act on the current playlist track in the iterator
            while True:
                # The current playlist track's album hasn't been seen before.
                # Make an entry for the album and iterate through the subsequent
                # playlist tracks
                if playlist_track.album.album_type == AlbumType.album and playlist_track.album.id not in album_entries:
                    # Record the album of this first-encountered track
                    album = playlist_track.album

                    # Make an entry for this album
                    album_entries[album.id] = album

                    # Walk through subsequent tracks with the same album id, using disc and track
                    # numbers to confirm that the full album is present in the correct order
                    last_disc_num = None
                    last_track_num = None
                    while album.id == playlist_track.album.id:
                        # To start out, the disc number and track number should both be equal to 1
                        if last_disc_num is None and last_track_num is None and \
                                playlist_track.disc_number == 1 and \
                                playlist_track.track_number == 1:
                            pass
                        # If this disc number is equal to last disc number then the track number
                        # should have been incremented by one
                        elif last_disc_num is not None and last_track_num is not None and \
                                last_disc_num == playlist_track.disc_number and \
                                playlist_track.track_number == (last_track_num + 1):
                            pass
                        # If this disc number is one greater than the last disc number, then the
                        # track number should be equal to 1
                        elif last_disc_num is not None and last_track_num is not None and \
                                playlist_track.disc_number == (last_disc_num + 1) and \
                                playlist_track.track_number == 1:
                            pass
                        # Otherwise the current track must be out of order
                        else:
                            break

                        # Set last equal to current
                        last_disc_num = playlist_track.disc_number
                        last_track_num = playlist_track.track_number

                        # Add this track id to the album
                        album.track_ids.append(playlist_track.id)

                        # Move to the next track in the playlist
                        playlist_track = next(playlist_iter)

                # The current playlist track's album has been seen before. This means that
                # the track is either a duplicate, or separated from the first track in
                # the album by tracks from other albums. In any case, it invalidates the
                # album entry. Set the album entry to invalid, and move on to the next
                # track in the playlist.
                elif playlist_track.album.id in album_entries:
                    album_entries[playlist_track.album.id] = None
                    playlist_track = next(playlist_iter)

                # Otherwise the album type is not an 'album'...just move to the next track
                else:
                    playlist_track = next(playlist_iter)

        # If a stop iteration is received, that means the playlist's tracks have been
        # exhausted - pencils down.
        except StopIteration:
            pass

        # Return albums from valid entries
        return [album for album in album_entries.values()
                if album is not None and len(album.track_ids) == album.total_tracks]
