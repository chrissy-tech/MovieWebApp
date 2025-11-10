from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)

	# Relationship to Movie model (cascade delete all movies when user is deleted)
	movies = db.relationship('Movie', backref='user', lazy=True,
							 cascade="all, delete-orphan")

	def __repr__(self):
		return f'<User {self.username}>'


class Movie(db.Model):
	__tablename__ = 'movies'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.ForeignKey('users.id'), nullable=False)
	title = db.Column(db.String(255), nullable=False)
	year = db.Column(db.String(10))
	director = db.Column(db.String(255))
	plot = db.Column(db.Text)
	poster_url = db.Column(db.String(500))
	omdb_id = db.Column(db.String(50), unique=False, nullable=True)
	date_added = db.Column(db.DateTime, default=db.func.now())

	# CRITICAL: Diese beiden Felder waren das Problem!
	rating = db.Column(db.Integer, default=0)
	status = db.Column(db.String(50), default='Planning to Watch')

	def __repr__(self):
		return f'<Movie {self.title}>'