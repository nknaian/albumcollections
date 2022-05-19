from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, BooleanField
from wtforms.fields.choices import SelectMultipleField


class AddCollectionForm(FlaskForm):
    playlist = SelectField('Available Playlists', choices=[])
    create_copy = BooleanField('Create an owned copy of this playlist to store as a collection')
    fill_missing_tracks = BooleanField('Fill in missing album tracks while adding as a collection')
    submit_new_collection = SubmitField('Add')


class RemoveCollectionsForm(FlaskForm):
    collections = SelectMultipleField(
        'Collections',
        choices=[],
        description="Removes from your album collections account - this will"
                    " NOT remove the underlying spotify playlist!"
    )
    submit_collection_removal = SubmitField('Remove')
