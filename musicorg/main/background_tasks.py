import random

from musicorg.spotify.item.spotify_music import SpotifyTrack
from musicorg.database.models import Round
from musicorg.enums import MusicType, RoundStatus

from musicorg import spotify_iface, scheduler, cache


'''CONSTANTS'''


# This is to create a 5 x 10 grid of imgs
MAX_BG_IMGS = 50


'''TASKS'''


@scheduler.task(
    "cron",
    id="update_bg_imgs",
    day="*",
    max_instances=1
)
def update_bg_imgs():
    """Update the images that are displayed on the main pages to a random
    selection of recent rounds.

    Schedule to occur once a day.
    """
    with scheduler.app.app_context():
        # Creat empty set to store images
        music_bg_imgs = set()

        # Get revealed rounds
        rounds = Round.query.filter_by(status=RoundStatus.revealed)

        # Get imgs from recent revealed rounds
        for round in reversed(list(rounds)):
            # Get subs that aren't snoozin's (we're interested in what actual ppl are recommending!)
            snoozinless_subs = [sub for sub in round.submissions if sub.user_name != "snoozin"]

            # Skip if round has less than two subs (means someone played alone with snoozin, so
            # not really recommending to anyone now are you?)
            if len(snoozinless_subs) < 2:
                continue

            # Get high quality imgs (obtained from album query) for two of the submissions for this round
            for sub in random.sample(snoozinless_subs, 2):
                music = spotify_iface.get_music_from_link(round.music_type, sub.spotify_link)

                if isinstance(music, SpotifyTrack):
                    img_url = spotify_iface.get_music_from_link(MusicType.album, music.album_item.link).img_url
                else:
                    img_url = music.img_url

                music_bg_imgs.add(img_url)

            # Exit once we have enough images
            if len(music_bg_imgs) >= MAX_BG_IMGS:
                break

        # Make a shuffled list of the images
        music_bg_imgs = list(music_bg_imgs)
        random.shuffle(music_bg_imgs)

        # Save the list of images to the cache
        cache.set("main_music_bg_imgs", music_bg_imgs, timeout=0)
