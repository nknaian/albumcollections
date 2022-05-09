from typing import List, Tuple
from flask import url_for, flash, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
from albumcollections.main import add_collections, remove_collections
from albumcollections.models import Collection
from albumcollections.user import get_user_id

from .forms import AddCollectionsForm, RemoveCollectionsForm


def process(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    add_collections_form: AddCollectionsForm,
    remove_collections_form: RemoveCollectionsForm,
) -> Tuple[bool, List[SpotifyPlaylist]]:
    """Get the list of collections that the user has chosen out of their
    Spotify playlists and process the add/remove collection forms

    Return a tuple of:
    - Whether the user's collections were changed during processing of forms
    - The user's collections before form processing
    """
    collections_changed = False

    # Get the user's playlists, and any errors that were encountered while
    # trying to get playlists. It should not be possible for this function
    # to raise an exception.
    user_playlists, playlist_retreival_errors = spotify_user.get_playlists()
    if len(playlist_retreival_errors):
        current_app.logger.error(
            f'User {spotify_user.display_name} encountered failures while'
            f' getting playlists: {", ".join(playlist_retreival_errors)}'
        )
        if len(user_playlists):
            flash("Failed to load some playlists", "warning")
        else:
            flash("Failed to load playlists", "danger")

    # Filter user playlist to get their collections
    try:
        user_collections = _user_collections(user_playlists)
    except Exception as e:
        raise albumcollectionsError(
            f"{spotify_user.display_name} failed to get user collections - {e}", url_for('main.index')
        )

    # Get the available playlists from the user's account that could be added as collections
    available_playlists = _get_available_playlists(user_playlists, user_collections)

    # Process the `add_collections_form`
    add_collections_form.playlists.choices.extend(available_playlists)
    if add_collections.do(
        spotify_user,
        add_collections_form
    ):
        collections_changed = True

    # Process the `remove_collections_form`
    remove_collections_form.collections.choices.extend(
        [(collection.id, collection.name) for collection in user_collections]
    )
    if remove_collections.do(
        spotify_user,
        remove_collections_form,
    ):
        collections_changed = True

    return collections_changed, user_collections


"""PRIVATE HELPER FUNCTIONS"""


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