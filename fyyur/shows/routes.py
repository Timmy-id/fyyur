import sys
from flask import (
    Blueprint,
    render_template,
    url_for,
    flash,
    redirect
)
from fyyur import db
from fyyur.models import Show
from fyyur.shows.forms import ShowForm

# Blueprint configuration
shows = Blueprint('shows', __name__, url_prefix='/shows')


# ***** Get All Shows *****
@shows.route('/')
def all_shows():
    # displays list of shows at /shows
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


@shows.route('/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@shows.route('/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing
    # form
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

            flash('Show was successfully listed!', 'success')
            return redirect(url_for('home.index'))
        except BaseException:
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Show could not be listed.', 'danger')
            return render_template('forms/new_show.html', form=form)
        finally:
            db.session.close()
    else:
        flash('An error occurred. Show could not be listed.', 'danger')
