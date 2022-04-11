from typing import List
from flask import redirect, render_template, url_for, flash, request

import albumcollections.spotify.spotify as spotify_iface

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.spotify.item.spotify_collection import SpotifyCollection
from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
from albumcollections.user import is_user_logged_in, get_user_id
from albumcollections.models import Collection

from albumcollections import db

from .forms import AddCollectionsForm
from . import bp


"""HANDLER FUNCTIONS"""


@bp.route('/', methods=['GET', 'POST'])
def index():
    # If user is logged in then process collection addition and removal forms
    # and load their collections
    if is_user_logged_in():
        add_collections_form = AddCollectionsForm()

        # Get the user's playlists
        try:
            user_playlists = spotify_user.get_user_playlists()
        except Exception as e:
            raise albumcollectionsError(f"Failed to load user playlists - {e}", url_for('main.index'))

        # Load the user's collections
        user_collections = _load_collections()

        # Add the playlists to the form
        add_collections_form.available_playlists.choices.extend(
            _get_available_playlist_names(user_playlists, user_collections)
        )

        # Handle form submission
        if add_collections_form.validate_on_submit():
            _add_collections(add_collections_form, user_playlists)
            return redirect(url_for('main.index'))
        elif add_collections_form.errors:
            flash("Failed to add collections", "error")

    # Otherwise load nothing
    else:
        add_collections_form = None
        user_collections = None

    return render_template(
        'main/index.html',
        user_collections=user_collections,
        add_collections_form=add_collections_form
    )


@bp.route('/about', methods=['GET'])
def about():
    return render_template('main/about.html')


@bp.route('/load_redirect', methods=['GET'])
def load_redirect():
    return render_template(
        'main/load-redirect.html',
        redirect_location=request.args.get("redirect_location"),
        load_message=request.args.get("load_message")
    )


"""PRIVATE HELPER FUNCTIONS"""


def _add_collections(add_collections_form: AddCollectionsForm, user_playlists: List[SpotifyPlaylist]):
    # Get user's chosen playlists to add as collections from the form
    chosen_user_playlists = [
        user_playlist
        for user_playlist in user_playlists
        if user_playlist.name in add_collections_form.available_playlists.data
    ]

    # Add new collections to the db
    for user_playlist in chosen_user_playlists:
        try:
            if Collection.query.filter_by(playlist_id=user_playlist.id, user_id=get_user_id()).first():
                raise Exception(f"'{user_playlist.name}' already present in your account")
            else:
                db.session.add(Collection(playlist_id=user_playlist.id, user_id=get_user_id()))
                db.session.commit()
        except Exception as e:
            raise albumcollectionsError(f"Failed to add collections - {e}", url_for('main.index'))


def _load_collections() -> List[SpotifyCollection]:
    return [
        spotify_iface.Spotify().get_collection(collection_entry.playlist_id, load_albums=False)
        for collection_entry in Collection.query.filter_by(user_id=get_user_id())
    ]


def _get_available_playlist_names(user_playlists, user_collections: List[SpotifyCollection]):
    user_collection_ids = [collection.id for collection in user_collections]

    return [user_playlist.name for user_playlist in user_playlists if user_playlist.id not in user_collection_ids]
