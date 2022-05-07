from typing import List

from flask import url_for, flash, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface
from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.models import Collection
from albumcollections.user import get_user_id

from albumcollections import db

from .forms import AddCollectionsForm


def do(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    add_collections_form: AddCollectionsForm,
) -> bool:
    """Handle `AddCollectionsForm` submission

    - Add chosen playlists as collections to db upon successful form submission.
    - Log and flash error upon failed form submission.

    Returns a boolean value representing whether collections were added to the database.
    """
    if add_collections_form.submit_new_collections.data and add_collections_form.validate():
        try:
            _add_choices_to_db(spotify_user, add_collections_form.playlists.data)
        except Exception as e:
            raise albumcollectionsError(
                f"{spotify_user.display_name} failed to add collections: {e}", url_for('main.index')
            )
        return True
    elif add_collections_form.errors:
        current_app.logger.error(
            f'User {spotify_user.display_name} add collections validate failure: {add_collections_form.errors}'
        )
        flash("Failed to add collections", "danger")

    return False


def _add_choices_to_db(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    playlist_id_choices: List[str]
):
    """Add user's chosen playlists to their Collections in the database"""
    for chosen_playlist_id in playlist_id_choices:
        if Collection.query.filter_by(playlist_id=chosen_playlist_id, user_id=get_user_id()).first():
            raise Exception(f"'{chosen_playlist_id}' already imported as a collection")
        else:
            db.session.add(Collection(playlist_id=chosen_playlist_id, user_id=get_user_id()))
            db.session.commit()
            current_app.logger.info(
                f'User {spotify_user.display_name} added collection: {chosen_playlist_id}'
            )
