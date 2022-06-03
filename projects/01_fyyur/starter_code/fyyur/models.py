from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from fyyur import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


# Venue Model
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String())
    genres = db.Column(ARRAY(String), nullable=False)
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venues',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'


# Artist Model
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    genres = db.Column(ARRAY(String), nullable=False)
    image_link = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String())
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artists',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'


# Show Model
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Show ID: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>'
