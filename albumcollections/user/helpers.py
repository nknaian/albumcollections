from albumcollections.spotify import spotify_user

"""PUBLIC FUNCTIONS"""


def is_user_logged_in() -> bool:
    # Check if user is currently authenticated with spotify
    return spotify_user.is_authenticated()
