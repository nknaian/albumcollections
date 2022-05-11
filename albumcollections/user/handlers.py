from flask import redirect, render_template, url_for, flash, current_app
from flask.globals import request

from albumcollections.errors.exceptions import albumcollectionsError

# Importing like this is necessary for unittest framework to patch
import albumcollections.spotify.spotify_user_interface as spotify_user_iface

from albumcollections.models import User


from albumcollections import db

from . import bp


"""USER INTERFACE ROUTES"""


@bp.route('/user/login', methods=['GET', 'POST'])
def login():
    try:
        return redirect(spotify_user_iface.get_auth_url())
    except Exception as e:
        raise albumcollectionsError(f"Failed to redirect to spotify authorization: {e}", url_for('main.index'))


@bp.route('/user/logout', methods=['POST'])
def logout():
    spotify_user_iface.unauth_user()

    flash("You are now logged out.", "warning")

    # Send user back to main page after logging out
    return redirect(url_for('main.index'))


"""EXTERNAL AUTHENTICATION CALLBACK ROUTES"""


@bp.route('/sp_auth_complete')
def sp_auth_complete():
    """Callback route for spotify authorization"""
    # User granted permission
    if request.args.get("code"):
        # Save their authorization code
        try:
            spotify_user_iface.auth_user(request.args.get("code"))

            spotify_user = spotify_user_iface.SpotifyUserInterface()

            if User.query.filter_by(spotify_user_id=spotify_user.user_id).first() is None:
                db.session.add(User(spotify_user_id=spotify_user.user_id))
                db.session.commit()
                current_app.logger.info(f"Added new user: {spotify_user.display_name}")

            flash(f"Hello {spotify_user.display_name}! You are now logged in through your Spotify account.",
                  "success")
        except Exception as e:
            spotify_user_iface.unauth_user()
            raise albumcollectionsError(f"Failed to authorize spotify account: {e}", url_for('main.index'))

        return render_template(
            'main/load-redirect.html',
            redirect_location=url_for('main.index'),
            load_message="Organizing your shelves..."
        )

    return redirect(url_for('main.index'))
