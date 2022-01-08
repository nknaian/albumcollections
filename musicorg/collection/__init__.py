"""Handles the album collection webpages"""


from flask import Blueprint

from musicorg import spotify_iface


bp = Blueprint('collection', __name__)


@bp.app_context_processor
def inject_collection_vars():
    return dict(
        get_playlist_albums=spotify_iface.get_playlist_albums
    )


from musicorg.collection import handlers
