from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired
from musicorg.enums import SnoozinRecType, MusicType


class NewCategoryForm(FlaskForm):
    name = StringField('Name of the category', validators=[DataRequired()])
    submit = SubmitField('Create Category')


class AddAlbumToCategoryForm(FlaskForm):
    # NOTE: The below field is not meant to be visible...just filled in
    # based on the current album selected to add.
    # NOTE: THe process of adding an album to a category should be really quick
    # I'm actually not even sure that a form is the right option because of the
    # reload that would happen. Probably a javascript comm would be the right thing??
    album_id = IntegerField('Album id', validators=[DataRequired()])
    category_id = SelectField(
        'Which category?,
        choices=SnoozinRecType.choices(),  # not sure how I'd do this corece thing w/ database
        coerce=SnoozinRecType.coerce
    )
    submit = SubmitField('Create Album')
