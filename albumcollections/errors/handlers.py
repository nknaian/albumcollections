from flask import flash, redirect, current_app, url_for
from flask.globals import request

from . import bp
from .exceptions import albumcollectionsException, albumcollectionsError, albumcollectionsAlert


@bp.app_errorhandler(albumcollectionsException)
def handle_user_errors(e):
    """If a albumcollectionsException, then flash the exception message
    and redirect the user to the appropriate page.

    - Alerts will be in the "warning" color, meant as a notice for users to
      be aware of.
    - Errors will be in the "danger" color, with the text 'Internal Error'
      prepended. These should never happen, and the user should know that it
      is internal...it is not their fault.
    """
    if isinstance(e, albumcollectionsAlert):
        current_app.logger.warn(f"User alert: {e}")
        flash(str(e), "warning")
    elif isinstance(e, albumcollectionsError):
        current_app.logger.error(f"User error: {e}")
        flash(str(e), "danger")

    if e._redirect_location:
        return redirect(e._redirect_location)
    else:
        return redirect(request.referrer)


@bp.app_errorhandler(Exception)
def handle_base_exception(e):
    current_app.logger.critical(f"Base exception encountered: {e}")
    flash("Unexpected failure occurred", "danger")

    if request.referrer is None:
        return redirect(url_for('main.index'))
    else:
        return redirect(request.referrer)
