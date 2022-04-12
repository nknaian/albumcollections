from typing import List
from flask import redirect, render_template, url_for, flash, request

from albumcollections.spotify import spotify_user
from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
from albumcollections.user import is_user_logged_in, get_user_id
from albumcollections.models import Collection

from albumcollections import db

from .forms import AddCollectionsForm, RemoveCollectionsForm
from . import bp


"""HANDLER FUNCTIONS"""


@bp.route('/', methods=['GET', 'POST'])
def index():
    # If user is logged in then process collection addition and removal forms
    # and load their collections
    if is_user_logged_in():
        # Initialize forms
        add_collections_form = AddCollectionsForm()
        remove_collections_form = RemoveCollectionsForm()

        # Get the user's playlists
        try:
            user_playlists = spotify_user.get_user_playlists()
        except Exception as e:
            raise albumcollectionsError(f"Failed to load user playlists - {e}", url_for('main.index'))

        # Filter user playlist to get their collections
        user_collections = _user_collections(user_playlists)

        # Add the playlist names to the add_collections_form
        add_collections_form.playlists.choices.extend(
            _get_available_playlist_names(user_playlists, user_collections)
        )

        # Handle add_collections_form submission
        if add_collections_form.submit_new_collections.data and add_collections_form.validate():
            _add_collections(add_collections_form, user_playlists)
            return redirect(url_for('main.index'))
        elif add_collections_form.errors:
            flash("Failed to add collections", "danger")

        # Add the collection names to the remove_collections_form
        remove_collections_form.collections.choices.extend(
            [collection.name for collection in user_collections]
        )

        # Handle remove_collections_form submission
        if remove_collections_form.submit_collection_removal.data and remove_collections_form.validate():
            _remove_collections(remove_collections_form, user_collections)
            return redirect(url_for('main.index'))
        elif remove_collections_form.errors:
            print("rerrors?: ", remove_collections_form.errors)
            flash("Failed to remove collections", "danger")

    # Otherwise load nothing
    else:
        user_collections = None
        add_collections_form = None
        remove_collections_form = None

    return render_template(
        'main/index.html',
        user_collections=user_collections,
        add_collections_form=add_collections_form,
        remove_collections_form=remove_collections_form
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
        if user_playlist.name in add_collections_form.playlists.data
    ]

    # Add new collections to the db
    for user_playlist in chosen_user_playlists:
        try:
            if Collection.query.filter_by(playlist_id=user_playlist.id, user_id=get_user_id()).first():
                raise Exception(f"'{user_playlist.name}' already imported as a collection")
            else:
                db.session.add(Collection(playlist_id=user_playlist.id, user_id=get_user_id()))
                db.session.commit()
        except Exception as e:
            raise albumcollectionsError(f"Failed to add collections - {e}", url_for('main.index'))


def _remove_collections(remove_collections_form: RemoveCollectionsForm, user_collections: List[SpotifyPlaylist]):
    # Get user's chosen collections to remove from the form
    collections_to_delete = [
        user_collection
        for user_collection in user_collections
        if user_collection.name in remove_collections_form.collections.data
    ]

    print("collections to delete: ", collections_to_delete)

    for collection in collections_to_delete:
        try:
            collection = Collection.query.filter_by(playlist_id=collection.id, user_id=get_user_id()).first()
            if collection is None:
                raise Exception(f"'{collection.name}' not found")
            else:
                db.session.delete(collection)
                db.session.commit()
        except Exception as e:
            raise albumcollectionsError(f"Failed to remove collections - {e}", url_for('main.index'))


def _user_collections(user_playlists: List[SpotifyPlaylist]) -> List[SpotifyPlaylist]:
    # Get list of playlist ids of user's collections
    user_collection_playlist_ids = [
        collection.playlist_id
        for collection in Collection.query.filter_by(user_id=get_user_id())
    ]

    # Get playlists that user has stored as collections
    return [
        user_playlist
        for user_playlist in user_playlists
        if user_playlist.id in user_collection_playlist_ids
    ]


def _get_available_playlist_names(user_playlists: List[SpotifyPlaylist], user_collections: List[SpotifyPlaylist]):
    user_collection_ids = [collection.id for collection in user_collections]

    return [user_playlist.name for user_playlist in user_playlists if user_playlist.id not in user_collection_ids]
