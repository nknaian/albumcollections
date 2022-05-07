from flask import Blueprint

from albumcollections import cache

bp = Blueprint('main', __name__)


"""JINJA VARIABLE INJECTION"""


@bp.app_context_processor
def inject_user_vars():
    return dict(
        choices_display_len=choices_display_len
    )


"""PUBLIC FUNCTIONS"""


def choices_display_len(num_choices: int) -> int:
    return num_choices if num_choices < 10 else 10


from albumcollections.main import handlers
