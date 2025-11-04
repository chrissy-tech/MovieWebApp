import click
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy object (it will be associated with the Flask app in app.py)
db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user in the MoviWeb application.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)

    # 'movies' is a relationship property (backref) to link to the Movie model
    movies = db.relationship('Movie', backref='user', lazy='dynamic',
                       cascade="all, delete-orphan")

    def __repr__(self):
       return f'<User {self.username}>'


class Movie(db.Model):
    """
    Represents a movie added to a user's list.
    Information is generally fetched from the OMDb API.
    """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key linking the movie to a specific user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                   nullable=False)

    # Core movie data, mostly from OMDb
    title = db.Column(db.String(128), nullable=False)
    year = db.Column(
       db.String(10))  # OMDb year can include ranges (e.g., "2020–")
    director = db.Column(db.String(128))
    plot = db.Column(db.Text)
    poster_url = db.Column(db.String(256))

    # Store the OMDb ID to easily check for duplicates or re-fetch details
    omdb_id = db.Column(db.String(15), nullable=False)

    # Tracking
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
       return f'<Movie {self.title} ({self.year}) by User ID {self.user_id}>'