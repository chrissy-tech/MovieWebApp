import functools
import logging
from typing import Tuple, Optional, Dict, Any

import requests
import click
from flask import Flask, render_template, request, redirect, url_for, \
	session, g, flash

from config import Config
from models import db, User, Movie
from data_manager import DataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_required(view):
	"""View decorator that redirects anonymous users to the login page."""

	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			flash('Please select or create a user to continue.',
				  'info')
			return redirect(url_for('user_select'))
		return view(**kwargs)

	return wrapped_view


def get_omdb_details(api_key: str, omdb_url: str,
					 movie_id: Optional[str] = None,
					 title: Optional[str] = None) -> Tuple[
	Optional[Dict[str, Any]], Optional[str]]:
	"""
	Fetches movie details from the OMDb API.
	"""
	if api_key == 'YOUR_OMDB_API_KEY_FALLBACK':
		return None, ("OMDb API Key is not configured. "
					  "Please set OMDB_API_KEY environment variable.")

	params = {'apikey': api_key}

	if movie_id:
		params['i'] = movie_id
	elif title:
		params['t'] = title
	else:
		return None, "Either movie_id or title must be provided."

	try:
		response = requests.get(omdb_url, params=params, timeout=10)
		response.raise_for_status()
		data = response.json()

		if data.get('Response') == 'True':
			return data, None
		else:
			return None, data.get('Error', 'Movie not found.')
	except requests.exceptions.Timeout:
		logger.error("OMDb API request timeout")
		return None, "Request timeout. Please try again."
	except requests.exceptions.RequestException as e:
		logger.error(f"OMDb API Request Error: {e}")
		return None, "Connection failed. Please check your internet connection."


def render_stars(rating: Optional[int]) -> str:
	"""
	Converts an integer rating (0-5) into a Unicode star string.
	"""
	if rating is None or rating == 0:
		return "Unrated"

	try:
		rating = int(rating)
		if rating < 0 or rating > 5:
			return "Unrated"
	except (TypeError, ValueError):
		return "Unrated"

	full_stars = '★' * rating
	empty_stars = '☆' * (5 - rating)
	return full_stars + empty_stars


