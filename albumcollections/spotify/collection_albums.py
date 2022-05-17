from typing import List

from .item.spotify_music import SpotifyAlbum


def get(playlist_tracks_iter) -> List[SpotifyAlbum]:
    """Get all valid albums in the given playlist.
    Albums will only be valid if the tracks are in the correct
    sequential order, not separated from eachother by tracks
    from other albums, and only occur once

    NOTE: albums should be returned in the playlist order as long
    as python version is 3.7+ because dictionaries retain insertion
    order
    """
    # Create dictionary to hold albums
    album_entries = {}

    try:
        # Get the first track in playlist
        playlist_track = next(playlist_tracks_iter)

        # Act on the current playlist track in the iterator
        while True:
            # The current playlist track's album hasn't been seen before.
            # Make an entry for the album and iterate through the subsequent
            # playlist tracks
            if playlist_track.album.id not in album_entries:
                # Record the album of this first-encountered track
                album = playlist_track.album

                # Make an entry for this album
                album_entries[album.id] = album

                # Walk through subsequent tracks with the same album id, using disc and track
                # numbers to confirm that the full album is present in the correct order
                last_disc_num = None
                last_track_num = None
                while album.id == playlist_track.album.id:
                    # To start out, the disc number and track number should both be equal to 1
                    if last_disc_num is None and last_track_num is None and \
                            playlist_track.disc_number == 1 and \
                            playlist_track.track_number == 1:
                        pass
                    # If this disc number is equal to last disc number then the track number
                    # should have been incremented by one
                    elif last_disc_num is not None and last_track_num is not None and \
                            last_disc_num == playlist_track.disc_number and \
                            playlist_track.track_number == (last_track_num + 1):
                        pass
                    # If this disc number is one greater than the last disc number, then the
                    # track number should be equal to 1
                    elif last_disc_num is not None and last_track_num is not None and \
                            playlist_track.disc_number == (last_disc_num + 1) and \
                            playlist_track.track_number == 1:
                        pass
                    # Otherwise the current track must be out of order
                    else:
                        break

                    # Set last equal to current
                    last_disc_num = playlist_track.disc_number
                    last_track_num = playlist_track.track_number

                    # Add this track id to the album
                    album.track_ids.append(playlist_track.id)

                    # If all tracks were seen, then mark the album as
                    # complete, move to the next track and break out of the loop
                    if len(album.track_ids) == album.total_tracks:
                        album.complete = True
                        playlist_track = next(playlist_tracks_iter)
                        break
                    # Otherwise the album isn't complete yet so stay in the loop
                    # and iterate to the next track in the playlist
                    else:
                        playlist_track = next(playlist_tracks_iter)

            # The current playlist track's album has been seen before. This means that
            # the track is either a duplicate, or separated from the first track in
            # the album by tracks from other albums. In any case, it means that the
            # complete album isn't present in the playlist
            else:
                album_entries[playlist_track.album.id].complete = False
                playlist_track = next(playlist_tracks_iter)

    # If a stop iteration is received, that means the playlist's tracks have been
    # exhausted - pencils down.
    except StopIteration:
        pass

    # Return albums from valid entries
    return list(album_entries.values())
