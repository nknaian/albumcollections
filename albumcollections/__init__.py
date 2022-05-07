import random
import time
import os
import logging

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_session import Session
from flask_caching import Cache

from albumcollections.spotify import spotipy_cache_handler
from albumcollections.config import DevConfig, ProdConfig


# Create db
db = SQLAlchemy()

# Create cache
cache = Cache()

# Create flask session spotipy cache handler
spotipy_cache_handler = spotipy_cache_handler.FlaskSessionCacheHandler(session)

# Seed random
random.seed(time.time())


def create_app(test_config=None):
    # Create flask application from config
    app = Flask(__name__)

    # Choose from testing, development or production configuration
    if test_config:
        app.config.from_object(test_config)
    elif os.environ.get('FLASK_ENV') and os.environ.get('FLASK_ENV') == "development":
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(ProdConfig)

        # Use gunicorn logger for production
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    # init database
    db.init_app(app)

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

    from albumcollections.pwa import bp as pwa_bp
    app.register_blueprint(pwa_bp)

    if app.config["TESTING"]:
        from albumcollections.test import bp as test_bp
        app.register_blueprint(test_bp)

    # Create bootstrap flask app
    Bootstrap5(app)

    # Create flask session
    app.config['SESSION_SQLALCHEMY'] = db
    Session(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
