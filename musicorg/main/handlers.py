from flask import render_template, redirect, url_for, flash

from musicorg.spotify.item.spotify_music import SpotifyAlbum
from musicorg.spotify import spotify_user

from musicorg import cache, spotify_iface

from . import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')


@bp.route('/about', methods=['GET'])
def about():
    return render_template('main/about.html')
