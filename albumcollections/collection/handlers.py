from flask import render_template, request, url_for

from spotipy.exceptions import SpotifyException

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError

from albumcollections import spotify_iface

from . import bp


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    try:
        # Get list of albums in playlist
        playlist_albums = spotify_iface.get_playlist_albums(playlist_id)

        # Get the name of the playlist
        playlist_name = spotify_iface.get_playlist_from_link(playlist_id).name

    except SpotifyException as e:
        raise albumcollectionsError(f"Failed to process playlist - {e}", url_for('main.index'))

    return render_template('collection/index.html',
                           playlist_id=playlist_id,
                           playlist_name=playlist_name,
                           playlist_albums=playlist_albums)


@bp.route('/collection/remove_album', methods=['POST'])
def remove_album():
    """Interface to remove an album from the collection playlist
    """
    # POST request
    if request.method == 'POST':
        # Get values from post request
        playlist_id = request.get_json()["playlist_id"]
        album_id = request.get_json()["album_id"]

        # Initialize response dict
        response_dict = {"success": True, "exception": None}

        # Try removing the requested album
        try:
            spotify_user.remove_album_from_playlist(playlist_id, album_id)
        except SpotifyException as e:
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return response_dict, 200
