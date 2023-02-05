from typing import List, Tuple

from flask import url_for, flash, current_app
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField
from wtforms.fields.choices import SelectMultipleField

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface


from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections import collection_playlists


"""EXCEPTIONS"""


class RoutineProcessingError(Exception):
    """Custom exception to denote an error in routine processing of
    the user's collections.
    """
    pass


"""FORMS"""


class AddCollectionForm(FlaskForm):
    playlist = SelectField('Available Playlists', choices=[])
    create_copy = BooleanField('Create an owned copy of this playlist to store as a collection')
    fill_missing_tracks = BooleanField('Fill in missing album tracks while adding as a collection')
    submit_new_collection = SubmitField('Add')


class RemoveCollectionsForm(FlaskForm):
    collections = SelectMultipleField(
        'Collections',
        choices=[],
        description="Removes from your album collections account - this will"
                    " NOT remove the underlying spotify playlist!"
    )
    submit_collection_removal = SubmitField('Remove')


"""FORM PROCESSING FUNCTIONS"""


def process(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    user_playlists: List[SpotifyPlaylist],
    user_collection_playlists: List[SpotifyPlaylist]
) -> Tuple[bool, AddCollectionForm, RemoveCollectionsForm]:
    """rocess the add/remove collection forms

    Return a tuple of:
    - Whether the user's collections were changed during processing of forms
    - The add_collection_form
    - The remove_collection_form
    """
    collections_changed = False
    add_collection_form = AddCollectionForm()
    remove_collections_form = RemoveCollectionsForm()

    # Process the `add_collection_form`
    add_collection_form.playlist.choices.extend(_get_available_playlists(user_playlists, user_collection_playlists))
    if _add_collection(
        spotify_user,
        add_collection_form
    ):
        collections_changed = True

    # Process the `remove_collections_form`
    remove_collections_form.collections.choices.extend(
        [(collection.id, collection.name) for collection in user_collection_playlists]
    )
    if _remove_collections(
        spotify_user,
        remove_collections_form,
    ):
        collections_changed = True

    return collections_changed, add_collection_form, remove_collections_form


"""PRIVATE HELPER FUNCTIONS"""


def _get_available_playlists(
    user_playlists: List[SpotifyPlaylist],
    user_collection_playlists: List[SpotifyPlaylist]
) -> List[Tuple[str, str]]:
    # Don't show playlists that are already displayed as collections as options
    unavaliable_ids = [collection.id for collection in user_collection_playlists]

    return [
        (user_playlist.id, f"{user_playlist.name} by {user_playlist.owner}")
        for user_playlist in user_playlists
        if user_playlist.id not in unavaliable_ids
    ]


def _remove_collections(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    remove_collections_form: RemoveCollectionsForm,
) -> bool:
    """Handle `RemoveCollectionsForm` submission

    - Remove chosen collections from db upon successful form submission.
    - Log and flash error upon failed form submission.

    Returns a boolean value representing whether collections were removed from the database.
    """
    if remove_collections_form.submit_collection_removal.data and remove_collections_form.validate():
        try:
            collection_playlists.remove(spotify_user, remove_collections_form.collections.data)
        except Exception as e:
            raise albumcollectionsError(
                f"Failed to remove collections: {e}", url_for('main.index')
            )
        return True
    elif remove_collections_form.errors:
        current_app.logger.error(
            f'User {spotify_user.display_name} failed to remove collections: {remove_collections_form.errors}'
        )
        flash("Failed to remove collections", "danger")

    return False


def _add_collection(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    add_collection_form: AddCollectionForm,
) -> bool:
    """Handle `AddCollectionForm` submission

    - Initialize collection based on chosen playlist (depending on options in form selected)
    - Add resulting collection to db upon successful form submission.
    - Log and flash error upon failed form submission.

    Returns a boolean value representing whether collections were added to the database.
    """
    if add_collection_form.submit_new_collection.data and add_collection_form.validate():
        try:
            # Initialize the collection based on form options selected
            new_collection_id = _init_collection(
                spotify_user,
                add_collection_form.playlist.data,
                add_collection_form.create_copy.data,
                add_collection_form.fill_missing_tracks.data
            )

            # Add the new collection's id to the db
            collection_playlists.add(spotify_user, new_collection_id)
        except Exception as e:
            raise albumcollectionsError(
                f"Failed to add collection: {e}", url_for('main.index')
            )
        return True
    elif add_collection_form.errors:
        current_app.logger.error(
            f'User {spotify_user.display_name} add collections validate failure: {add_collection_form.errors}'
        )
        flash("Failed to add collections", "danger")

    return False


def _init_collection(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    source_playlist_id: str,
    create_copy: bool,
    fill_missing_tracks: bool
) -> str:
    """Initialize the collection that will be stored.

    - Create a new playlist if the option was specified
    - Fill in missing album tracks if the option was specified
    """
    # If copy was specified, create a copy of the playlist and record the new playlist
    # id as the new collection id
    if create_copy:
        new_collection_id = spotify_user.create_playlist(
            f"{spotify_user.get_playlist(source_playlist_id).name} (albums copy)"
        ).id
    # Otherwise set the new collection id as the id of the form's chosen playlist id
    else:
        new_collection_id = source_playlist_id

    # Initialize playlist tracks based on chosen options in form
    if fill_missing_tracks:
        spotify_user.fill_collection_missing_tracks(
            spotify_user.get_collection(source_playlist_id),
            new_collection_id
        )
    elif create_copy:
        spotify_user.add_items_to_playlist(
            new_collection_id,
            [track.uri for track in spotify_user.get_playlist_tracks(source_playlist_id)]
        )

    return new_collection_id
