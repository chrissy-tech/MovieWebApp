import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	"""Base configuration class."""

	# Secret key for session management
	SECRET_KEY = os.environ.get(
		'SECRET_KEY') or 'a-very-secret-key-that-should-be-changed'

	# Database Configuration (SQLite)
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
							  'sqlite:///' + os.path.join(basedir,
														  'moviweb.db')

	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# External API Configuration
	OMDB_URL = "http://www.omdbapi.com/"
	API_KEY = os.getenv(
		"OMDB_API_KEY") or 'YOUR_OMDB_API_KEY_FALLBACK'