from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, \
    DateTimeField, BooleanField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, AnyOf, URL, Optional
from models import Choice, Genre

def states_choices():
    return Choice.query.order_by('id').all()

def genres_choices():
    return Genre.query.order_by('id').all()

class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
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
        query_factory=states_choices, get_label='name'
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
        'genres', validators=[DataRequired()], query_factory=genres_choices, get_label='name'
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
        query_factory=states_choices, get_label='name'
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
        'genres', validators=[DataRequired()], query_factory=genres_choices, get_label='name'
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
