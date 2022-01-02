from datetime import datetime
from sqlalchemy.orm import validates

from musicorg import db
from musicorg.enums import MusicType, SnoozinRecType, RoundStatus
from musicorg.errors.exceptions import musicorgError


'''Storage Constants'''

MAX_SPOTIFY_ID_LENGTH = 50
MAX_SPOTIFY_USER_ID_LENGTH = 50
MAX_DISPLAY_NAME_LENGTH = 50
MAX_CATEGORY_NAME_LENGTH = 50


'''SQL Classes'''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_user_id = db.Column(db.String(MAX_SPOTIFY_USER_ID_LENGTH), unique=True, nullable=False)
    display_name = db.Column(db.String(MAX_DISPLAY_NAME_LENGTH))

    albums = db.relationship('Album', backref=db.backref('user', lazy=True))
    categories = db.relationship('Cateogory', backref=db.backref('user', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.id


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id= db.Column(db.String(MAX_SPOTIFY_ID_LENGTH), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    @validates('spotify_id')
    def validate_spotify_id(self, key, spotify_id):
        if len(spotify_id) > MAX_SPOTIFY_ID_LENGTH:
            raise musicorgError(f"Spotify id greater than storage limit of {MAX_SPOTIFY_ID_LENGTH} characters.")
        return spotify_id

    def __repr__(self):
        return '<Album %r>' % self.id


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(MAX_CATEGORY_NAME_LENGTH))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    albums = db.relationship('Album', backref=db.backref('category', lazy=True))

    @validates('name')
    def validate_name(self, key, name):
        if len(name) > MAX_CATEGORY_NAME_LENGTH:
            raise musicorgError(f"long id greater than storage limit of {MAX_CATEGORY_NAME_LENGTH} characters.")
        return name

    def __repr__(self):
        return '<Category %r>' % self.id
