from unittest.mock import patch
from flask import url_for

from tests import SpotifyInterfaceMock

from tests.test_main import MainTestCase


class CollectionIndexTestCase(MainTestCase):
    """Test GET on main index route."""
    @patch('albumcollections.spotify.spotify_interface.SpotifyInterface', new_callable=SpotifyInterfaceMock)
    def test_get_index(self, _mock):
        response = self.client.get(url_for("collection.index", playlist_id="dummyplaylistid1"))
        self.assert_200(response)
        self.assertIn(b"dummycollectionname", response.data)
        self.assertIn(b'dummyalbum1', response.data)
        self.assertIn(b'dummyalbum2', response.data)
