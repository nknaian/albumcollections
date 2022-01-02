from flask import render_template, redirect, url_for, flash


from musicorg.database.helpers import add_round_to_db

from . import bp
from .forms import NewRoundForm


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')


@bp.route('/about', methods=['GET'])
def about():
    return render_template('main/about.html')
