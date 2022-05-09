from unittest.mock import patch
from flask import url_for

from albumcollections.models import User

from albumcollections import db

from tests import SpotifyInterfaceMock, SpotifyUserInterfaceMock

from tests.test_main import MainTestCase


class CollectionIndexTestCase(MainTestCase):
    """Test GET on main index route."""

    @patch(
        'albumcollections.spotify.spotify_user_interface.SpotifyUserInterface',
        new_callable=SpotifyUserInterfaceMock
    )
    def test_authed_user_get_index(self, _mock):
        """Test that an authenticated user can view a collection"""
        self.auth_dummy_user()
        db.session.add(User(spotify_user_id=SpotifyUserInterfaceMock.user_id))
        db.session.commit()

        response = self.client.get(url_for("collection.index", playlist_id="dummyplaylistid1"))
        self.assert_200(response)
        self.assertIn(b"dummycollectionname", response.data)
        self.assertIn(b'dummyalbum1', response.data)
        self.assertIn(b'dummyalbum2', response.data)

    @patch(
        'albumcollections.spotify.spotify_interface.SpotifyInterface',
        new_callable=SpotifyInterfaceMock
    )
    def test_unauthed_user_get_index(self, _mock):
        """Test that an unauthenticated user can view a collection"""
        response = self.client.get(url_for("collection.index", playlist_id="dummyplaylistid1"))
        self.assert_200(response)
        self.assertIn(b"dummycollectionname", response.data)
        self.assertIn(b'dummyalbum1', response.data)
        self.assertIn(b'dummyalbum2', response.data)
