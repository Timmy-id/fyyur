import sys
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    url_for,
    request,
    flash,
    redirect
)
from sqlalchemy import or_
from fyyur.models import Show, Venue
from fyyur import db
from fyyur.venues.forms import VenueForm

# Blueprint configuration
venues = Blueprint('venues', __name__, url_prefix='/venues')


# ***** Create a New Venue *****

@venues.route('/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@venues.route('/create', methods=['POST'])
def create_venue_submission():
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

            db.session.add(venue)
            db.session.commit()

            flash(
                f'Venue {form.name.data} was successfully listed!', 'success')
            return redirect(url_for('home.index'))
        except BaseException:
            db.session.rollback()
            print(sys.exc_info())
            flash(
                f'An error occurred. Venue {form.name.data} could not be listed!',
                'danger')
            return render_template('forms/new_venue.html', form=form)
        finally:
            db.session.close()
    else:
        flash(
            f'An error occurred. Venue {form.name.data} could not be listed!',
            'danger')
        return render_template('forms/new_venue.html', form=form)


# ***** Get All Venues *****

@venues.route('/')
def all_venues():
    # Get the distinct values for city and state
    venues = Venue.query.distinct(Venue.city, Venue.state).all()

    all_data = []

    for venue in venues:
        venue_data = {
            'city': venue.city,
            'state': venue.state
        }

        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

        # filter the database using the distinct city and state
        res = Venue.query.filter_by(city=venue.city, state=venue.state).all()

        venue_details = []

        for data in res:
            venue_details.append({
                'id': data.id,
                'name': data.name,
                'num_upcoming_shows': len(upcoming_shows)
            })

        venue_data['venues'] = venue_details
        all_data.append(venue_data)
    return render_template('pages/venues.html', areas=all_data)


# ***** Search Venue *****

@venues.route('/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(or_(
        Venue.name.ilike(f'%{search_term}%'),
        Venue.city.ilike(f'{search_term}'),
        Venue.state.ilike(f'{search_term}')
    )).all()

    data = []

    for venue in venues:
        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()

        data.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(upcoming_shows)
        })
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


# ***** Get a Single Venue by ID *****

@venues.route('/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get_or_404(venue_id)

    upcoming_show_artist_details = []
    past_show_artist_details = []

    past_shows = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

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

@venues.route('/<int:venue_id>/edit', methods=['GET'])
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

        return render_template('forms/edit_venue.html', form=form, venue=venue)
    except BaseException:
        print(sys.exc_info())
        flash('Something went wrong', 'danger')
        return render_template('errors/500.html')


@venues.route('/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    venue = Venue.query.get_or_404(venue_id)
    if form.validate_on_submit():
        try:
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
            return redirect(url_for('venues.show_venue', venue_id=venue_id))
        except BaseException:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue could not be updated', 'danger')
            return render_template('errors/404.html')
        finally:
            db.session.close()
    else:
        print(sys.exc_info())
        flash('An error occurred. Venue could not be updated', 'danger')
        return render_template('forms/edit_venue.html', form=form, venue=venue)


# ***** Delete Venue *****

@venues.route('/<int:venue_id>/delete', methods=['GET', 'POST'])
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()

        flash('Venue deleted successfully', 'success')
        return redirect(url_for('home.index'))
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue was not deleted', 'danger')
        return redirect(url_for('venues.show_venue', venue_id=venue_id))
