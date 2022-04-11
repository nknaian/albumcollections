from flask import redirect, render_template, url_for, flash
from flask.globals import request

from spotipy.exceptions import SpotifyException

from albumcollections.errors.exceptions import albumcollectionsError
from albumcollections.spotify import spotify_user
from albumcollections.spotify.spotify_user import SpotifyUserAuthFailure
from albumcollections.models import User


from albumcollections import db

from . import bp


"""USER INTERFACE ROUTES"""


@bp.route('/user/login', methods=['GET', 'POST'])
def login():
    # Attempt to get user id. This will trigger spotify authentication
    # the first time around, and second time have no side effect
    try:
        spotify_user_id = spotify_user.get_user_id()

    except SpotifyException as e:
        spotify_user.logout()
        raise albumcollectionsError(f"Failed to authenticate with spotify\n{e}", url_for('main.index'))

    # Add user to database if they don't exist already
    try:
        if User.query.filter_by(spotify_user_id=spotify_user_id).first() is None:
            db.session.add(User(spotify_user_id=spotify_user_id))
            db.session.commit()
    except Exception as e:
        spotify_user.logout()
        raise albumcollectionsError(f"Failed add user to database\n{e}", url_for('main.index'))

    flash(f"Hello {spotify_user.get_user_display_name()}! You are now logged in through your Spotify account.",
          "success")

    return render_template(
        'main/load-redirect.html',
        redirect_location=url_for('main.index'),
        load_message="Organizing your shelves..."
    )


@bp.route('/user/logout', methods=['POST'])
def logout():
    spotify_user.logout()

    flash("You are now logged out.", "warning")

    # Send user back to main page after logging out
    return redirect(url_for('main.index'))


"""EXTERNAL AUTHENTICATION CALLBACK ROUTES"""


@bp.route('/sp_auth_complete')
def sp_auth_complete():
    """Callback route for spotify authorization"""

    permission_granted = False

    # User granted permission
    if request.args.get("code"):
        permission_granted = True

        # Save their authorization code
        try:
            spotify_user.auth_new_user(request.args.get("code"))
        except SpotifyException as e:
            spotify_user.logout()
            raise albumcollectionsError(f"Failed to login\n{e}", url_for('main.index'))

    if permission_granted:
        return redirect(url_for('user.login'))
    else:
        return redirect(url_for('main.index'))


"""EXCEPTION HANDLER ROUTES"""


@bp.app_errorhandler(SpotifyUserAuthFailure)
def handle_external_auth_exception(e):
    return redirect(e.auth_url)
