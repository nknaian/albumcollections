from flask import url_for

from tests.test_main import MainTestCase


class CollectionIndexTestCase(MainTestCase):
    """Test GET on main index route."""
    def test_get_index(self):
        response = self.client.get(url_for("collection.index", playlist_id="dummyplaylistid1"))
        self.assert_200(response)
        self.assertIn(b"dummyplaylist1", response.data)
        self.assertIn(b'dummyalbum1', response.data)
        self.assertIn(b'dummyalbum2', response.data)
