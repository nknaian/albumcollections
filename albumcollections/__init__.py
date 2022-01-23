import random
import time

from flask import Flask, session
from flask_bootstrap import Bootstrap
from flask_session import Session
from flask_caching import Cache

from albumcollections.spotify.spotify import Spotify
from albumcollections.spotify import spotipy_cache_handler
from albumcollections.config import Config


# Create cache
cache = Cache()

# Create 'client credentials' spotify interface
spotify_iface = Spotify()

# Create flask session spotipy cache handler
spoipy_cache_handler = spotipy_cache_handler.FlaskSessionCacheHandler(session)

# Seed random
random.seed(time.time())


def create_app(config_class=Config):
    # Create flask application from config
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize spotify as long as we're not testing
    if not app.config["TESTING"]:
        spotify_iface.init_sp()

    # Initialize cache
    cache.init_app(app)

    # Register blueprints
    from albumcollections.main import bp as main_bp
    app.register_blueprint(main_bp)

    from albumcollections.user import bp as user_bp
    app.register_blueprint(user_bp)

    from albumcollections.collection import bp as collection_bp
    app.register_blueprint(collection_bp)

    from albumcollections.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    if app.config["TESTING"]:
        from albumcollections.test import bp as test_bp
        app.register_blueprint(test_bp)

    # Create bootstrap flask app
    Bootstrap(app)

    # Create flask session
    Session(app)

    return app
