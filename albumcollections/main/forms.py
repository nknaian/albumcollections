from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.choices import SelectMultipleField


class AddCollectionsForm(FlaskForm):
    playlists = SelectMultipleField('Available Playlists', choices=[])
    submit_new_collections = SubmitField('Add')


class RemoveCollectionsForm(FlaskForm):
    collections = SelectMultipleField(
        'Collections',
        choices=[],
        description="Removes from your album collections account - this will"
                    " NOT remove the underlying spotify playlist!"
    )
    submit_collection_removal = SubmitField('Remove')
