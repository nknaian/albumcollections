from flask import redirect, url_for

from . import bp


@bp.route('/test/fake_sp_auth', methods=["GET", "POST"])
def fake_sp_auth():
    return redirect(url_for('user.sp_auth_complete', code="dummycode"))
