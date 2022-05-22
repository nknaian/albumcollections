from flask import url_for, flash, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface
from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.models import Collection
from albumcollections.user import get_user_id

from albumcollections import db

from .forms import AddCollectionForm


def do(
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
            _add_choice_to_db(spotify_user, new_collection_id)
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


def _add_choice_to_db(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    new_collection_id: str
):
    """Add new collection id to their Collections in the database"""
    if Collection.query.filter_by(playlist_id=new_collection_id, user_id=get_user_id()).first():
        raise Exception(f"'{new_collection_id}' already imported as a collection")
    else:
        db.session.add(Collection(playlist_id=new_collection_id, user_id=get_user_id()))
        db.session.commit()
        current_app.logger.info(
            f'User {spotify_user.display_name} added collection: {new_collection_id}'
        )
