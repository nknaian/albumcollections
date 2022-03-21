from requests.exceptions import ConnectionError

from albumcollections.spotify import spotify_user

"""PUBLIC FUNCTIONS"""


def is_user_logged_in() -> bool:
    # Check if user is currently authenticated with spotify
    try:
        auth = spotify_user.is_authenticated()
    except ConnectionError:
        print("Connection error while checking if user logged in")
        auth = False
    except Exception as e:
        print(f"Exceptino while checking if user logged in: {e}")
        auth = False

    return auth
