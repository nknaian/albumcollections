class SpotifyItem():
    """Base class for a Spotify object. Holds selected information
    about a spotify item retrieved through api call.
    """

    def __init__(self, spotify_item):
        # Name of the spotify music object
        self.name = spotify_item["name"]

        # Get the open.spotify link to the music
        self.link = spotify_item["external_urls"]["spotify"]

        # Get the spotify id of the music
        self.id = spotify_item["id"]

        # url for image of item
        self.img_url = None

    def _set_image_url(self, images):
        for img in images:
            if img["height"] == self.IMG_DIMEN and img["width"] == self.IMG_DIMEN:
                self.img_url = img["url"]
                break
