from unittest.mock import patch

from flask.helpers import url_for

from albumcollections.models import User
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from tests import SpotifyUserInterfaceMock
from tests.test_user import UserTestCase


class UserLoginTestCase(UserTestCase):
    """Test flows involving POSTS to the user.login route

    The 'user.sp_auth_complete' route is also exercised through
    these tests.
    """
    @patch(
        'albumcollections.spotify.spotify_user_interface.SpotifyUserInterface',
        new_callable=SpotifyUserInterfaceMock
    )
    def test_login_user(self, _mock):
        # Visit main page. Verify that the text 'Login' is on the page
        response = self.client.get(url_for('main.index'))
        self.assert_200(response)
        self.assertIn(bytes('Login', 'utf-8'), response.data)

        # Make post to login from the main page
        response = self.client.post(
            url_for('user.login'),
            data=dict(login_with_spotify="Log in"),
            follow_redirects=True,
        )

        # Verify that the post was successful and the user
        # was added to the database and is authenticated
        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].spotify_user_id, SpotifyUserInterfaceMock.user_id)
        self.assertTrue(spotify_user_iface.is_auth())


class UserLogoutTestCase(UserTestCase):
    """Test flows involving POST to the user.logout route
    """
    def test_logout_user_from_mainindex(self):
        # Mock authentication of the fake user
        self.auth_dummy_user()

        # Make POST to logout page from the main index page
        response = self.client.post(
            url_for('user.logout'),
            data=dict(logout_from_spotify="Log out"),
            follow_redirects=True,
        )

        # Verify that post was successful and the user is now
        # marked as being not authenticated
        self.assert200(response)
        self.assertFalse(spotify_user_iface.is_auth())
