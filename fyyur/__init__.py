from flask import Flask
import dateutil.parser
import babel
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from fyyur.config import Config


db = SQLAlchemy()
moment = Moment()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)

    from fyyur.venues.routes import venues
    from fyyur.shows.routes import shows
    from fyyur.artists.routes import artists
    from fyyur.home.routes import home
    from fyyur.errors.errors import errors

    app.register_blueprint(home)
    app.register_blueprint(venues)
    app.register_blueprint(artists)
    app.register_blueprint(shows)
    app.register_blueprint(errors)


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


    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

    return app
