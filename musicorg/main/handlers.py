from flask import render_template, redirect, url_for, flash

from . import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')
