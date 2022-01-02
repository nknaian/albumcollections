from .spotify_item import SpotifyItem


class SpotifyPlaylist(SpotifyItem):
    """Class to hold selected information about a spotify artist"""

    IMG_DIMEN = 300
    MAX_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 300

    def __init__(self, spotify_playlist):
        # Initialize base class
        super().__init__(spotify_playlist)

        # TODO: Investigate how to get an image...right now the only dimension
        # available is 640...which is too large. And also, when I change the
        # image in spotify, it still keeps the original placeholder image (just
        # the first song in the playlist)
        self._set_image_url(spotify_playlist["images"])
