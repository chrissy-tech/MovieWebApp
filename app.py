import requests
import click  # Used for custom CLI commands
import functools
from flask import Flask, render_template, request, redirect, url_for, \
	session, g

# Assuming config.py and models.py are in the same directory
# NOTE: login_required decorator helper is missing from the original file,
# I am including a simple version here so the movie routes work correctly.
from config import Config
from models import db, User, Movie
from data_manager import \
	DataManager  # New: Import the DataManager class


# --- Authentication Decorator (Added for completeness) ---
def login_required(view):
	"""View decorator that redirects anonymous users to the login page."""

	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('user_select'))
		return view(**kwargs)

	return wrapped_view


# --- Application Factory Function ---
def create_app():
	"""Initializes the Flask application."""
	app = Flask(__name__)
	app.config.from_object(Config)

	# Initialize extensions
	db.init_app(app)

	# --- Helper Function for OMDb API ---
	def get_omdb_details(movie_id=None, title=None):
		"""Fetches movie details from the OMDb API, using updated config names."""
		# Use the new API_KEY name from Config
		params = {'apikey': app.config['API_KEY']}

		# We search by ID ('i') for confirmed adds, and by Title ('t') for initial search
		if movie_id:
			params['i'] = movie_id
		elif title:
			params['t'] = title

		# Check for placeholder API key (using the fallback key defined in config.py)
		if app.config['API_KEY'] == 'YOUR_OMDB_API_KEY_FALLBACK':
			return None, "OMDb API Key is not properly configured in config.py or environment."

		try:
			# Use the new OMDB_URL name from Config
			# Assuming OMDB_URL is defined in Config (e.g., 'http://www.omdbapi.com/')
			omdb_url = app.config.get('OMDB_URL',
									  'http://www.omdbapi.com/')
			response = requests.get(omdb_url,
									params=params)
			response.raise_for_status()  # Raise exception for bad status codes (4xx or 5xx)
			data = response.json()

			if data.get('Response') == 'True':
				return data, None
			else:
				return None, data.get('Error',
									  'Movie not found or OMDb error.')
		except requests.exceptions.RequestException as e:
			print(f"OMDb API Request Error: {e}")
			return None, "Connection or API request failed."

	# --- CLI Commands for Database Management ---
	@app.cli.command("init-db")
	def init_db_command():
		"""Initializes the database tables."""
		# We removed the @click.with_appcontext decorator here to fix the runtime error
		with app.app_context():
			db.create_all()
		click.echo('Initialized the database.')

	# --- Before Request Hook for User Management ---
	@app.before_request
	def load_logged_in_user():
		"""Checks the session for a user ID and loads the user object into Flask's global 'g'."""
		user_id = session.get('user_id')

		if user_id is None:
			g.user = None
		else:
			g.user = db.session.get(User, user_id)

	# --- Routes ---

	@app.route('/users')
	def list_users():
		"""Temporarily returns a string representation of all users for DataManager integration test."""
		users = DataManager.get_all_users()
		# Returning a string representation of the list of User objects
		return str(
			[f"ID: {u.id}, Username: {u.username}" for u in users])

	@app.route('/', methods=['GET'])
	def user_select():
		"""Displays all users for selection and handles user creation. Reads error from URL args."""
		# Get error/message from URL query parameters (used after redirects)
		error = request.args.get('error')
		users = DataManager.get_all_users()
		return render_template('user_select.html', users=users,
							   error=error)

	@app.route('/register', methods=['POST'])
	def register():
		"""Handles the creation of a new user."""
		username = request.form.get('username')

		if not username:
			return render_template('user_select.html',
								   users=DataManager.get_all_users(),
								   error="Username cannot be empty.")

		# Assuming DataManager.create_user returns (user_object, error_message)
		# The original code structure suggests it returns a User object on success, or None.
		new_user, db_error = DataManager.create_user(
			username) if hasattr(DataManager, 'create_user') else (
			None, "create_user not found")

		if new_user:
			session['user_id'] = new_user.id
			return redirect(url_for('movie_list'))
		else:
			return render_template('user_select.html',
								   users=DataManager.get_all_users(),
								   error=db_error if db_error else "User already exists or DB error.")

	@app.route('/select_user/<int:user_id>')
	def select_user(user_id):
		"""Sets the selected user ID in the session and redirects."""
		user = db.session.get(User, user_id)
		if user:
			session['user_id'] = user_id
			return redirect(url_for('movie_list'))
		return redirect(
			url_for('user_select', error="User not found."))

	@app.route('/logout')
	def logout():
		"""Clears the user ID from the session."""
		session.clear()
		return redirect(url_for('user_select'))

	# --- NEW ROUTE: Delete User ---
	@app.route('/delete_user/<int:user_id>', methods=['POST'])
	def delete_user_route(user_id):
		"""Deletes a user and all their associated movies."""

		# Store the ID of the user currently logged in
		logged_in_user_id = session.get('user_id')

		# Assuming DataManager.delete_user is implemented as described above
		success, error = DataManager.delete_user(user_id)

		if success:
			# If the deleted user was the one logged in, clear the session
			if logged_in_user_id == user_id:
				session.clear()
				message = f"User (ID: {user_id}) and all their data were successfully deleted."
			else:
				message = f"User (ID: {user_id}) and all their data were successfully deleted."

			# Redirect back to user selection with a success message
			return redirect(url_for('user_select', error=message))
		else:
			# Redirect back with the error message
			return redirect(url_for('user_select',
									error=f"Error deleting user: {error}"))

	# --- END NEW ROUTE ---

	@app.route('/movies')
	@login_required
	def movie_list():
		"""Displays the current user's movie list."""
		# login_required handles the g.user check now
		movies = DataManager.get_user_movies(g.user.id)
		return render_template('movie_list.html', movies=movies)

	@app.route('/movies/add', methods=['GET', 'POST'])
	@login_required
	def movie_add():
		"""Allows users to search for a movie and add it to their list."""
		# login_required handles the g.user check now

		search_result = None
		error = None
		message = None

		if request.method == 'POST':
			omdb_id = request.form.get('omdb_id')

			# --- 1. Handle "Confirm Add" (omdb_id is present) ---
			if omdb_id:
				# Re-fetch details to ensure full data structure for storage
				movie_data, api_error = get_omdb_details(
					movie_id=omdb_id)

				if movie_data:
					# Map OMDb response fields to our Movie model fields
					movie_map = {
						'title': movie_data.get('Title', 'N/A'),
						'year': movie_data.get('Year', 'N/A'),
						'director': movie_data.get('Director', 'N/A'),
						'plot': movie_data.get('Plot', 'N/A'),
						# If poster is 'N/A', we'll use our placeholder URL later
						'poster_url': movie_data.get(
							'Poster') if movie_data.get(
							'Poster') != 'N/A' else None,
						'omdb_id': movie_data.get('imdbID')
					}

					# Add to DB
					new_movie, db_error = DataManager.add_movie_for_user(
						g.user.id, movie_map)

					if new_movie:
						return redirect(url_for('movie_list'))
					else:
						error = db_error  # e.g., "Movie already in list"
				else:
					error = f"Failed to retrieve details for OMDb ID {omdb_id}. {api_error}"

			# --- 2. Handle "Search" (movie_title is present) ---
			else:
				movie_title = request.form.get('movie_title')
				if movie_title:
					search_result, api_error = get_omdb_details(
						title=movie_title)

					if search_result:
						message = f"Found: {search_result.get('Title')} ({search_result.get('Year')}). Click 'Confirm Add' to save."
					else:
						error = api_error

		return render_template('add_movie.html',
							   search_result=search_result,
							   error=error, message=message)

	@app.route('/movies/delete/<int:movie_id>', methods=['POST'])
	@login_required
	def movie_delete(movie_id):
		"""Deletes a movie from the user's list."""
		# login_required handles the g.user check now

		# Pass user_id for security check within the DataManager
		DataManager.delete_movie(movie_id, g.user.id)

		return redirect(url_for('movie_list'))

	@app.route('/movies/update/<int:movie_id>',
			   methods=['GET', 'POST'])
	@login_required
	def movie_update(movie_id):
		"""Handles updating a movie's details (specifically the plot/review)."""
		# login_required handles the g.user check now

		movie = db.session.get(Movie, movie_id)

		# Security check: Ensure movie exists and belongs to the current user
		if not movie or movie.user_id != g.user.id:
			return redirect(url_for('movie_list'))

		error = None
		message = None

		if request.method == 'POST':
			new_plot = request.form.get('plot')

			if new_plot:
				# Update the movie using the DataManager method
				updated_movie, db_error = DataManager.update_movie(
					movie_id, g.user.id, {'plot': new_plot})

				if updated_movie:
					message = f"Successfully updated details for {movie.title}!"
					# Re-fetch the movie to display the new plot on the GET request below
					movie = updated_movie
				else:
					error = db_error

		return render_template('index.html', movie=movie,
							   error=error, message=message)

	return app


if __name__ == '__main__':
	app = create_app()
	with app.app_context():
		db.create_all()  # Ensure tables exist on run
	app.run(debug=True, host='0.0.0.0', port=5000)