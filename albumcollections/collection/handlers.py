from flask import flash, render_template, request, url_for, jsonify
import json
from requests.exceptions import ConnectionError

from spotipy.exceptions import SpotifyException

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify as spotify_iface

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError

from . import bp
from .test_collection import TestSpotifyCollection


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    try:
        # Backdoor to test visuals with no connection to spotify
        if playlist_id == "offline":
            collection = TestSpotifyCollection()
        # Get the collection by playlist id, reloading albums objects for it
        else:
            collection = spotify_iface.Spotify().get_collection_from_playlist_id(playlist_id, reload_albums=True)

        collection_name = collection.name
        collection_albums = collection.albums

    except SpotifyException as e:
        raise albumcollectionsError(f"Spotify Exception occurred while loading collection: {e}", url_for('main.index'))
    except ConnectionError:
        flash("Connection error encountered while loading playlist", "warning")
        collection_name = ""
        collection_albums = []
    except Exception as e:
        raise albumcollectionsError(f"Exception occured while loading collection: {e}", url_for('main.index'))

    return render_template('collection/index.html',
                           playlist_id=playlist_id,
                           playlist_name=collection_name,
                           playlist_albums=collection_albums)


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
        except SpotifyException as e:
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
        except SpotifyException as e:
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
        except SpotifyException as e:
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
        except SpotifyException as e:
            response_dict["success"] = False
            response_dict["exception"] = str(e)

        return jsonify(response_dict)
