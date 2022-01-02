from .spotify_item import SpotifyItem


class SpotifyArtist(SpotifyItem):
    """Class to hold selected information about a spotify artist"""

    def __init__(self, spotify_artist):
        # Initialize base class
        super().__init__(spotify_artist)
