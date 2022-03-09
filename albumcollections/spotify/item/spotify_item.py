class SpotifyItem():
    """Base class for a Spotify object. Holds selected information
    about a spotify item retrieved through api call.
    """

    def __init__(self, spotify_item):
        # Name of the spotify music object
        self.name = spotify_item["name"]

        # Get the open.spotify link to the music
        # It may not exist...(there are some entires in
        # spotify grayed out, marked as 'unavailable')
        try:
            self.link = spotify_item["external_urls"]["spotify"]
        except KeyError:
            self.link = None

        # Get the spotify id of the music
        self.id = spotify_item["id"]

        # Get the uri
        self.uri = spotify_item["uri"]

        # url for image of item
        self.img_url = None

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def _set_image_url(self, images):
        for img in images:
            if img["height"] == self.IMG_DIMEN and img["width"] == self.IMG_DIMEN:
                self.img_url = img["url"]
                break
