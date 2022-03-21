from flask import render_template, flash

from spotipy.exceptions import SpotifyException

from albumcollections.spotify import spotify_user

from . import bp


@bp.route('/', methods=['GET', 'POST'])
def index():
    try:
        if spotify_user.is_authenticated():
            user_collections = spotify_user.get_user_collections()
        else:
            user_collections = None
    except SpotifyException as e:
        flash(f"Spotify Exception occurred while loading collections: {e}", "warning")
        user_collections = None
    except ConnectionError:
        flash("Connection error encountered while loading collections", "warning")
        user_collections = None
    except Exception as e:
        flash(f"Exception occurred while loading collections: {e}", "danger")
        user_collections = None

    return render_template('main/index.html', user_collections=user_collections)
