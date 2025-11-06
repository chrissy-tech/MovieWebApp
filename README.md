# 🎬 **MoviTracker: Your Personal Movie Watchlist**

**MoviTracker is a multi-user web application designed to help movie enthusiasts manage their personal watch lists.
Powered by Flask and integrated with the OMDb API, you can search for, add, track, and rate movies all in one place.**

## ✨ Features

➢ **Multi-User Support** 🧑‍🤝‍🧑: Simple user selection/registration to keep watchlists separate.

➢ **OMDb Integration** 🌐: Search for movies by title and instantly fetch details like poster, year, and director.

➢ **Custom Tracking** 📝: Add movies to your personal list.

➢ **Status Management** ✅: Track movies with statuses like 'Watching', 'Watched', or 'Planned'.

➢ **Custom Rating System** ⭐: Rate movies on a 1-5 star scale, displayed using a clean visual indicator.

➢ **User Management** 🗑️: Ability to select, register, and delete users along with their data.

➢ **Database Initialization** 💾: Includes a custom Flask CLI command (flask init-db) for easy setup.


## ⚙️ Setup and Installation

**Follow these steps to get MoviTracker running locally.**

_1. Clone the Repository_

git clone https://github.com/chrissy-tech/MovieWebApp.git
cd movietracker


_2. Set up Virtual Environment_

It's recommended to use a virtual environment to manage dependencies:

python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate


_3. Install Dependencies_

Install all necessary packages, including Flask, SQLAlchemy, and Requests:

pip install Flask Flask-SQLAlchemy requests click




_4. Configuration (OMDb API Key)_

You need to create a config.py file to handle configuration variables, including your OMDb API key.

Sign up for an API key at OMDb API.

Create a file named config.py in the root directory.

Add the following required configuration variables:

# config.py
import os

class Config:
    # Set a strong secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_and_complex_key'
    
    # Database Configuration (using SQLite for simplicity)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movietracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OMDb API Settings
    API_KEY = 'YOUR_OMDB_API_KEY_HERE'  # 🔑 Replace with your actual OMDb API Key
    OMDB_URL = '[http://www.omdbapi.com/](http://www.omdbapi.com/)'


_5. Initialize the Database_

Use the custom Flask CLI command to create the necessary tables (User and Movie) defined in models.py:

flask init-db



## ▶️ Usage

_1. Run the Application_

Start the Flask development server:

flask run


The application will typically be available at http://127.0.0.1:5000/.



_2. Getting Started_

Navigate to the root URL (/).

Register a new user or select an existing one.

Use the Add a New Movie page to search the OMDb database.

View your Watch List and use the Edit Status/Rating button to add your personal notes and set a star rating.



## 🛠️ Project Structure (Required files)

To run the application, you must have the following files present alongside app.py:

➢ **config.py**: Stores API keys and database configuration.

➢ **models.py**: Defines the SQLAlchemy database structure (User, Movie).

➢ **data_manager.py**: Contains the logic for interacting with the database (CRUD operations).

➢ **HTML Templates** (e.g., movie_list.html, add_movie.html, base.html, etc.).
