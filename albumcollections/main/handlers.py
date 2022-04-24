from typing import List, Tuple
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
    user_collections = None
    add_collections_form = None
    remove_collections_form = None
    add_playlists_disp_len = None
    remove_collections_disp_len = None

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
            _get_available_playlists(user_playlists, user_collections)
        )

        # Get display length of playlist choices
        add_playlists_disp_len = _choices_display_len(len(add_collections_form.playlists.choices))

        # Handle add_collections_form submission
        if add_collections_form.submit_new_collections.data and add_collections_form.validate():
            _add_collections(add_collections_form)
            return redirect(url_for('main.index'))
        elif add_collections_form.errors:
            flash("Failed to add collections", "danger")

        # Add the collection names to the remove_collections_form
        remove_collections_form.collections.choices.extend(
            [(collection.id, collection.name) for collection in user_collections]
        )

        # Get display length of playlist choices
        remove_collections_disp_len = _choices_display_len(len(remove_collections_form.collections.choices))

        # Handle remove_collections_form submission
        if remove_collections_form.submit_collection_removal.data and remove_collections_form.validate():
            _remove_collections(remove_collections_form)
            return redirect(url_for('main.index'))
        elif remove_collections_form.errors:
            flash("Failed to remove collections", "danger")

    return render_template(
        'main/index.html',
        user_collections=user_collections,
        add_collections_form=add_collections_form,
        remove_collections_form=remove_collections_form,
        add_playlists_disp_len=add_playlists_disp_len,
        remove_collections_disp_len=remove_collections_disp_len
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


def _add_collections(add_collections_form: AddCollectionsForm):
    """Add user's chosen playlists to their Collections in the database"""
    for chosen_playlist_id in add_collections_form.playlists.data:
        try:
            if Collection.query.filter_by(playlist_id=chosen_playlist_id, user_id=get_user_id()).first():
                raise Exception(f"'{chosen_playlist_id}' already imported as a collection")
            else:
                db.session.add(Collection(playlist_id=chosen_playlist_id, user_id=get_user_id()))
                db.session.commit()
        except Exception as e:
            raise albumcollectionsError(f"Failed to add collections - {e}", url_for('main.index'))


def _remove_collections(remove_collections_form: RemoveCollectionsForm):
    """Remove user's chosen collections from their Collections in the database"""
    for chosen_collection_id in remove_collections_form.collections.data:
        try:
            collection = Collection.query.filter_by(playlist_id=chosen_collection_id, user_id=get_user_id()).first()
            if collection is None:
                raise Exception(f"'{chosen_collection_id}' not found")
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


def _get_available_playlists(
    user_playlists: List[SpotifyPlaylist],
    user_collections: List[SpotifyPlaylist]
) -> List[Tuple[str, str]]:
    user_collection_ids = [collection.id for collection in user_collections]

    return [
        (user_playlist.id, user_playlist.name)
        for user_playlist in user_playlists
        if user_playlist.id not in user_collection_ids
    ]


def _choices_display_len(num_choices: int) -> int:
    return num_choices if num_choices < 10 else 10
