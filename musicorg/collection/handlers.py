from flask import render_template

from . import bp


@bp.route('/collection/<string:playlist_id>', methods=['GET'])
def index(playlist_id):
    return render_template('collection/index.html', playlist_id=playlist_id)
