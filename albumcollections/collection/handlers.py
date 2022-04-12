from flask import render_template, request, url_for, jsonify
import json

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify as spotify_iface

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError

from . import bp


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    try:
        # Get the spotify collection object by playlist id
        collection = spotify_iface.Spotify().get_collection(playlist_id)

    except Exception as e:
        raise albumcollectionsError(f"Failed to load collection {playlist_id} - {e}", url_for('main.index'))

    return render_template('collection/index.html', collection=collection)


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
            spotify_user.remove_album_from_playlist(playlist_id, album_id)
        except Exception as e:
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)


@bp.route('/collection/get_devices', methods=['POST'])
def get_devices():
    """Interface to get the spotify player devices that are
    available to play on currently.
    """
    if request.method == 'POST':
        # Initialize response dict
        response_dict = {"exception": None, "devices": None}

        try:
            response_dict["devices"] = spotify_user.get_devices()
        except Exception as e:
            response_dict["exception"] = str(e)

    return jsonify(response_dict)


@bp.route('/collection/play_collection', methods=['POST'])
def play_collection():
    """Interface to play a collection
    """
    # POST request
    if request.method == 'POST':
        # Get data from post request
        data = json.loads(request.form["data"])
        playlist_id = data["playlist_id"]
        device_id = data["device_id"]
        start_album_id = data["start_album_id"]
        shuffle_albums = data["shuffle_albums"]

        # Initialize response dict
        response_dict = {"played": True, "exception": None, "devices": None}

        try:
            spotify_user.play_collection(playlist_id, start_album_id, shuffle_albums, device_id=device_id)
        except Exception as e:
            response_dict["played"] = False
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
            spotify_user.reorder_collection(playlist_id, moved_album_id, next_album_id)
        except Exception as e:
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)
