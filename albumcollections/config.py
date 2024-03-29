import os


class Config(object):
    """Config base class"""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'

    SESSION_TYPE = 'sqlalchemy'

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    """This class is used to configure the flask app using
    default settings and environment variable settings for
    use in development
    """
    CACHE_TYPE = 'FileSystemCache'
    CACHE_DIR = './.flask_caching/'
    CACHE_DEFAULT_TIMEOUT = 300

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


class ProdConfig(Config):
    """This class is used to configure the flask app using
    default settings and environment variable settings for
    use in production
    """
    if os.environ.get('DATABASE_URL'):
        # The Database url that heroku provides starts with 'postgres', but sqlalchemy only
        # accepts databases that start with 'postgresql'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace("postgres", "postgresql")

    if os.environ.get('MEMCACHIER_SERVERS'):
        CACHE_TYPE = 'saslmemcached'
        CACHE_DEFAULT_TIMEOUT = 3600  # One hour default timeout for cache items
        CACHE_MEMCACHED_SERVERS = os.environ.get('MEMCACHIER_SERVERS').split(',')
        CACHE_MEMCACHED_USERNAME = os.environ.get('MEMCACHIER_USERNAME')
        CACHE_MEMCACHED_PASSWORD = os.environ.get('MEMCACHIER_PASSWORD')
        CACHE_OPTIONS = {'behaviors': {
            # Faster IO
            'tcp_nodelay': True,
            # Keep connection alive
            'tcp_keepalive': True,
            # Timeout for set/get requests
            'connect_timeout': 2000,  # ms
            'send_timeout': 750 * 1000,  # us
            'receive_timeout': 750 * 1000,  # us
            '_poll_timeout': 2000,  # ms
            # Better failover
            'ketama': True,
            'remove_failed': 1,
            'retry_timeout': 2,
            'dead_timeout': 30
        }}
