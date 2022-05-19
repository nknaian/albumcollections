from flask import redirect, render_template, url_for, flash, request, current_app

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.user import is_user_logged_in
from albumcollections.main import collections

from . import bp
from .forms import AddCollectionForm, RemoveCollectionsForm


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
    user_collections = None
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

        # Initialize the forms
        add_collection_form = AddCollectionForm()
        remove_collections_form = RemoveCollectionsForm()

        # Process the user's collections, reloading the page if collections changed
        # If a processing error occurs then unauthenticate the user, as it's likely
        # failure will occur on every retry and create an infinite loop
        try:
            collections_changed, user_collections = collections.process(
                spotify_user, add_collection_form, remove_collections_form
            )
        except collections.RoutineProcessingError as e:
            current_app.logger.critical(f"Failed to process collections for user {spotify_user.display_name}: {e}")
            spotify_user_iface.unauth_user()
            flash("Failed to process collections", "danger")
        else:
            if collections_changed:
                return redirect(url_for('main.index'))

    return render_template(
        'main/index.html',
        user_collections=user_collections,
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
