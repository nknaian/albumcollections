from typing import List, Tuple
from flask import flash, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
from albumcollections.main import add_collection, remove_collections
from albumcollections.models import Collection
from albumcollections.user import get_user_id, get_user_playback_playlist_id

from albumcollections import db

from .forms import AddCollectionForm, RemoveCollectionsForm


class RoutineProcessingError(Exception):
    """Custom exception to denote an error in routine processing of
    the user's collections.
    """
    pass


def process(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    add_collection_form: AddCollectionForm,
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
        raise RoutineProcessingError(f"Failed to get collections: {e}")

    # Get the available playlists from the user's account that could be added as collections
    try:
        available_playlists = _get_available_playlists(user_playlists, user_collections)
    except Exception as e:
        raise RoutineProcessingError(f"Falied to filter available playlists: {e}")

    # Process the `add_collection_form`
    add_collection_form.playlist.choices.extend(available_playlists)
    if add_collection.do(
        spotify_user,
        add_collection_form
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
    # Make dictionary of user playlists w/ ids as keys
    user_playlist_dict = {user_playlist.id: user_playlist for user_playlist in user_playlists}

    # Get the user's playlists that have been stored as collections
    user_collections = []
    for collection in Collection.query.filter_by(user_id=get_user_id()):
        if collection.playlist_id in user_playlist_dict:
            user_collections.append(user_playlist_dict[collection.playlist_id])
        else:
            # If the stored collection is not present in the user's collections
            # then remove it
            db.session.delete(collection)
            db.session.commit()

    return user_collections


def _get_available_playlists(
    user_playlists: List[SpotifyPlaylist],
    user_collections: List[SpotifyPlaylist]
) -> List[Tuple[str, str]]:
    # Don't show playlists that are already displayed as collections as options
    unavaliable_ids = [collection.id for collection in user_collections]

    # Don't show the user playback playlist as an option
    unavaliable_ids.append(get_user_playback_playlist_id())

    return [
        (user_playlist.id, f"{user_playlist.name} by {user_playlist.owner}")
        for user_playlist in user_playlists
        if user_playlist.id not in unavaliable_ids
    ]
