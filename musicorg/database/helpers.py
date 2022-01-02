import secrets

from flask.helpers import url_for

from musicorg.database.models import User, Album, Category
from musicorg.enums import RoundStatus
from musicorg.errors.exceptions import musicorgAlert

from musicorg import db


def add_category_to_db(user_id, name):
    """Add a category to the database with the given properties

    Return the newly added category object
    """

    category = Category(
        name=name,
        user_id=user_id
    )
    db.session.add(category)
    db.session.commit()

    return category


def add_album_to_db(user_id, category_id, spotify_id):
    """Add an album to the database with the given properties

    Return the newly added album object
    """
    album = Album(
        spotify_id=spotify_id,
        user_id=user_id,
        category_id=category_id,
    )
    db.session.add(album)
    db.session.commit()

    return album


def add_user_to_db(spotify_user_id, display_name):
    user = User(
        spotify_user_id=spotify_user_id,
        display_name=display_name
    )
    db.session.add(user)
    db.session.commit()

    return user


def lookup_user_in_db(spotify_user_id) -> User:
    return User.query.filter_by(spotify_user_id=spotify_user_id).first()


"""PRIVATE FUNCTIONS"""


def _create_round_long_id():
    return secrets.token_urlsafe(16)
