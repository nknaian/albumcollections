from flask import render_template, redirect, url_for, request

from musicorg.spotify.spotify import SpotifyException
from musicorg.spotify.item.spotify_music import SpotifyAlbum
from musicorg.spotify import spotify_user

from musicorg import spotify_iface, cache

from . import bp


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    # Get list of albums in playlist
    playlist_albums = spotify_iface.get_playlist_albums(playlist_id)

    # Cache the list of albums
    # NOTE: What should timeout be?
    cache.set(f"playlist_albums_{playlist_id}", playlist_albums, timeout=0)

    # Get the name of the playlist
    playlist_name = spotify_iface.get_playlist_from_link(playlist_id).name

    return render_template('collection/index.html', playlist_id=playlist_id, playlist_name=playlist_name, playlist_albums=playlist_albums)


@bp.route('/collection/remove_album', methods=['POST'])
def remove_album():
    """Interface to remove an album from the collection playlist
    """
    # POST request
    if request.method == 'POST':
        # Get values from post request
        playlist_id = request.get_json()["playlist_id"]
        album_index = int(request.get_json()["album_index"])

        # Initialize response dict
        response_dict = {"success": True}

        # Get cached playlist albums
        playlist_albums = cache.get(f"playlist_albums_{playlist_id}")

        # If we've got albums, then go ahead and remove the requested one
        if playlist_albums:
            # Get SpotifyAlbum that was requested to be removed
            album = playlist_albums[album_index]

            try:
                spotify_user.remove_album_from_playlist(playlist_id, album.id)
            except SpotifyException:
                response_dict["success"] = False

        return response_dict, 200