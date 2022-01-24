from spotipy.cache_handler import CacheHandler


class FlaskSessionCacheHandler(CacheHandler):
    """Flask-Session handler for spotipy"""

    def __init__(self, flask_session) -> None:
        self.flask_session = flask_session

    def get_cached_token(self):
        return self.flask_session.get('flask_session_cache_token')

    def save_token_to_cache(self, token_info):
        self.flask_session['flask_session_cache_token'] = token_info

    def remove_cached_token(self):
        self.flask_session.pop('flask_session_cache_token', None)
