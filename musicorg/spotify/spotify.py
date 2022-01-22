"""Spotify interface class that uses the spotipy client
credentials authentication method. This class can be used
to interface with spotify for use cases that don't require
access to individual user accounts. So, things like searching
for music, or getting information about music based on a
spotify link.
"""

import random
import copy
from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

from .item.spotify_music import SpotifyMusic, SpotifyAlbum, SpotifyTrack
from .item.spotify_playlist import SpotifyPlaylist
from musicorg.enums import MusicType


"""Maximum number of samples that can be used
in spotipy's "recommendations" function
"""
MAX_REC_SEEDS = 5


class Spotify:
    """Class to interface with Spotify API through an
    instance of client credentials authenticated spotipy.
    """

    """Public Functions"""

    def init_sp(self):
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials())

    def search_for_music(self,
                         music_type: MusicType,
                         search_term: str,
                         num_results=5,
                         popularity_threshold=None) -> List[SpotifyMusic]:
        """Gets spotify music by searching the search term. Filters
        music out that is below the popularity threshold.

        If nothing is found it will return None
        """
        # Search for the music type using the search term
        search = self.sp.search(search_term, type=music_type.name, limit=num_results)
        music_items = search[f'{music_type.name}s']['items']

        # Go through the music items brought up in the search
        spotify_musics = []
        if len(music_items):
            for music_item in music_items:
                # If the popularity is above the threshold, then return
                # the item
                if popularity_threshold is None or \
                        self._get_artists_popularity(music_item['artists']) >= popularity_threshold:
                    if music_type == MusicType.album:
                        if music_item['album_type'] == "album":
                            spotify_musics.append(SpotifyAlbum(music_item))
                    elif music_type == MusicType.track:
                        if music_item['type'] == "track":
                            spotify_musics.append(SpotifyTrack(music_item))

        return spotify_musics

    def recommend_music(self, music_type: MusicType, music_list: List[SpotifyMusic]) -> SpotifyMusic:
        """Gets a spotify recommendation based on a list of spotify music
        passed in.
        """
        # Assure that we have at least one human music rec
        assert len(music_list) > 0

        if music_type == MusicType.album:
            return self._recommend_album(music_list)
        elif music_type == MusicType.track:
            return self._recommend_track(music_list)

    def get_music_from_link(self, music_type, link):
        """Use spotify link to get `SpotifyMusic` object"""
        if music_type == MusicType.album:
            spotify_album = self.sp.album(link)
            return SpotifyAlbum(spotify_album)
        elif music_type == MusicType.track:
            spotify_track = self.sp.track(link)
            return SpotifyTrack(spotify_track)

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

    def spotify_link_invalid(self, music_type: MusicType, spotify_link: str):
        """Check whether the given spotify link is a valid 'music type' link"""
        try:
            self.get_music_from_link(music_type, spotify_link)
            return False
        except SpotifyException:
            return True

    """Private Functions"""

    def _recommend_album(self, human_album_recs: List[SpotifyAlbum]) -> SpotifyAlbum:
        # Get artist seeds from the album list passed in
        seed_artists = [album.get_primary_artist().id
                        for album in human_album_recs]
        if len(seed_artists) > MAX_REC_SEEDS:
            seed_artists = random.sample(seed_artists, MAX_REC_SEEDS)

        # Get an album rec
        album_rec = None
        while album_rec is None:
            # Get a track rec based on the given seed artists
            track_rec = self._get_track_rec_from_seeds(
                human_album_recs, seed_artists=seed_artists)

            # Get a random album by the primary artist of the track rec
            artist_album_items = self.sp.artist_albums(
                track_rec.get_primary_artist().id, album_type="album"
            )['items']
            if len(artist_album_items):
                # Pick a random album from the artist's discography
                album_rec = SpotifyAlbum(random.sample(artist_album_items, 1)[0])

        return album_rec

    def _recommend_track(self, human_track_recs: List[SpotifyTrack]) -> SpotifyTrack:
        # Get the track seeds from the track list passed in (spotipy accepts
        # ids as one of the options for track seeds)
        seed_tracks = [track.id for track in human_track_recs]
        if len(seed_tracks) > MAX_REC_SEEDS:
            seed_tracks = random.sample(seed_tracks, MAX_REC_SEEDS)

        # Get a track rec based on the given seed tracks
        track_rec = None
        while track_rec is None:
            track_rec = self._get_track_rec_from_seeds(
                human_track_recs, seed_tracks=seed_tracks)

        return track_rec

    def _get_track_rec_from_seeds(self,
                                  human_music_recs: List[SpotifyMusic],
                                  seed_tracks=None,
                                  seed_artists=None):
        track_items = self.sp.recommendations(
            seed_tracks=seed_tracks, seed_artists=seed_artists
        )["tracks"]
        sp_track_recs = [SpotifyTrack(track_item) for track_item in track_items]

        # Remove any track that shares an artist with one of the human
        # music recs
        sp_track_recs_copy = copy.deepcopy(sp_track_recs)
        for sp_track_rec in sp_track_recs_copy:
            if any(self._do_musics_share_artist(sp_track_rec, human_music_rec)
                   for human_music_rec in human_music_recs):
                self._remove_music_from_list(sp_track_rec.id, sp_track_recs)

        # Pick one random track
        if len(sp_track_recs):
            return random.sample(sp_track_recs, 1)[0]
        else:
            return None

    def _do_musics_share_artist(self, music1: SpotifyMusic, music2: SpotifyMusic):
        music1_artist_ids = [artist.id for artist in music1.artists]
        music2_artist_ids = [artist.id for artist in music2.artists]

        common_ids = set(music1_artist_ids) & set(music2_artist_ids)

        return bool(common_ids)

    def _remove_music_from_list(self, music_id: str, music_list: List[SpotifyMusic]):
        for music in music_list:
            if music_id == music.id:
                music_list.remove(music)
                break

    def _get_artists_popularity(self, artists):
        """Get the popularity of the most popular artist in the list
        of artists

        Popularity is a number that spotify assigns to music
        based on how many listens it's been getting recently.
        """
        popularity = 0

        for artist in artists:
            artist_popularity = self._get_artist_popularity(artist['id'])
            if artist_popularity > popularity:
                popularity = artist_popularity

        return popularity

    def _get_artist_popularity(self, artist_id):
        return self.sp.artist(artist_id)['popularity']
