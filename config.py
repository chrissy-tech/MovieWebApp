import os

# Get the absolute path to the directory this file is in
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	"""Base configuration class."""

	# Secret key for session management (SECURITY WARNING: Change this for production!)
	SECRET_KEY = os.environ.get(
		'SECRET_KEY') or 'a-very-secret-key-that-should-be-changed'

	# --- Database Configuration (SQLite) ---
	# Use SQLite for simplicity during development
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
							  'sqlite:///' + os.path.join(basedir,
														  'moviweb.db')

	# Disable tracking modifications as it consumes resources
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# --- External API Keys (Updated Names) ---
	OMDB_URL = "http://www.omdbapi.com/"
	# Retrieves key from environment variable (Note: removed trailing space from key name)
	API_KEY = os.getenv(
		"OMDB_API_KEY") or 'YOUR_OMDB_API_KEY_FALLBACK'