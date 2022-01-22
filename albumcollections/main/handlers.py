from flask import render_template

from albumcollections.spotify import spotify_user

from . import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if spotify_user.is_authenticated():
        user_playlists = spotify_user.get_user_playlists()
    else:
        user_playlists = None

    return render_template('main/index.html', user_playlists=user_playlists)
