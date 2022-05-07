from unittest.mock import patch

from flask import url_for

from albumcollections.models import User, Collection

from tests.test_main import MainTestCase

from tests import SpotifyUserInterfaceMock

from albumcollections import db


class MainIndexTestCase(MainTestCase):
    """Test GET on main index route."""
    def test_get_index_logged_out(self):
        response = self.client.get(url_for("main.index"))
        self.assert_200(response)

    @patch(
        'albumcollections.spotify.spotify_user_interface.SpotifyUserInterface',
        new_callable=SpotifyUserInterfaceMock
    )
    def test_get_index_logged_in(self, _mock):
        # Auth dummy user and add them to database
        self.auth_dummy_user()
        db.session.add(User(spotify_user_id=SpotifyUserInterfaceMock.user_id))
        db.session.commit()

        response = self.client.get(url_for("main.index"))
        self.assert_200(response)

    @patch(
        'albumcollections.spotify.spotify_user_interface.SpotifyUserInterface',
        new_callable=SpotifyUserInterfaceMock
    )
    def test_add_collections(self, _mock):
        # Auth dummy user and add them to database
        self.auth_dummy_user()
        db.session.add(User(spotify_user_id=SpotifyUserInterfaceMock.user_id))
        db.session.commit()

        # Make post with `AddCollectionsForm` data
        response = self.client.post(url_for("main.index"), data=dict(
            playlists=["dummyplaylistid1", "dummyplaylistid2"],
            submit_new_collections="Submit",
        ), follow_redirects=True)

        self.assert_200(response)

        # Make sure that both playlists got added
        collections = Collection.query.all()
        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0].playlist_id, "dummyplaylistid1")
        self.assertEqual(collections[1].playlist_id, "dummyplaylistid2")

    @patch(
        'albumcollections.spotify.spotify_user_interface.SpotifyUserInterface',
        new_callable=SpotifyUserInterfaceMock
    )
    def test_remove_collections(self, _mock):
        # Auth dummy user and add them to database
        self.auth_dummy_user()
        db.session.add(User(spotify_user_id=SpotifyUserInterfaceMock.user_id))
        db.session.commit()

        # Add a few collections
        db.session.add(Collection(playlist_id="dummyplaylistid1", user_id=1))
        db.session.add(Collection(playlist_id="dummyplaylistid2", user_id=1))
        db.session.add(Collection(playlist_id="dummyplaylistid3", user_id=1))
        db.session.commit()

        # Make post with `RemoveCollectionsForm` data
        response = self.client.post(url_for("main.index"), data=dict(
            collections=["dummyplaylistid1", "dummyplaylistid2"],
            submit_collection_removal="Submit",
        ), follow_redirects=True)

        self.assert_200(response)

        # Make sure that only one collection remains
        collections = Collection.query.all()
        self.assertEqual(len(collections), 1)
        self.assertEqual(collections[0].playlist_id, "dummyplaylistid3")


class MainAboutTestCase(MainTestCase):
    """Test GET on main about route."""
    def test_get_about(self):
        response = self.client.get(url_for("main.about"))
        self.assert_200(response)
