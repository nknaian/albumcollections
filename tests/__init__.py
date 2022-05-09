import unittest
from unittest.mock import Mock
from flask.helpers import url_for
import flask_testing

from albumcollections.config import Config
from albumcollections.spotify.item.spotify_artist import SpotifyArtist
from albumcollections.spotify.item.spotify_music import SpotifyAlbum
from albumcollections.spotify.item.spotify_collection import SpotifyCollection
from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections import create_app


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    WTF_CSRF_ENABLED = False

    # Overwrite session type to not have to deal with database in tests
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'


class PickableMock(Mock):
    """This is needed for any mock objects that are going to
    be added to the cache as part of tests. It wasn't easy to
    find this workaround...https://github.com/testing-cabal/mock/issues/139
    """
    def __reduce__(self):
        return (Mock, ())


"""MOCK SPOTIFY CLIENT CREDENTIALS INTERFACE"""


class SpotifyInterfaceMock(Mock):
    """Mock object to patch in to replace
    albumcollections.spotify.spotify_interface.SpotifyInterface() class
    """
    def get_collection(self, *args, **kwargs):
        """Return dummy mock collection
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

        collection_mock = Mock(spec=SpotifyCollection)
        collection_mock.albums = [album_mock1, album_mock2]
        collection_mock.name = "dummycollectionname"

        return collection_mock


class SpotifyUserInterfaceMock(SpotifyInterfaceMock):
    user_id = "12345ABC"

    def get_playlists(self, *args):
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
        playlist2_mock.name = "dummyplaylist2"
        playlist2_mock.img_url = None

        playlist3_mock = Mock(spec=SpotifyPlaylist)
        playlist3_mock.id = "dummyplaylistid3"
        playlist3_mock.link = "dummyplaylistlink3"
        playlist3_mock.name = "dummyplaylist3"
        playlist3_mock.img_url = None

        return ([playlist1_mock, playlist2_mock, playlist3_mock], [])


class AlbumCollectionsTestCase(flask_testing.TestCase, unittest.TestCase):
    """Base test case class for all tests in albumcollections. Creates app
    using TestingConfig.
    """
    def create_app(self):
        # pass in test configuration
        return create_app(TestingConfig)

    def setUp(self):
        self.unauth_dummy_user()

    def tearDown(self):
        pass

    """MOCK SPOTIFY USER INTERFACE MODULE FUNCTIONS"""

    def auth_dummy_user(self, *args):
        spotify_user_iface.is_auth = Mock(side_effect=lambda *args: True)
        spotify_user_iface.unauth_user = Mock(side_effect=self.unauth_dummy_user)

    def unauth_dummy_user(self, *args):
        spotify_user_iface.is_auth = Mock(side_effect=lambda *args: False)
        spotify_user_iface.auth_user = Mock(side_effect=self.auth_dummy_user)
        spotify_user_iface.get_auth_url = Mock(side_effect=lambda *args: url_for("test.fake_sp_auth"))
