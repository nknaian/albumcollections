import unittest
from unittest.mock import Mock
from flask.helpers import url_for

import flask_testing

from albumcollections.config import Config
from albumcollections.spotify.item.spotify_artist import SpotifyArtist
from albumcollections.spotify.item.spotify_music import SpotifyAlbum
from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
import albumcollections.spotify.spotify_user as sp_user

from albumcollections import spotify_iface

from albumcollections import create_app, cache


class PickableMock(Mock):
    """This is needed for any mock objects that are going to
    be added to the cache as part of tests. It wasn't easy to
    find this workaround...https://github.com/testing-cabal/mock/issues/139
    """
    def __reduce__(self):
        return (Mock, ())


class TestingConfig(Config):
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class AlbumCollectionsTestCase(flask_testing.TestCase, unittest.TestCase):
    """Base test case class for all tests in albumcollections. Creates app
    using TestingConfig.
    """
    def create_app(self):
        # pass in test configuration
        return create_app(TestingConfig)

    def setUp(self):
        # Mock the user being logged out
        self.unauth_dummy_user()

        amock = PickableMock()

        cache.set("value", amock)

        # Mock spotify interface
        spotify_iface.get_playlist_albums = Mock(side_effect=self._mock_get_playlist_albums)
        spotify_iface.get_playlist_from_link = Mock(side_effect=self._mock_get_playlist_from_link)

    def tearDown(self):
        pass

    """MOCK SPOTIFY USER INTERFACE"""

    DUMMY_USER_SP_ID = "12345ABC"
    DUMMY_USER_DISPLAY_NAME = "Dummy User"

    def _raise_sp_test_exception(self, *args):
        """Raises an exception to authorize at the fake sp auth route"""
        raise sp_user.SpotifyUserAuthFailure(auth_url=url_for("test.fake_sp_auth"))

    def _mock_get_user_playlists(self, *args):
        """Return a list of dummy spotify playlists
        """
        playlist1_mock = Mock(spec=SpotifyPlaylist)
        playlist1_mock.id = "dummyplaylistid1"
        playlist1_mock.link = "dummyplaylistlink1"
        playlist1_mock.name = "dummyplaylist1"
        playlist1_mock.img_url = None

        playlist2_mock = Mock(spec=SpotifyPlaylist)
        playlist2_mock.id = "dummyplaylistid2"
        playlist2_mock.link = "dummyplaylistlink2"
        playlist1_mock.name = "dummyplaylist2"
        playlist2_mock.img_url = None

        return [playlist1_mock, playlist2_mock]

    def auth_dummy_user(self, *args):
        sp_user.get_user_id = Mock(side_effect=lambda *args: self.DUMMY_USER_SP_ID)
        sp_user.is_authenticated = Mock(side_effect=lambda *args: True)
        sp_user.get_user_display_name = Mock(side_effect=lambda *args: self.DUMMY_USER_DISPLAY_NAME)
        sp_user.logout = Mock(side_effect=self.unauth_dummy_user)
        sp_user.get_user_playlists = Mock(side_effect=self._mock_get_user_playlists)

    def unauth_dummy_user(self, *args):
        sp_user.get_user_id = Mock(side_effect=self._raise_sp_test_exception)
        sp_user.is_authenticated = Mock(side_effect=lambda *args: False)
        sp_user.get_user_display_name = Mock(side_effect=self._raise_sp_test_exception)
        sp_user.auth_new_user = Mock(side_effect=self.auth_dummy_user)
        sp_user.get_user_playlists = Mock(side_effect=lambda *args: [])

    """MOCK SPOTIFY MUSIC"""

    def _mock_get_playlist_from_link(self, *args):
        playlist1_mock = Mock(spec=SpotifyPlaylist)
        playlist1_mock.id = "dummyplaylistid1"
        playlist1_mock.link = "dummyplaylistlink1"
        playlist1_mock.name = "dummyplaylist1"
        playlist1_mock.img_url = None

        return playlist1_mock

    def _mock_get_playlist_albums(self, *args):
        """Return list of albums with dummy attributes
        """
        album_mock1 = PickableMock(spec=SpotifyAlbum)
        album_mock1.name = "dummyalbum1"
        album_mock1.artists = [PickableMock(spec=SpotifyArtist)]
        album_mock1.artists[0].name = "dummyalbumartist1"
        album_mock1.id = "dummyalbumid1"
        album_mock1.link = "dummyalbumlink1"
        album_mock1.img_url = None

        album_mock2 = PickableMock(spec=SpotifyAlbum)
        album_mock2.name = "dummyalbum2"
        album_mock2.artists = [PickableMock(spec=SpotifyArtist)]
        album_mock2.artists[0].name = "dummyalbumartist2"
        album_mock2.id = "dummyalbumid2"
        album_mock2.link = "dummyalbumlink2"
        album_mock2.img_url = None

        return [album_mock1, album_mock2]