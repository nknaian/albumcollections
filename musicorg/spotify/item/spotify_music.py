from .spotify_item import SpotifyItem
from .spotify_artist import SpotifyArtist


class SpotifyMusic(SpotifyItem):
    """Base class for a spotify music (album or track).
    """

    def __init__(self, spotify_music):
        # Initialize base class
        super().__init__(spotify_music)

        # List of artists credited
        self.artists = [
            SpotifyArtist(spotify_artist) for spotify_artist in spotify_music["artists"]
        ]

        self.release_date = None

    def get_artists_comma_separated(self):
        return ', '.join(artist.name for artist in self.artists)

    def format_for_response_dict(self):
        return {"music_name": str(self), "music_img_url": self.img_url, "music_link": self.link}

    def get_primary_artist(self):
        return self.artists[0]

    def get_release_year(self):
        return self.release_date.split("-")[0]

    def _set_release_date(self, release_date):
        self.release_date = release_date

    def __str__(self) -> str:
        return (f"{self.name} by "
                f"{self.get_artists_comma_separated()}")


class SpotifyAlbum(SpotifyMusic):
    """Class to hold selected information about a spotify album."""

    IMG_DIMEN = 300

    def __init__(self, spotify_album):
        # Initialize base class
        super().__init__(spotify_album)

        # Get image url with given IMG_DIMEN
        self._set_image_url(spotify_album["images"])

        # Set the release year
        self._set_release_date(spotify_album["release_date"])


class SpotifyTrack(SpotifyMusic):
    """Class to hold selected information about a spotify track."""

    IMG_DIMEN = 64

    def __init__(self, spotify_track):
        # Initialize base class
        super().__init__(spotify_track)

        # Set the album item for this track
        self.album_item = SpotifyItem(spotify_track["album"])

        # Get image url with given IMG_DIMEN
        self._set_image_url(spotify_track["album"]["images"])

        # Set the release date (of the album)
        self._set_release_date(spotify_track["album"]["release_date"])
