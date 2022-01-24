from flask import render_template, url_for

from spotipy.exceptions import SpotifyException

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError

from . import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if spotify_user.is_authenticated():
        try:
            user_playlists = spotify_user.get_user_playlists()
        except SpotifyException as e:
            spotify_user.logout()
            raise albumcollectionsError(f"Failed to get playlists - {e}", url_for('main.index'))
    else:
        user_playlists = None

    return render_template('main/index.html', user_playlists=user_playlists)
