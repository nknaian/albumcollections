from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.choices import SelectMultipleField


class AddCollectionsForm(FlaskForm):
    available_playlists = SelectMultipleField('Available Playlists', choices=[])
    submit_new_collections = SubmitField('Add')
