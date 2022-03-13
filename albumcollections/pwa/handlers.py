from flask import send_from_directory, make_response

from . import bp


@bp.route('/manifest.json')
def manifest():
    print("manifest!")
    return send_from_directory('static', 'manifest.json')


@bp.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response