def create_app():
	"""Initializes and configures the Flask application."""
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)

	# Register template helper function
	app.jinja_env.globals.update(render_stars=render_stars)


	@app.cli.command("init-db")
	def init_db_command():
		"""Initializes the database tables."""
		with app.app_context():
			db.create_all()
		click.echo('✓ Database initialized successfully.')

	@app.before_request
	def load_logged_in_user():
		"""Loads the current user from session before each request."""
		user_id = session.get('user_id')
		g.user = db.session.get(User, user_id) if user_id else None

	@app.route('/')
	def user_select():
		"""Displays all users for selection."""
		error = request.args.get('error')
		users = DataManager.get_all_users()
		return render_template('user_select.html', users=users,
							   error=error)

	@app.route('/register', methods=['POST'])
	def register():
		"""Handles the creation of a new user."""
		username = request.form.get('username', '').strip()

		if not username:
			return render_template('user_select.html',
								   users=DataManager.get_all_users(),
								   error="Username cannot be empty.")

		if len(username) > 80:
			return render_template('user_select.html',
								   users=DataManager.get_all_users(),
								   error="Username is too long (max 80 characters).")

		new_user, db_error = DataManager.create_user(username)

		if new_user:
			session['user_id'] = new_user.id
			flash(f'Welcome, {new_user.username}!', 'success')
			return redirect(url_for('movie_list'))
		else:
			return render_template('user_select.html',
								   users=DataManager.get_all_users(),
								   error=db_error or "User already exists.")

	@app.route('/select_user/<int:user_id>')
	def select_user(user_id):
		"""Sets the selected user ID in the session."""
		user = db.session.get(User, user_id)
		if user:
			session['user_id'] = user_id
			flash(f'Logged in as {user.username}', 'success')
			return redirect(url_for('movie_list'))
		return redirect(
			url_for('user_select', error="User not found."))

	@app.route('/logout')
	def logout():
		"""Clears the user ID from the session."""
		username = g.user.username if g.user else "User"
		session.clear()
		flash(f'Goodbye, {username}!', 'info')
		return redirect(url_for('user_select'))

	@app.route('/delete_user/<int:user_id>', methods=['POST'])
	def delete_user_route(user_id):
		"""Deletes a user and all their associated movies."""
		logged_in_user_id = session.get('user_id')
		success, error = DataManager.delete_user(user_id)

		if success:
			if logged_in_user_id == user_id:
				session.clear()
			message = f"User (ID: {user_id}) and all their data were successfully deleted."
			return redirect(url_for('user_select', error=message))
		else:
			return redirect(url_for('user_select',
									error=f"Error deleting user: {error}"))

	@app.route('/movies')
	@login_required
	def movie_list():
		"""Displays the current user's movie list."""
		movies = DataManager.get_user_movies(g.user.id)
		return render_template('movie_list.html', movies=movies)

	@app.route('/movies/add', methods=['GET', 'POST'])
	@login_required
	def movie_add():
		"""Allows users to search for a movie and add it to their list."""
		search_result = None
		error = None
		message = None

		if request.method == 'POST':
			omdb_id = request.form.get('omdb_id')

			# Handle "Confirm Add"
			if omdb_id:
				movie_data, api_error = get_omdb_details(
					app.config['API_KEY'],
					app.config['OMDB_URL'],
					movie_id=omdb_id
				)

				if movie_data:
					movie_map = {
						'title': movie_data.get('Title', 'N/A'),
						'year': movie_data.get('Year', 'N/A'),
						'director': movie_data.get('Director', 'N/A'),
						'plot': movie_data.get('Plot', 'N/A'),
						'poster_url': movie_data.get(
							'Poster') if movie_data.get(
							'Poster') != 'N/A' else None,
						'omdb_id': movie_data.get('imdbID')
					}

					new_movie, db_error = DataManager.add_movie_for_user(
						g.user.id, movie_map
					)

					if new_movie:
						flash(
							f'Successfully added "{new_movie.title}" to your list!',
							'success')
						return redirect(url_for('movie_list'))
					else:
						error = db_error
				else:
					error = f"Failed to retrieve details for movie. {api_error}"

			# Handle "Search"
			else:
				movie_title = request.form.get('movie_title',
											   '').strip()
				if movie_title:
					search_result, api_error = get_omdb_details(
						app.config['API_KEY'],
						app.config['OMDB_URL'],
						title=movie_title
					)

					if search_result:
						message = (f"Found: {search_result.get('Title')} "
								   f"({search_result.get('Year')})")
					else:
						error = api_error
				else:
					error = "Please enter a movie title."

		return render_template('add_movie.html',
							   search_result=search_result,
							   error=error,
							   message=message)

	@app.route('/movies/delete/<int:movie_id>', methods=['POST'])
	@login_required
	def movie_delete(movie_id):
		"""Deletes a movie from the user's list."""
		success, error = DataManager.delete_movie(movie_id, g.user.id)

		if success:
			flash('Movie deleted successfully.', 'success')
		else:
			flash(error or 'Failed to delete movie.', 'danger')

		return redirect(url_for('movie_list'))

	@app.route('/movies/update/<int:movie_id>',
			   methods=['GET', 'POST'])
	@login_required
	def movie_update(movie_id):
		"""Handles updating a movie's details."""
		movie = db.session.get(Movie, movie_id)

		if not movie or movie.user_id != g.user.id:
			flash("Movie not found or you don't have permission.",
				  'danger')
			return redirect(url_for('movie_list'))

		if request.method == 'POST':
			update_data = {}

			# Get form data
			new_plot = request.form.get('plot', '').strip()
			new_rating = request.form.get('rating')
			new_status = request.form.get('status')

			# Validate and prepare update data
			if new_plot:
				update_data['plot'] = new_plot

			if new_rating is not None:
				try:
					rating_int = int(new_rating)
					if 0 <= rating_int <= 5:
						update_data['rating'] = rating_int
					else:
						flash('Rating must be between 0 and 5.',
							  'danger')
						return render_template('movie_update.html',
											   movie=movie)
				except (ValueError, TypeError):
					flash('Invalid rating value.', 'danger')
					return render_template('movie_update.html',
										   movie=movie)

			if new_status:
				valid_statuses = ['Planning to Watch', 'Watching',
								  'Watched']
				if new_status in valid_statuses:
					update_data['status'] = new_status
				else:
					flash('Invalid status value.', 'danger')
					return render_template('movie_update.html',
										   movie=movie)

			# Update if we have data
			if update_data:
				updated_movie, db_error = DataManager.update_movie(
					movie_id, g.user.id, update_data
				)

				if updated_movie:
					flash(f'Successfully updated "{movie.title}"!',
						  'success')
					return redirect(url_for('movie_list'))
				else:
					flash(db_error or 'Failed to update movie.',
						  'danger')
			else:
				flash('No changes submitted.', 'info')
				return redirect(url_for('movie_list'))

		# GET request - display form
		return render_template('movie_update.html', movie=movie)

	@app.errorhandler(404)
	def not_found(error):
		"""Handle 404 errors."""
		flash('Page not found.', 'danger')
		return redirect(url_for('user_select'))

	@app.errorhandler(500)
	def internal_error(error):
		"""Handle 500 errors."""
		db.session.rollback()
		logger.error(f"Internal error: {error}")
		flash('An internal error occurred. Please try again.',
			  'danger')
		return redirect(url_for('user_select'))

	return app


if __name__ == '__main__':
	app = create_app()
	with app.app_context():
		db.create_all()
	app.run(debug=True, host='0.0.0.0', port=5000)