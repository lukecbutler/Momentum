import pytest
import sqlite3
from app import app as flask_app, get_db_connection

@pytest.fixture
def app():
    """
    Creat a test client to test the app and database and not clear any information from 
    the real app database
    yielf: flask_app
    """
    flask_app.config.update({
        "TESTING": True,  # Tell Flask we are in testing mode (special behaviors like better error catching)
        "DATABASE": ":memory:",  # Use an in-memory database for testing
        "SECRET_KEY": "test_secret_key"   # Set a simple secret key just for testing sessions
    })

    # Initialize the database
    # Open a Flask application context (needed to modify app-related resources like the database)
    with flask_app.app_context():
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row # Allows us to access rows like dictionaries (row['username'])
        cursor = conn.cursor()

        # Create 'users' table in the in-memory database
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

                # Create 'tasks' table in the in-memory database
        cursor.execute('''
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()  # Save the changes (create the tables)

        def mock_get_db_connection():
            """
            Mock the get_db_connection function to return the in-memory database connection
            """
            return conn
        # Replace the original get_db_connection with the mock one
        flask_app.get_db_connection = mock_get_db_connection
        yield flask_app

        