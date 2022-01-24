from flask import flash, redirect
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
        flash(str(e), "warning")
    elif isinstance(e, albumcollectionsError):
        flash(str(e), "danger")

    if e._redirect_location:
        return redirect(e._redirect_location)
    else:
        return redirect(request.referrer)
