from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, \
    DateTimeField, BooleanField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, AnyOf, URL, Optional
import models

def get_model_choices(model_name):
    return getattr(models, model_name).query.order_by('name').all()

class ShowForm(Form):
    artist = QuerySelectField(
        'artist', validators=[DataRequired()],
        query_factory=lambda: get_model_choices('Artist'), get_label='name'
    )
    venue = QuerySelectField(
        'venue', validators=[DataRequired()],
        query_factory=lambda: get_model_choices('Venue'), get_label='name'
    )
    show_date = DateTimeField(
        'show_date',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = QuerySelectField(
        # TODO emplemetn data required
        'state', validators=[DataRequired()],
        query_factory=lambda: get_model_choices('Choice'), get_label='name'
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link', validators=[Optional(), URL()]
    )
    genres = QuerySelectMultipleField(
        # TODO implement enum restriction data required
        'genres', validators=[DataRequired()],
        query_factory=lambda: get_model_choices('Genre'), get_label='name'
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    website = StringField(
        'website', validators=[Optional(), URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talnet'
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = QuerySelectField(
        'state', validators=[DataRequired()],
        query_factory=lambda: get_model_choices('Choice'), get_label='name'
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link', validators=[Optional(), URL()]
    )
    genres = QuerySelectMultipleField(
        # TODO implement enum restriction data required
        'genres', validators=[DataRequired()],
        query_factory=lambda: get_model_choices('Genre'), get_label='name'
    )
    facebook_link = StringField(
        'facebook_link', validators=[Optional(), URL()]
    )
    website = StringField(
        'website', validators=[Optional(), URL()]
    )
    seeking_venue = BooleanField(
        'seeking_talnet'
    )
    seeking_description = TextAreaField(
        'seeking_description'
    )

# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
