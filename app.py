#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from forms import *
from models import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #date = dateutil.parser.parse(value)
  date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Subquery.
#----------------------------------------------------------------------------#

def get_upcoming_shows_subquery(field):
    upcoming_shows = Show.query.with_entities(
      getattr(Show, field).label(field),
      db.func.count(Show.id).label('num_upcoming_shows')) \
      .filter(Show.show_date >= datetime.today()) \
      .group_by(getattr(Show, field)).subquery()

    null_expr = db.case(
        [(upcoming_shows.c.num_upcoming_shows == None, 0)],
        else_ = upcoming_shows.c.num_upcoming_shows)

    return upcoming_shows, null_expr

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  city_venues = {}
  city_state = {}

  upcoming_shows, null_expr = get_upcoming_shows_subquery('venue_id')

  venues = Venue.query.with_entities(
    Venue.id, Venue.name,
    Venue.city, Venue.state_id,
    null_expr.label('num_upcoming_shows')
  ).outerjoin(
    upcoming_shows, Venue.id == upcoming_shows.c.venue_id
  ).order_by('city')

  for ven in venues:
      if ven.city not in city_venues:
         city_venues[ven.city] = []
         city_state[ven.city] = ven.state_id
      city_venues[ven.city].append({'id': ven.id,
            'name':ven.name, 'num_upcoming_shows':ven.num_upcoming_shows})
  data =[]
  for city in city_venues:
      data.append({'city': city, 'state': city_state[city], 'venues':city_venues[city]})
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  upcoming_shows, null_expr = get_upcoming_shows_subquery('venue_id')

  venues = Venue.query.with_entities(
    Venue.id, Venue.name,
    null_expr.label('num_upcoming_shows')
  ).outerjoin(
    upcoming_shows, Venue.id == upcoming_shows.c.venue_id
  ).filter(Venue.name.ilike('%' + request.form.get('search_term', '') + '%'))

  response = {'count': venues.count(), 'data': venues}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.options(
    db.joinedload(Venue.shows).
    subqueryload(Show.artist)).get_or_404(venue_id)

  data.past_shows = []
  data.upcoming_shows = []
  past_shows_count, upcoming_shows_count = 0, 0
  attr = ''
  for show in data.shows:
    if show.show_date >= datetime.today():
        upcoming_shows_count += 1
        attr = 'upcoming_shows'
    else:
        past_shows_count += 1
        attr = 'past_shows'

    getattr(data, attr).append({
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.show_date
    })
  data.past_shows_count = past_shows_count
  data.upcoming_shows_count = upcoming_shows_count
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  if form.validate_on_submit():
      # on successful db insert, flash success
      error = False
      data = {}
      try:
          venue = Venue()
          form.populate_obj(venue)
          #raise Exception('cheking the error hadling')
          db.session.add(venue)
          db.session.commit()
          data['name'] = venue.name
      except:
          error = True
          db.session.rollback()
          print(sys.exc_info())
          flash('Unable to write data!')
          # is it normal not to close session here?
          # return after session.close() leades to "Instance is not bound to a Session;"
          # in QuerySelectField lazy load.
          # http://sqlalche.me/e/bhk3
          return render_template('forms/new_venue.html', form=form)
      finally:
          db.session.close()

      if not error:
          flash('Venue ' + data['name'] + ' was successfully listed!')
          return redirect(url_for('venues'))
  else:
      flash('Check your data!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/<venue_id>', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get_or_404(venue_id)
  if len(venue.shows):
      flash('Unable to remove the venue on which shows are held!')
      return redirect(url_for('show_venue', venue_id = venue_id))
  data = {}
  data['name'] = venue.name
  try:
    venue.genres = []
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + data['name'] + ' has been deleted.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Venue ' + data['name'] + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  upcoming_shows, null_expr = get_upcoming_shows_subquery('artist_id')

  artists = Artist.query.with_entities(
    Artist.id, Artist.name,
    null_expr.label('num_upcoming_shows')
  ).outerjoin(
    upcoming_shows, Artist.id == upcoming_shows.c.artist_id
  ).filter(Artist.name.ilike('%' + request.form.get('search_term', '') + '%'))

  response = {'count': artists.count(), 'data': artists}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  data = Artist.query.get_or_404(artist_id)

  data = Artist.query.options(
    db.joinedload(Artist.shows).
    subqueryload(Show.venue)).get_or_404(artist_id)

  data.past_shows = []
  data.upcoming_shows = []
  past_shows_count, upcoming_shows_count = 0, 0
  attr = ''
  for show in data.shows:
    if show.show_date >= datetime.today():
        upcoming_shows_count += 1
        attr = 'upcoming_shows'
    else:
        past_shows_count += 1
        attr = 'past_shows'

    getattr(data, attr).append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.show_date
    })
  data.past_shows_count = past_shows_count
  data.upcoming_shows_count = upcoming_shows_count

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  if form.validate_on_submit():
      try:
          artist = Artist()
          form.populate_obj(artist)
          db.session.add(artist)
          db.session.commit()
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except:
          db.session.rollback()
          print(sys.exc_info())
          flash('Unable to write data!')
          return render_template('forms/new_artist.html', form=form)
      finally:
          db.session.close()

      return redirect(url_for('artists'))
  else:
      flash('Check your data!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('forms/new_artist.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = Show.query.order_by('show_date').all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  if form.validate_on_submit():
      try:
          show = Show()
          form.populate_obj(show)
          db.session.add(show)
          db.session.commit()
          flash('Show was successfully listed!')
      except:
          db.session.rollback()
          print(sys.exc_info())
          flash('Unable to write data!')
          return render_template('forms/new_show.html', form=form)
      finally:
          db.session.close()

      return redirect(url_for('shows'))
  else:
      flash('Check your data!')
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.env = 'development'
    app.run(host='0.0.0.0', port=5000, debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
