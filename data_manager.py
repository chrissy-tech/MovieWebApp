from models import db, User, Movie
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

class DataManager:

	@staticmethod
	def get_all_users():
		"""Returns a list of all User objects."""
		return db.session.execute(db.select(User)).scalars().all()

	@staticmethod
	def create_user(username):
		"""Creates a new user and returns the User object or an error message."""
		try:
			existing_user = db.session.execute(
				db.select(User).filter_by(username=username)
			).scalar_one_or_none()
			if existing_user:
				return None, "A user with that username already exists."
			new_user = User(username=username)
			db.session.add(new_user)
			db.session.commit()
			return new_user, None
		except IntegrityError:
			db.session.rollback()
			return None, "Database integrity error. User might already exist."
		except Exception as e:
			db.session.rollback()
			return None, f"An unexpected error occurred: {e}"

	@staticmethod
	def delete_user(user_id):
		"""Deletes a user and all associated movies."""
		try:
			user_to_delete = db.session.get(User, user_id)
			if user_to_delete:
				db.session.delete(user_to_delete)
				db.session.commit()
				return True, None
			else:
				return False, "User not found."
		except Exception as e:
			db.session.rollback()
			return False, f"Database error during user deletion: {e}"

	@staticmethod
	def get_user_movies(user_id):
		"""Returns a list of all movies belonging to a specific user."""
		return db.session.execute(
			db.select(Movie)
			.filter_by(user_id=user_id)
			.order_by(Movie.date_added.desc())
		).scalars().all()

	@staticmethod
	def get_movie_by_id(movie_id, user_id):
		"""Returns a single Movie object by ID,
		ensuring it belongs to the user."""
		return db.session.execute(
			db.select(Movie).filter_by(id=movie_id, user_id=user_id)
		).scalar_one_or_none()

	@staticmethod
	def add_movie_for_user(user_id, movie_data):
		"""Adds a new movie to the user's list."""
		try:
			omdb_id = movie_data.get('omdb_id')
			existing_movie = db.session.execute(
				db.select(Movie).filter(
					and_(
						Movie.user_id == user_id,
						Movie.omdb_id == omdb_id
					)
				)
			).scalar_one_or_none()

			if existing_movie:
				return None, "This movie is already in your list."

			new_movie = Movie(
				user_id=user_id,
				title=movie_data.get('title'),
				year=movie_data.get('year'),
				director=movie_data.get('director'),
				plot=movie_data.get('plot'),
				poster_url=movie_data.get('poster_url'),
				omdb_id=omdb_id,
			)

			db.session.add(new_movie)
			db.session.commit()
			return new_movie, None

		except Exception as e:
			db.session.rollback()
			print(f"Error adding movie: {e}")
			return None, ("An unexpected database "
						  "error occurred while adding the movie.")

	@staticmethod
	def delete_movie(movie_id, user_id):
		"""Deletes a movie from the user's list."""
		try:
			movie_to_delete = db.session.execute(
				db.select(Movie).filter_by(id=movie_id,
										   user_id=user_id)
			).scalar_one_or_none()

			if movie_to_delete:
				db.session.delete(movie_to_delete)
				db.session.commit()
				return True, None
			else:
				return False, ("Movie not found or does "
							   "not belong to the current user.")
		except Exception as e:
			db.session.rollback()
			return False, f"Database error during movie deletion: {e}"

	@staticmethod
	def update_movie(movie_id, user_id, update_data):
		"""Updates a movie's fields and saves to the database."""
		try:
			# Find the movie
			movie = db.session.execute(
				db.select(Movie).filter_by(id=movie_id,
										   user_id=user_id)
			).scalar_one_or_none()

			if not movie:
				return (None, "Movie not found or does"
							  " not belong to the current user.")

			print(
				f"DEBUG DataManager - Before update: rating={movie.rating}")
			print(f"DEBUG DataManager - Update data: {update_data}")

			# Apply updates
			for key, value in update_data.items():
				setattr(movie, key, value)
				print(f"DEBUG DataManager - Set {key} to {value}")

			print(
				f"DEBUG DataManager - After setattr: rating={movie.rating}")

			# Commit the transaction
			db.session.commit()

			# Refresh to get latest DB values
			db.session.refresh(movie)

			print(
				f"DEBUG DataManager - After commit & "
				f"refresh: rating={movie.rating}")

			return movie, None
		except Exception as e:
			db.session.rollback()
			print(f"Error updating movie: {e}")
			return None, f"Database error during update: {e}"