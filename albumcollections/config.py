import os


class Config(object):
    """This class is used to configure the flask app using
    default settings and environment variable settings
    """
    CACHE_TYPE = 'FileSystemCache'
    CACHE_DIR = './.flask_caching/'
    CACHE_DEFAULT_TIMEOUT = 300

    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
