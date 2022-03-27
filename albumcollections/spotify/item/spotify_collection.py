from typing import List
from albumcollections import db, cache
from albumcollections.spotify.item.spotify_music import SpotifyAlbum

from .spotify_item import SpotifyItem


MAX_SPOTIFY_PLAYLIST_ID_LENGTH = 50
MAX_SPOTIFY_SNAPSHOT_ID_LENGTH = 100


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.String(MAX_SPOTIFY_PLAYLIST_ID_LENGTH), unique=True, nullable=False)
    snapshot_id = db.Column(db.String(MAX_SPOTIFY_SNAPSHOT_ID_LENGTH))
    num_albums = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.id


class SpotifyCollection(SpotifyItem):
    """Class to hold selected information about a spotify collection.

    Uses database entries associated with playlist id to reduce loading time.
    """

    IMG_DIMEN = 300

    def __init__(self, spotify_playlist):
        # Initialize base class
        super().__init__(spotify_playlist)

        self._set_image_url(spotify_playlist["images"])

        # Get current snapshot id
        self.snapshot_id = spotify_playlist["snapshot_id"]

        # Get the stored entry for this collection. Create an entry for it
        # if there isn't one already
        self.stored_collection = Collection.query.filter_by(playlist_id=self.id).first()
        if self.stored_collection is None:
            self.stored_collection = Collection(playlist_id=self.id)
            db.session.add(self.stored_collection)
            db.session.commit()

        # Compare this snapshot to the stored snapshot. If it's different than it means
        # that the playlist is changed.
        if self.stored_collection.snapshot_id is not None and \
                self.stored_collection.snapshot_id == self.snapshot_id:
            self.changed = False
        else:
            self.changed = True

            # Store snapshot id in db entry
            self.stored_collection.snapshot_id = self.snapshot_id
            db.session.commit()

    @property
    def albums(self) -> List[SpotifyAlbum]:
        # This is a bit weird, because this would return `None` in the case
        # that the cache expires but a Collection object is still being used.
        # I don't really think it's a problem though, because we shouldn't
        # be holding on to a collection item for a long time without having already
        # gotten it's albums
        return cache.get(f"collection_albums_{self.id}")

    @albums.setter
    def albums(self, albums: List[SpotifyAlbum]):
        cache.set(f"collection_albums_{self.id}", albums)

    @property
    def num_albums(self):
        return self.stored_collection.num_albums

    @num_albums.setter
    def num_albums(self, num_albums):
        self.stored_collection.num_albums = num_albums
        db.session.commit()
