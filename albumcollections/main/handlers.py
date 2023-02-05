from flask import redirect, render_template, url_for, flash, request, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.user import is_user_logged_in
from albumcollections import collection_playlists

from . import bp, forms


"""HANDLER FUNCTIONS"""


@bp.route('/', methods=['GET', 'POST'])
def index():
    """If a user is unauthenticated with Spotify when they visit this route it
    is a very simple page, just a launcher with text and a button
    to log in with Spotify

    Otherwise this page displays the user's collections from a high level, giving
    them the ability to add/remove them using multi-select forms.

    This route is the destination of many errors
    """
    user_collection_playlists = None
    add_collection_form = None
    remove_collections_form = None

    if is_user_logged_in():
        # Get the spotify user that is logged in
        try:
            spotify_user = spotify_user_iface.SpotifyUserInterface()
        except Exception as e:
            current_app.logger.critical(f"Failed to create spotify user interface: {e}")
            spotify_user_iface.unauth_user()
            flash("Failed to create Spotify user interface", "danger")

        # Load the user's playlists
        # If an error occurs then unauthenticate the user, as it's likely
        # failure will occur on every retry and create an infinite loop
        try:
            user_collection_playlists, user_playlists = collection_playlists.load(spotify_user)
        except Exception as e:
            current_app.logger.critical(f"Failed to load collections for {spotify_user.display_name}: {e}")
            spotify_user_iface.unauth_user()
            flash("Failed to load collections", "danger")

        # Process the collection forms, reloading if collections changed
        collection_changed, add_collection_form, remove_collections_form = forms.process(
            spotify_user, user_playlists, user_collection_playlists)
        if collection_changed:
            return redirect(url_for('main.index'))

    return render_template(
        'main/index.html',
        user_collection_playlists=user_collection_playlists,
        add_collection_form=add_collection_form,
        remove_collections_form=remove_collections_form,
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
