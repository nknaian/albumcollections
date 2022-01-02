from importlib import import_module
from typing import Dict
from urllib.parse import urlparse

from flask import redirect, render_template, url_for, flash
from flask.globals import request, session

from musicorg.spotify import spotify_user
from musicorg.database.models import Round
from musicorg.database.helpers import lookup_user_in_db
from musicorg.enums import MusicType
from musicorg.spotify.spotify_user import SpotifyUserAuthFailure
from musicorg.errors.exceptions import musicorgError

from musicorg import spotify_iface

from . import bp
from .helpers import login_or_register_user


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

    login_or_register_user()

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


@bp.route('/create_category', methods=['GET', 'POST'])
def create_category():
    new_category_form = NewCategoryForm()

    if new_category_form.validate_on_submit():
        # Add the category to the database
        create_category = add_category_to_db(new_category_form.description.data,
                                       new_category_form.music_type.data,
                                       new_category_form.snoozin_rec_type.data)

        # Go to the page for the new category
        return redirect(url_for('category.index', long_id=create_category.long_id))

    elif new_category_form.errors:
        flash("There were errors in your new category submission", "warning")

    return render_template('main/create_category.html', new_category_form=new_category_form)


@bp.route('/user/rounds')
def rounds():
    def created_datetime(round_music_subs):
        return round_music_subs[0].created

    # Get music type from args
    music_type = request.args.get("music_type")
    if music_type not in ['track', 'album']:
        raise musicorgError(f'{music_type} is not a valid music type.')

    user = lookup_user_in_db(spotify_user.get_user_id())

    # Construct list of tuples with the rounds the user has submitted to,
    # with the music that they submitted to that round
    round_music_subs = set()
    for submission in user.submissions:
        round = Round.query.filter_by(id=submission.round_id).first()

        if round.music_type == MusicType[music_type]:
            round_music_subs.add((
                round,
                spotify_iface.get_music_from_link(round.music_type, submission.spotify_link)
            ))

    return render_template('user/rounds.html',
                           music_type=music_type,
                           round_music_subs=reversed(sorted(list(round_music_subs), key=created_datetime)))


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
