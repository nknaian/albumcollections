import os


class DevConfig(object):
    """This class is used to configure the flask app using
    default settings and environment variable settings for
    use in development
    """
    CACHE_TYPE = 'FileSystemCache'
    CACHE_DIR = './.flask_caching/'
    CACHE_DEFAULT_TIMEOUT = 300

    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'


class ProdConfig(object):
    """This class is used to configure the flask app using
    default settings and environment variable settings for
    use in production
    """

    # NOTE: I'm not sure how, but this seems to be working in production on heroku
    # I thought that because the filesystem isn't writable it wouldn't work...
    # When logging in w/ bash to the system I can't find the ".flask_session" folder
    # anywhere, but somehow the session dictionary seems to be functioning
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './.flask_session/'
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'

    if os.environ.get('MEMCACHIER_SERVERS'):
        CACHE_TYPE = 'saslmemcached'
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
