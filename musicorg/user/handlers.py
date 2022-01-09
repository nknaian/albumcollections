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


@bp.route('/user/login', methods=['GET', 'POST'])
def login():
    # Attempt to get user id. This will trigger spotify authentication
    # the first time around, and second time have no side effect
    spotify_user.get_user_id()
    
    flash("You are now logged in through your Spotify account!", "success")

    # Send the now logged in user to their collections (playlists)
    return redirect(url_for('user.collections'))


@bp.route('/user/logout', methods=['POST'])
def logout():
    spotify_user.logout()

    flash("You are now logged out.", "warning")

    # Send user back to main page after logging out
    return redirect(url_for('main.index'))


@bp.route('/user/collections', methods=['GET'])
def collections():
    # NOTE: perhaps use caching to avoid requesting from spotify api
    # on every page refresh. But
    # - would be nice if the data were actually cached locally in the user's
    #   browser...that way it's super quick
    #
    # user_playlists = cache.get('user_playlists')
    # if user_playlists is None:
    #     user_playlists = spotify_user.get_user_playlists()
    #     cache.set("user_playlists", user_playlists, timeout=0)

    user_playlists = spotify_user.get_user_playlists()
    return render_template('user/collections.html', user_playlists=user_playlists)


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

    if permission_granted:
        return redirect(url_for('user.login'))
    else:
        return url_for('main.index')


"""EXCEPTION HANDLER ROUTES"""


@bp.app_errorhandler(SpotifyUserAuthFailure)
def handle_external_auth_exception(e):
    return redirect(e.auth_url)
