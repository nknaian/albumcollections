from flask import render_template, url_for

from spotipy.exceptions import SpotifyException

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError

from . import bp


@bp.route('/', methods=['GET', 'POST'])
def index():
    if spotify_user.is_authenticated():
        try:
            user_collections = spotify_user.get_user_collections()
        except SpotifyException as e:
            spotify_user.logout()
            raise albumcollectionsError(f"Failed to get playlists - {e}", url_for('main.index'))
    else:
        user_collections = None

    return render_template('main/index.html', user_collections=user_collections)
