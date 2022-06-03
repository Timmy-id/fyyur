from flask import Blueprint, render_template
from fyyur.models import Artist, Venue


home = Blueprint('home', __name__)


# Home
# ----------------------------------------------------------------

@home.route('/')
def index():
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()

    return render_template('pages/home.html', venues=venues, artists=artists)
