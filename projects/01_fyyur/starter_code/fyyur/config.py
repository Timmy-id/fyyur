import os

class Config:
    SECRET_KEY = os.urandom(32)
    DATABASE_NAME = 'fyyur'
    username = 'postgres'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = "postgresql://{}@{}/{}".format(
        username, url, DATABASE_NAME
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Enable debug mode.
    DEBUG = True
