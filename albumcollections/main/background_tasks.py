import random

from albumcollections.spotify.item.spotify_music import SpotifyAlbum
from albumcollections.enums import MusicType, RoundStatus

from albumcollections import spotify_iface, scheduler, cache


'''CONSTANTS'''


# This is to create a 5 x 10 grid of imgs
NUM_BG_IMGS = 50


'''TASKS'''


@scheduler.task(
    "cron",
    id="update_bg_imgs",
    hour="*",
    max_instances=1
)
def update_bg_imgs():
    """Update the images that are displayed on the main pages to
    spotify's 'new releases.

    Schedule to occur once per hour.
    """
    with scheduler.app.app_context():
        sp_albums = spotify_iface.sp.new_releases(limit=NUM_BG_IMGS)["albums"]["items"]

        album_imgs = [SpotifyAlbum(sp_album).img_url for sp_album in sp_albums]

        # Save the list of images to the cache
        cache.set("main_music_bg_imgs", album_imgs, timeout=0)
