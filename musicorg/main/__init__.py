from flask import Blueprint

from musicorg import cache

bp = Blueprint('main', __name__)


@bp.app_context_processor
def inject_main_vars():
    return dict(
        music_bg_imgs=cache.get("main_music_bg_imgs")
    )


from musicorg.main import handlers
