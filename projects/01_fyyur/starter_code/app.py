#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from models import *
from sqlalchemy import or_
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
        if format == 'full':
            format = "EEEE MMMM, d, y 'at' h:mma"
        elif format == 'medium':
            format = "EE MM, dd, y h:mma"
        return babel.dates.format_datetime(date, format, locale='en')
    else:
        date = value


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# Home
# ----------------------------------------------------------------


@app.route('/')
def index():
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()

    return render_template('pages/home.html', venues=venues, artists=artists)


#  Venues
#  ----------------------------------------------------------------

# ***** Create a New Venue *****

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)

    if form.validate_on_submit():
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=request.form.getlist('genres'),
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            print(venue)

            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash(
                f'Venue {form.name.data} was successfully listed!', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash(
                f'An error occurred. Venue {form.name.data} could not be listed!', 'danger')
            return render_template('forms/new_venue.html', form=form)
        finally:
            db.session.close()
    else:
        flash(
            f'An error occurred. Venue {form.name.data} could not be listed!', 'danger')
        return render_template('forms/new_venue.html', form=form)

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


# ***** Get All Venues *****

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    # Get the distinct values for city and state
    venues = Venue.query.distinct(Venue.city, Venue.state).all()

    all_data = []

    for venue in venues:
        venue_data = {
            'city': venue.city,
            'state': venue.state
        }
        # print('Venue Data: ', venue_data)

        # Get the shows for each venue, then filter the shows to get the number of upcoming shows
        venue_shows = venue.shows
        upcoming_shows = [
            *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') >=
                    str(datetime.today()), venue_shows)]
        num_of_upcoming_shows = len(upcoming_shows)

        # filter the database using the distinct city and state
        res = Venue.query.filter_by(city=venue.city, state=venue.state).all()

        venue_details = []

        for data in res:
            venue_details.append({
                'id': data.id,
                'name': data.name,
                'num_upcoming_shows': num_of_upcoming_shows
            })

        venue_data['venues'] = venue_details
        all_data.append(venue_data)
        # print(all_data)
    return render_template('pages/venues.html', areas=all_data)

# ***** Search Venue *****


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(or_(
        Venue.name.ilike(f'%{search_term}%'),
        Venue.city.ilike(f'{search_term}'),
        Venue.state.ilike(f'{search_term}')
    )).all()

    data = []

    for venue in venues:
        upcoming_shows = [
            *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') >=
                    str(datetime.today()), venue.shows)]

        data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(upcoming_shows)
        })
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# ***** Get a Single Venue by ID *****


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get_or_404(venue_id)

    venue_shows = venue.shows
    upcoming_show_artist_details = []
    past_show_artist_details = []

    upcoming_shows = [
        *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') >=
                str(datetime.today()), venue_shows)]

    past_shows = [
        *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') <
                str(datetime.today()), venue_shows)]

    setattr(venue, 'upcoming_shows', upcoming_shows)
    setattr(venue, 'upcoming_shows_count', len(upcoming_shows))
    setattr(venue, 'past_shows', past_shows)
    setattr(venue, 'past_shows_count', len(past_shows))

    for show in venue.upcoming_shows:
        artist_details = {}

        artist_details['artist_id'] = show.artist_id
        artist_details['artist_name'] = show.artists.name
        artist_details['artist_image_link'] = show.artists.image_link
        artist_details['start_time'] = show.start_time.strftime(
            '%Y-%m-%d %H:%M:%S')

        upcoming_show_artist_details.append(artist_details)

    venue.upcoming_shows = upcoming_show_artist_details

    for show in venue.past_shows:
        artist_details = {}

        artist_details['artist_id'] = show.artist_id
        artist_details['artist_name'] = show.artists.name
        artist_details['artist_image_link'] = show.artists.image_link
        artist_details['start_time'] = show.start_time.strftime(
            '%Y-%m-%d %H:%M:%S')

        past_show_artist_details.append(artist_details)

    venue.past_shows = past_show_artist_details
    return render_template('pages/show_venue.html', venue=venue)

