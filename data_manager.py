from models import db, User, Movie
from datetime import datetime


class DataManager:
	"""
	A class to encapsulate all database operations using SQLAlchemy ORM.
	This replaces the previous DBManager and is used by the Flask routes in app.py.
	"""

	@staticmethod
	def get_all_users():
		"""Returns a list of all User objects."""
		return User.query.all()

	@staticmethod
	def create_user(username):
		"""Creates and commits a new user to the database."""
		# NOTE: The calling function in app.py expects a user object or None for error handling.
		if User.query.filter_by(username=username).first():
			return None, "User already exists."
		try:
			new_user = User(username=username)
			db.session.add(new_user)
			db.session.commit()
			return new_user, None
		except Exception as e:
			db.session.rollback()
			return None, str(e)

	@staticmethod
	def get_user_movies(user_id):
		"""Returns a list of all movies for a specific user, ordered newest first."""
		return Movie.query.filter_by(user_id=user_id).order_by(
			Movie.date_added.desc()).all()

	@staticmethod
	def add_movie_for_user(user_id, movie_data):
		"""Adds a movie to a user's list if it doesn't already exist."""
		omdb_id = movie_data.get('omdb_id')

		# Check if the movie is already in the user's list
		exists = Movie.query.filter_by(user_id=user_id,
									   omdb_id=omdb_id).first()
		if exists:
			return None, "Movie is already in your list."

		# Create new movie object
		new_movie = Movie(
			user_id=user_id,
			title=movie_data['title'],
			year=movie_data['year'],
			director=movie_data['director'],
			plot=movie_data['plot'],
			poster_url=movie_data['poster_url'],
			omdb_id=movie_data['omdb_id']
		)

		db.session.add(new_movie)
		db.session.commit()
		return new_movie, None

	@staticmethod
	def delete_movie(movie_id, user_id):
		"""Deletes a movie, ensuring it belongs to the specified user."""
		movie_to_delete = db.session.get(Movie, movie_id)

		if movie_to_delete and movie_to_delete.user_id == user_id:
			db.session.delete(movie_to_delete)
			db.session.commit()
			return True
		return False

	@staticmethod
	def update_movie(movie_id, user_id, new_data):
		"""Updates the plot/review of a movie, ensuring it belongs to the specified user."""
		movie_to_update = db.session.get(Movie, movie_id)

		if movie_to_update and movie_to_update.user_id == user_id:
			# For simplicity, only allow updating the plot (personal review)
			movie_to_update.plot = new_data.get('plot',
												movie_to_update.plot)
			db.session.commit()
			return movie_to_update, None

		return None, "Movie not found or does not belong to the current user."

	@staticmethod
	def delete_user(user_id):
		"""Deletes a user and all their associated movies."""
		try:
			user = db.session.get(User, user_id)
			if user:
				# CRITICAL: Delete all associated movies first to satisfy foreign key constraints
				Movie.query.filter_by(user_id=user_id).delete(
					synchronize_session='fetch')

				db.session.delete(user)
				db.session.commit()
				return True, None  # Success
			return False, "User not found."
		except Exception as e:
			db.session.rollback()
			return False, str(e)