from importlib import import_module
from typing import Dict
from urllib.parse import urlparse

from flask import redirect, render_template, url_for, flash
from flask.globals import request, session

from musicorg.spotify import spotify_user
from musicorg.spotify.spotify_user import SpotifyUserAuthFailure
from musicorg.errors.exceptions import musicorgError

from musicorg import spotify_iface, cache

from . import bp



"""USER INTERFACE ROUTES"""


@bp.route('/user/profile', methods=['GET', 'POST'])
def profile():
    return render_template('user/profile.html')


@bp.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.args.get("next"):
        next = request.args.get("next")
    else:
        next = request.referrer

    spotify_user.get_user_id()
    
    flash("You are now logged in through your Spotify account!", "success")

    return redirect(next)


@bp.route('/user/logout', methods=['POST'])
def logout():
    spotify_user.logout()

    flash("You are now logged out.", "warning")

    # If the referrer is a user page, then redirect to main
    if urlparse(request.referrer).path.split("/")[1] == "user":
        next = url_for('main.index')
    # Otherwise, go back to the page the user was on
    else:
        next = request.referrer

    return redirect(next)


@bp.route('/user/playlists', methods=['GET'])
def playlists():
    user_playlists = cache.get('user_playlists')
    if user_playlists is None:
        user_playlists = spotify_user.get_user_playlists()
        cache.set("user_playlists", user_playlists)

    return render_template('user/playlists.html', user_playlists=user_playlists)


@bp.route('/user/playlist/<string:playlist_id>', methods=['GET'])
def playlist(playlist_id):
    return render_template('user/playlist.html', playlist_id=playlist_id)


"""EXTERNAL AUTHENTICATION CALLBACK ROUTES"""


@bp.route('/sp_auth_complete')
def sp_auth_complete():
    """Callback route for spotify authorization"""

    permission_granted = False

    # User granted permission
    if request.args.get("code"):
        permission_granted = True

        # Save their authorization code
        spotify_user.auth_new_user(request.args.get("code"))

        # Call the recovered function
        retry_func_info = session.get("user_retry_func_info", None)
        if retry_func_info:
            _call_retry_func(retry_func_info)

    # Set next url to original referrer url.
    if "user_referrer_url" in session and \
            session["user_referrer_url"] is not None:
        destination_url = session["user_referrer_url"]
    # If it wasn't set, just redirect to main index
    else:
        destination_url = url_for('main.index')

    # Clear all external auth session data
    if "user_referrer_url" in session:
        session.pop("user_referrer_url")
    if "user_retry_func_info" in session:
        session.pop("user_retry_func_info")

    if permission_granted:
        return redirect(url_for('user.login', next=destination_url))
    else:
        return redirect(destination_url)


"""EXCEPTION HANDLER ROUTES"""


@bp.app_errorhandler(SpotifyUserAuthFailure)
def handle_external_auth_exception(e):
    # Save the referrer url before redirecting to the auth url,
    # so that the original user location can be recovered and
    # redirected back to after authentication is complete
    session["user_referrer_url"] = request.referrer
    return redirect(e.auth_url)


"""PRIVATE FUNCTIONS"""


def _call_retry_func(func_info: Dict):
    """Get the function that needs to be retried and then call it
    """
    func_module = import_module(func_info["module"])
    func = getattr(func_module, func_info["qualname"])
    func(*func_info["args"], **func_info["kwargs"])
