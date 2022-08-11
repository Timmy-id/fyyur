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
from fyyur import db
from fyyur.artists.forms import ArtistForm
from fyyur.models import Artist, Show, Venue

# Blueprint configuration
artists = Blueprint('artists', __name__, url_prefix='/artists')


# ***** Create a New Artist *****

@artists.route('/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@artists.route('/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
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

            flash(
                f'Artist {request.form["name"]} was successfully listed!',
                'success')
            return redirect(url_for('home.index'))
        except BaseException:
            db.session.rollback()
            print(sys.exc_info())
            flash(
                f'An error occurred. Artist {request.form["name"]} could not be listed.',
                'danger')
            return render_template('forms/new_artist.html', form=form)
        finally:
            db.session.close()
    else:
        flash(
            f'An error occurred. Artist {request.form["name"]} could not be listed.',
            'danger')
        return render_template('forms/new_artist.html', form=form)


# ***** Get All Artists *****

@artists.route('/')
def all_artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


# ***** Search Artist *****

@artists.route('/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(or_(
        Artist.name.ilike(f'%{search_term}%'),
        Artist.city.ilike(f'{search_term}'),
        Artist.state.ilike(f'{search_term}')
    )).all()

    data = []

    for artist in artists:
        upcoming_shows = db.session.query(Show).join(Venue).filter(
            Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()
            
        data.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(upcoming_shows)
        })
    response = {
        "count": len(artists),
        "data": data
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


# ***** Get a Single Artist by ID *****

@artists.route('/<int:artist_id>')
def show_artist(artist_id):
    """
    The function takes in an artist_id and returns a page with the artist's details and upcoming and
    past shows

    :param artist_id: the ID of the artist
    :return: The show_artist function returns a rendered template of the show_artist.html page.
    """
    artist = Artist.query.get_or_404(artist_id)

    upcoming_show_venue_details = []
    past_show_venue_details = []

    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()


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

@artists.route('/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
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

        return render_template(
            'forms/edit_artist.html',
            form=form,
            artist=artist)
    except:
        print(sys.exc_info())
        flash('Something went wrong', 'danger')
        return render_template('errors/500.html')


@artists.route('/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    try:
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
            f'Artist {request.form["name"]} was updated successfully!',
            'success')
        return redirect(url_for('artists.show_artist', artist_id=artist_id))
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist could not be updated', 'danger')
        return render_template(
            'forms/edit_artist.html',
            form=form,
            artist=artist)
    finally:
        db.session.close()


# ***** Delete Artist *****
@artists.route('/<artist_id>/delete', methods=['GET', 'POST'])
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    try:
        db.session.delete(artist)
        db.session.commit()

        flash('Artist deleted successfully', 'success')
        return redirect(url_for('home.index'))
    except BaseException:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist was not deleted', 'danger')
        return redirect(url_for('artists.show_artist', artist_id=artist_id))
