from flask.helpers import url_for

from tests.test_user import UserTestCase


class UserLoginTestCase(UserTestCase):
    """Test flows involving POSTS to the user.login route

    The 'user.sp_auth_complete' route is also exercised through
    these tests.
    """
    def test_login_user(self):
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

        # Verify that post was successful and redirected back to the main page
        # and now UI is ready for user to log out
        self.assert200(response)
        self.assertIn(bytes("Log out", 'utf-8'), response.data)


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

        # Verify that post was successful and redirected back to the main page
        # and now UI is ready for user to log in
        self.assert200(response)
        self.assertIn(bytes("Login", 'utf-8'), response.data)