# ***** Update Venue *****


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    try:
        venue = Venue.query.get_or_404(venue_id)

        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.image_link.data = venue.image_link
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.website_link.data = venue.website
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description

        # TODO: populate form with values from venue with ID <venue_id>
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    except:
        flash('Something went wrong', 'danger')
        return render_template('errors/500.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm()
    if form.validate_on_submit():
        try:
            venue = Venue.query.get_or_404(venue_id)

            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.genres = request.form.getlist('genres')
            venue.facebook_link = form.facebook_link.data
            venue.website = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data

            db.session.add(venue)
            db.session.commit()

            flash(f'Venue {venue.name} was updated successfully!', 'success')
            return redirect(url_for('show_venue', venue_id=venue_id))
        except:
            db.session.rollback()
            flash('An error occurred. Venue could not be updated', 'danger')
            return render_template('errors/404.html')
        finally:
            db.session.close()

# ***** Delete Venue *****


@app.route('/venues/<venue_id>/delete', methods=['GET', 'POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get_or_404(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()

        flash('Venue deleted successfully', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('An error occurred. Venue was not deleted', 'danger')
        return redirect(url_for('show_venue', venue_id=venue_id))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------


# ***** Create a New Artist *****

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)

    if form.validate_on_submit():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                genres=request.form.getlist('genres'),
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )

            db.session.add(artist)
            db.session.commit()

            # on successful db insert, flash success
            flash(
                f'Artist {request.form["name"]} was successfully listed!', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash(
                f'An error occurred. Artist {request.form["name"]} could not be listed.', 'danger')
            return render_template('forms/new_artist.html', form=form)
        finally:
            db.session.close()
    else:
        flash(
            f'An error occurred. Artist {request.form["name"]} could not be listed.', 'danger')
        return render_template('forms/new_artist.html', form=form)
# ***** Get All Artists *****


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)

# ***** Search Artist *****


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(or_(
        Artist.name.ilike(f'%{search_term}%'),
        Artist.city.ilike(f'{search_term}'),
        Artist.state.ilike(f'{search_term}')
    )).all()

    data = []

    for artist in artists:
        upcoming_shows = [
            *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') >=
                    str(datetime.today()), artist.shows)]
        data.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(upcoming_shows)
        })
    response = {
        "count": len(artists),
        "data": data
    }
    # print(response)
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# ***** Get a Single Artist by ID *****


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    """
    The function takes in an artist_id and returns a page with the artist's details and upcoming and
    past shows

    :param artist_id: the ID of the artist
    :return: The show_artist function returns a rendered template of the show_artist.html page.
    """

    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get_or_404(artist_id)

    artist_shows = artist.shows
    upcoming_show_venue_details = []
    past_show_venue_details = []

    upcoming_shows = [
        *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') >=
                str(datetime.today()), artist_shows)]
    past_shows = [
        *filter(lambda d: d.start_time.strftime('%Y-%m-%d %H:%M:%S') <
                str(datetime.today()), artist_shows)]

    setattr(artist, 'upcoming_shows', upcoming_shows)
    setattr(artist, 'upcoming_shows_count', len(upcoming_shows))
    setattr(artist, 'past_shows', past_shows)
    setattr(artist, 'past_shows_count', len(past_shows))

    for show in artist.upcoming_shows:
        venue_details = {}
        venue_details['venue_id'] = show.venue_id
        venue_details['venue_image_link'] = show.venues.image_link
        venue_details['venue_name'] = show.venues.name
        venue_details['start_time'] = show.start_time.strftime(
            '%Y-%m-%d %H:%M:%S')

        upcoming_show_venue_details.append(venue_details)

    artist.upcoming_shows = upcoming_show_venue_details

    for show in artist.past_shows:
        venue_details = {}
        venue_details['venue_id'] = show.venue_id
        venue_details['venue_image_link'] = show.venues.image_link
        venue_details['venue_name'] = show.venues.name
        venue_details['start_time'] = show.start_time.strftime(
            '%Y-%m-%d %H:%M:%S')

        past_show_venue_details.append(venue_details)

    artist.past_shows = past_show_venue_details
    return render_template('pages/show_artist.html', artist=artist)

# ***** Update Artist *****


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    try:
        artist = Artist.query.get_or_404(artist_id)

        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.image_link.data = artist.image_link
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.website_link.data = artist.website
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description

        return render_template('forms/edit_artist.html', form=form, artist=artist)
    except:
        flash('Something went wrong', 'danger')
        return render_template('errors/500.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    try:
        artist = Artist.query.get(artist_id)

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data

        db.session.add(artist)
        db.session.commit()

        flash(
            f'Artist {request.form["name"]} was updated successfully!', 'success')
        return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        db.session.rollback()
        flash('An error occurred. Artist could not be updated', 'danger')
        return render_template('errors/404.html')
    finally:
        db.session.close()


# ***** Delete Artist *****


@app.route('/artists/<artist_id>/delete', methods=['GET', 'POST'])
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    try:
        db.session.delete(artist)
        db.session.commit()

        flash('Artist deleted successfully', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('An error occurred. Artist was not deleted', 'danger')
        return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows
#  ----------------------------------------------------------------

# ***** Get All Shows *****


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows = Show.query.all()
    data = []

    for show in shows:
        show_info = {
            'venue_id': show.venues.id,
            'venue_name': show.venues.name,
            'artist_id': show.artists.id,
            'artist_name': show.artists.name,
            'artist_image_link': show.artists.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }

        data.append(show_info)
    return render_template('pages/shows.html', shows=data)

# ***** Create a Show *****


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
            show = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            # Adding the show to the database and committing it.
            db.session.add(show)
            db.session.commit()

            # on successful db insert, flash success
            flash('Show was successfully listed!', 'success')
            return redirect(url_for('index'))
        except:
            db.session.rollback()
            flash('An error occurred. Show could not be listed.', 'danger')
            return render_template('forms/new_show.html', form=form)
        finally:
            db.session.close()
    else:
        flash('An error occurred. Show could not be listed.', 'danger')
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
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
