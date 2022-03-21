from typing import List

from albumcollections.spotify.item.spotify_collection import SpotifyCollection
from albumcollections.spotify.item.spotify_music import SpotifyAlbum


class TestSpotifyCollection(SpotifyCollection):
    """A mock spotify collection for situations where interfacing with
    the spotify api is not possible
    """
    def __init__(self):
        super().__init__(
            {
                "id": "test",
                "uri": "Spotify:Album:test",
                "name": "This is a test collection, for use when offline",
                "snapshot_id": None,
                "images": []
            }
        )

    @property
    def albums(self) -> List[SpotifyAlbum]:
        return [
            SpotifyAlbum(
                {
                    "id": "test",
                    "uri": "Spotify:Album:test",
                    "name": "Test album 1",
                    "artists": [
                        {
                            "id": "test",
                            "uri": "Spotify:Artist:test",
                            "name": "Test Artist"
                        }
                    ],
                    "release_date": None,
                    "album_type": "album",
                    "total_tracks": 0,
                    "images": []
                }
            )
        ]
