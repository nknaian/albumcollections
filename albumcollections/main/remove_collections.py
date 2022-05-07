from typing import List

from flask import url_for, flash, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.models import Collection
from albumcollections.user import get_user_id

from albumcollections import db

from .forms import RemoveCollectionsForm


def do(
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
            _remove_choices_from_db(spotify_user, remove_collections_form.collections.data)
        except Exception as e:
            raise albumcollectionsError(
                f"{spotify_user.display_name} failed to remove collections: {e}", url_for('main.index')
            )
        return True
    elif remove_collections_form.errors:
        current_app.logger.error(
            f'User {spotify_user.display_name} failed to remove collections: {remove_collections_form.errors}'
        )
        flash("Failed to remove collections", "danger")

    return False


def _remove_choices_from_db(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    collection_id_choices: List[str]
):
    """Remove user's chosen collections from their Collections in the database"""
    for chosen_collection_id in collection_id_choices:
        collection = Collection.query.filter_by(playlist_id=chosen_collection_id, user_id=get_user_id()).first()
        if collection is None:
            raise Exception(f"'{chosen_collection_id}' not found")
        else:
            db.session.delete(collection)
            db.session.commit()
            current_app.logger.info(
                f'User {spotify_user.display_name}'
                f' removed collection: {chosen_collection_id}'
            )
