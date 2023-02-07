# Interface for user's collections and underlying spotify playlists

from typing import List, Tuple

from flask import current_app, flash

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.spotify.item.spotify_playlist import SpotifyPlaylist
from albumcollections.models import Collection
from albumcollections.user import get_user_id
from albumcollections import db


"""PUBLIC FUNCTIONS"""


def load(spotify_user: spotify_user_iface.SpotifyUserInterface) -> Tuple[List[SpotifyPlaylist], List[SpotifyPlaylist]]:
    """Load the user's playlists - both those saved as collections in the app and overall playlists.
    """

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

    # Make dictionary of user playlists w/ ids as keys
    user_playlist_dict = {user_playlist.id: user_playlist for user_playlist in user_playlists}

    # Get the user's playlists that have been stored as collections
    user_collection_playlists = []
    for collection in Collection.query.filter_by(user_id=get_user_id()):
        if collection.playlist_id in user_playlist_dict:
            user_collection_playlists.append(user_playlist_dict[collection.playlist_id])
        else:
            # If the stored collection is not present in the user's collections
            # then remove it
            db.session.delete(collection)
            db.session.commit()

    return user_collection_playlists, user_playlists


def add(
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


def remove(
    spotify_user: spotify_user_iface.SpotifyUserInterface,
    collection_ids: List[str]
):
    """Remove collection ids from user's Collections in the database"""
    for chosen_collection_id in collection_ids:
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
