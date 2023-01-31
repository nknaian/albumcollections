from typing import List
from albumcollections import cache
from albumcollections.spotify.item.spotify_music import SpotifyAlbum

from .spotify_item import SpotifyItem


class SpotifyCollection(SpotifyItem):
    """Class to hold selected information about a spotify collection.

    Uses database entries associated with playlist id to reduce loading time.
    """

    IMG_DIMEN = 300

    def __init__(self, spotify_playlist):
        # Initialize base class
        super().__init__(spotify_playlist)

        self.__albums = None

        self._set_image_url(spotify_playlist["images"])

        self.owner_id = spotify_playlist["owner"]["id"]

        # Get current snapshot id
        self.snapshot_id = spotify_playlist["snapshot_id"]

    @property
    def albums(self) -> List[SpotifyAlbum]:
        """Get albums.

        If the member private variable is None then attempt to get
        albums from the cache.
        """
        # Try to load albums from cache if albums haven't been set
        if self.__albums is None:
            cached_snapshot_id = cache.get(f"collection_{self.id}_snapshot")

            # Remove stale cache info if snapshot id for the collection has changed
            if cached_snapshot_id is not None and self.snapshot_id is not None and \
                    cached_snapshot_id != self.snapshot_id:
                cache.delete(f"collection_{self.id}_snapshot")
                cache.delete(f"collection_albums_{self.id}")
                self.__albums = None
            # Load the albums from the cache if the snapshot for the collection has not changed
            elif cached_snapshot_id is not None and self.snapshot_id is not None and \
                    cached_snapshot_id == self.snapshot_id:
                self.__albums = cache.get(f"collection_albums_{self.id}")

        return self.__albums

    @albums.setter
    def albums(self, albums: List[SpotifyAlbum]):
        self.__albums = albums
        cache.set(f"collection_albums_{self.id}", albums)
        cache.set(f"collection_{self.id}_snapshot", self.snapshot_id)
