from flask import render_template, request, url_for, jsonify, current_app, redirect
import json

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_interface as spotify_iface
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.user import is_user_logged_in
from albumcollections.errors.exceptions import albumcollectionsError

from . import bp


"""ROUTE HANDLERS"""


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    # Get a spotify interface to use based on whether user is logged in
    try:
        if is_user_logged_in():
            sp_interface = spotify_user_iface.SpotifyUserInterface()
            sp_user_id = sp_interface.user_id
        else:
            sp_interface = spotify_iface.SpotifyInterface()
            sp_user_id = None
    except Exception as e:
        raise albumcollectionsError(f"Failed to create spotify interface: {e}", url_for('main.index'))

    # Get collection based on the playlist id
    try:
        collection = sp_interface.get_collection(playlist_id)

    except Exception as e:
        raise albumcollectionsError(f"Failed to load collection {playlist_id}: {e}", url_for('main.index'))

    return render_template('collection/index.html', collection=collection, user_id=sp_user_id)


@bp.route('/collection/shuffle_collection/<string:playlist_id>', methods=['GET', 'POST'])
def shuffle_collection(playlist_id):
    """Shuffle the underlying playlist"""

    try:
        # Get spotify user
        spotify_user = spotify_user_iface.SpotifyUserInterface()

        # Get the collection
        collection = spotify_user.get_collection(playlist_id)

        # Shuffle the collection
        if len(collection.albums) > 1:
            spotify_user.shuffle_collection(collection)

    except Exception as e:
        current_app.logger.error(f"Failed to shuffle collection {playlist_id}: {e}")

    return redirect(url_for('collection.index', playlist_id=collection.id))


@bp.route('/collection/remove_album', methods=['POST'])
def remove_album():
    """Interface to remove an album from the collection playlist
    """
    # POST request
    if request.method == 'POST':
        # Get values from post request
        playlist_id = request.form["playlist_id"]
        album_id = request.form["album_id"]

        # Initialize response dict
        response_dict = {"success": True, "exception": None}

        # Try removing the requested album
        try:
            spotify_user_iface.SpotifyUserInterface().remove_album_from_playlist(playlist_id, album_id)
        except Exception as e:
            current_app.logger.error(f"Failed to remove album {album_id} from playlist {playlist_id}: {e}")
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)


@bp.route('/collection/reorder_collection', methods=['POST'])
def reorder_collection():
    """Interface to reorder a collection
    """
    # POST request
    if request.method == 'POST':
        # Get data from post request
        data = json.loads(request.form["data"])
        playlist_id = data["playlist_id"]
        moved_album_id = data['moved_album_id']
        next_album_id = data['next_album_id']

        # Initialize response dict
        response_dict = {"success": True, "exception": None}

        try:
            spotify_user_iface.SpotifyUserInterface().reorder_collection(playlist_id, moved_album_id, next_album_id)
        except Exception as e:
            current_app.logger.error(f"Failed to reorder collection {playlist_id}: {e}")
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)
