from albumcollections import db

MAX_SPOTIFY_PLAYLIST_ID_LENGTH = 50
MAX_SPOTIFY_SNAPSHOT_ID_LENGTH = 100
MAX_SPOTIFY_USER_ID_LENGTH = 50


class AcUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_user_id = db.Column(db.String(MAX_SPOTIFY_USER_ID_LENGTH), unique=True, nullable=False)
    playback_playlist_id = db.Column(db.String(MAX_SPOTIFY_PLAYLIST_ID_LENGTH))  # depreciated

    collections = db.relationship('Collection', backref=db.backref('ac_user', lazy=True))

    def __repr__(self):
        return '<AcUser %r>' % self.id


class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.String(MAX_SPOTIFY_PLAYLIST_ID_LENGTH), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('ac_user.id'), nullable=False)

    def __repr__(self):
        return '<Collection %r>' % self.id
