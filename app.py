#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

# note this line should be in the models section .. in some cases python linters take all impor lines and add them to the beginning of the file .. if this is the case turn off your linter and take this line back to models section.
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

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
    '''Takes in a number n, returns the square of n'''

    venues = Venue.query.all()
    data = []
    city_state_list = []
    for venue in venues:
        city_state = (venue.city, venue.state)
        if city_state not in city_state_list:
            city_state_list.append(city_state)
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": []
            })
    for venue in venues:
        num_upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        for city_state in data:
            if venue.state == city_state['state'] and venue.city == city_state['city']:
                city_state['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    '''
    function: searches venues for a certain searchterm
    returns: "count": output.count(), "data": output
    '''
    search_term = request.form.get('search_term', '')
    output = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    response = {
        "count": output.count(),
        "data": output
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    '''
    function: returns a venue with a certain id
    arguments : id of the wanted venue
    '''
    current_venue = Venue.query.get(venue_id)
    if not current_venue:
        return render_template('errors/404.html')

    all_comming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
    upcoming_shows = []

    all_past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    past_shows = []

    for show in all_past_shows:
        print(show.artist.name)
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    for x in all_comming_shows:
        print("x")
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    data = {
        "id": venue_id,
        "name": current_venue.name,
        "genres": current_venue.genres,
        "address": current_venue.address,
        "city": current_venue.city,
        "state": current_venue.state,
        "phone": current_venue.phone,
        "website": current_venue.website,
        "facebook_link": current_venue.facebook_link,
        "seeking_talent": current_venue.seeking_talent,
        "seeking_description": current_venue.seeking_description,
        "image_link": current_venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    '''
    function: fetch create form
    returns: html of the
    '''
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    '''function: creates a new venue
    returns: adds new venue to database and renders the home page back
    '''
    error = False
    body = {}

    try:
        form = VenueForm()
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        image_link = request.form['image_link']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        genres = form.genres.data
        seeking_description = form.seeking_description.data
        website = form.website.data
        seeking_talent = form.seeking_talent.data

        venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            image_link=image_link,
            facebook_link=facebook_link,
            genres=genres,
            seeking_description=seeking_description,
            website=website,
            seeking_talent=seeking_talent
        )

        db.session.add(venue)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    '''
    function: deletes a veneue by id
    arguments : id of the deleted venue
    returns: redirects back to index page
    '''
    try:
        # Get venue by ID
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted successfuly')
    except:
        flash('Venue wasnt deleted successfuly')
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    '''
    function: list all artists
    arguments : none
    returns: render the artist's page with fetched data from database
    '''
    artists = Artist.query.all()
    data = []
    for artist in artists:
        data.append({"id": artist.id, "name": artist.name})

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    '''
    function: search artists
    arguments : none
    returns: renders list of artists met the search conditions
    '''
    search_term = request.form.get('search_term', '')
    output = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    response = {
        "count": output.count(),
        "data": output
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    '''
    function: displays a certain artist
    arguments : id of the artist
    returns: renders the artist's page
    '''
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    old_shows_list = []
    comming_shows_list = []
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        show_item = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > datetime.now():
            comming_shows_list.append(show_item)
        else:
            old_shows_list.append(show_item)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": old_shows_list,
        "upcoming_shows": comming_shows_list,
        "past_shows_count": len(old_shows_list),
        "upcoming_shows_count": len(comming_shows_list)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    '''
    function: edits the data of a certain artist
    arguments : id of the artist
    returns: renders the form
    '''
    form = ArtistForm()
    a = Artist.query.get(artist_id)
    artist = {
        "id": a.id,
        "name": a.name,
        "genres": a.genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "facebook_link": a.facebook_link,
        "image_link": a.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    '''
    function: edits the data of a certain artist
    arguments : id of the artist
    returns: renders the artist ppage
    '''
    error = False
    body = {}
    try:
        form = ArtistForm()

        artist = Artist.query.get(artist_id)

        artist.name = request.form['name']
        artist.phone = request.form['phone']
        artist.state = request.form['state']
        artist.city = request.form['city']
        artist.genres = form.genres.data
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']

        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An Error has occured and the update unsuccessful')
    finally:
        db.session.close()

    flash('The Artist ' + request.form['name'] +
          ' has been successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    v = Venue.query.get(venue_id)
    venue = {
        "id": v.id,
        "name": v.name,
        "genres": v.genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link,    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    '''
    function: edits the data of a certain venue
    arguments : id of the venue
    returns: renders the venue ppage
    '''
    error = False
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.genres = form.genres.data
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.image_link = request.form['image_link']
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An Error has occured and the update unsuccessful')
    finally:
        db.session.close()

    flash('The venue ' + request.form['name'] +
          ' has been successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():

    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    '''
    function: creates a new artist
    arguments : none
    returns: renders the home page again
    '''
    error = False
    body = {}
    try:
        form = ArtistForm()

        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        image_link = request.form['image_link']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        genres = form.genres.data

        artist = Artist(name=name,
                        city=city,
                        state=state,
                        phone=phone,
                        image_link=image_link,
                        facebook_link=facebook_link,
                        genres=genres
                        )

        db.session.add(artist)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. artist ' +
              data.name + ' could not be listed.')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('artist ' + request.form['name'] +
              ' was successfully listed!')
        return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    '''
    function: fetch all shows
    arguments : none
    returns: renders the shows page
    '''
    data = []
    shows = Show.query.order_by(db.desc(Show.start_time))
    for show in shows:
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)

        data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    '''
    function: creates a new show
    arguments : none
    returns: renders the home page again
    '''
    error = False
    body = {}
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id,
                    venue_id=venue_id,
                    start_time=format_datetime(str(start_time)))

        db.session.add(show)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('Show was successfully listed!')
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Show wasnt successfully listed!')
        return render_template('pages/home.html')
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
