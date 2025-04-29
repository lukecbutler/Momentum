import pytest
import sqlite3
import random
from app import app as flask_app
from app import *
from werkzeug.security import generate_password_hash, check_password_hash


@pytest.fixture
def app():
    """
    Fixture to provide the Flask app for testing.
    :return: Flask app instance
    """
    flask_app.config["TESTING"] = True
    return flask_app

    
@pytest.fixture
def client(app):
    """
    Creating a test client to test the app and database
    :param app: Flask app instance
    :return: Test client instance
    """
    return app.test_client()

def test_get_db_connection():
    """
    Test if get_db_connection() returns a valid SQLite connection
    """
    # Use 'with' to automatically close the connection when done
    with get_db_connection() as conn:
        # Check if it's a valid sqlite3.Connection object
        assert isinstance(conn, sqlite3.Connection)

        # Check if the row_factory is set to sqlite3.Row
        assert conn.row_factory == sqlite3.Row

        # Check if a simple query works
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

def test_init_db():
    """
    Test the init_db function to ensure that the database tables are created correctly
    and that the database is initialized properly.
    """

    # Call the init_db function
    init_db()

    # Check if the tables exist by querying the sqlite_master table
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Verify that both 'users' and 'tasks' tables exist
        assert 'users' in tables
        assert 'tasks' in tables


def register_test_user(client, test_username, test_password):
    """
    Reusable function to register a test user in the database
    :param client: Test client that was created for testing the app
    :param test_username: Username for the test user
    :param test_password: Password for the test user (plain text)
    """
    response = client.post('/register', data={
        "username": test_username,
        "password": test_password  # send plain password
    }, follow_redirects=True)
    
    assert response.status_code == 200
        
def remove_test_user(client, app, test_username):
    """
    Reusable function to remove a test user from the database
    :param client: Test client that was created for testing the app
    :param test_username: Username for the test user to be removed
    """
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE username = ?', (test_username,))
            conn.commit()

            # Check if a user was actually deleted
            return cursor.rowcount > 0

def test_register_success(app, client):
    """
    Test the registration functionality to ensure that users can register
    with a unique username and password
    :param client: Test client that was created for testing the app
    """
    # Check the databse to make sure the user was added
    register_test_user(client, "testusername", "testpassword")

    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', ("testusername",))
            user = cursor.fetchone()
            assert user is not None
            assert user['username'] == "testusername"
            assert user['password'] != "testpassword"  # Password should be hashed in a real instance
            assert user['id'] is not None  # Check if the user ID is generated

            # Ensure that the user is deleted
            removed = remove_test_user(client, app, "testusername") # Clean up/remove test user after the test
            assert removed is True  # Ensure that the user is deleted

def test_register_failure(app, client):
    """
    Test the registration functionality to ensure that duplicate usernames cannot be
    registered
    :param client: Test client that was created for testing the app
    """
    # Register a test user
    register_test_user(client, "duplicate", "testpassword")

    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Attempt to register the same user again
            response = client.post('/register', data={
                "username": "duplicate",
                "password": "testpassword" 
            }, follow_redirects=True)
            
            # Check that the response indicates failure (e.g., status code 200 and error message)
            assert response.status_code == 200
            assert b"Username already exists!" in response.data

            # Ensure that the user is deleted
            removed = remove_test_user(client, app, "duplicate") # Clean up/remove test user after the test
            assert removed is True  # Ensure that the user is deleted
    
def test_login_success(app, client):
    """
    Test the login functionality to ensure that users can log in successfully
    :param client: Test client that was created for testing the app
    """
    # Insert a test user into the database
    register_test_user(client, "testuser", "testpassword")

    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })

    assert response.status_code == 302  # Check for redirect after successful login
    
    removed = remove_test_user(client, app, "testuser") # Clean up/remove test user after the test
    assert removed is True 

def test_login_failure(client):
    """
    Test the login functionality to ensure that invalid credentials are handled gracefully
    :param client: Test client that was created for testing the app
    """
    # Attempt to log in with invalid credentials
    response = client.post('/login', data={'username': 'invaliduser', 'password': 'invalidpass'})
    
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data

def test_add_task_success(app, client):
    """
    Test the add_task function to ensure that valid tasks are successful and are added
    to the database
    :param app: Flask app instance
    :param client: Test client that was created for testing the app
    """
    # Create a test user
    register_test_user(client, "testuser", "testpassword")

    with app.app_context():
        # Get the user_id of the created test user
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', ('testuser',)).fetchone()
            assert user is not None  # make sure the user was created
            user_id = user['id']

        # Now call the add_task function
        task_added = add_task("Finish Unit Test", user_id, "2025-04-26")
        assert task_added is True  # Ensure the function returned True

        # Now check if the task was actually inserted into the database
        with get_db_connection() as conn:
            task = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchone()
            assert task is not None
            assert task['task'] == "Finish Unit Test"
            assert task['date'] == "2025-04-26"
            assert task['user_id'] == user_id

        # Remove test user
        removed = remove_test_user(client, app, "testuser")
        assert removed is True

def test_add_task_failure(app, client):
    """
    Test the add_task function to ensure that invalid tasks are handled gracefully
    :param app: Flask app instance
    :param client: Test client that was created for testing the app
    """
    # Create a test user (optional in this case if you want)
    register_test_user(client, "testuser", "testpassword")

    with app.app_context():
        # Get the user_id of the created test user
        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', ('testuser',)).fetchone()
            assert user is not None
            user_id = user['id']

        # Now simulate a failure
        # Intentionally break it: pass invalid SQL parameters

        # Passing None as task_date should break if the database expects NOT NULL
        task_added = add_task("Invalid Task", user_id, None)
        assert task_added is False  # It should fail and return False

        # Clean up
        removed = remove_test_user(client, app, "testuser")
        assert removed is True

def test_delete_task_success(app, client):
    """
    Test the delete_task function to ensure that valid tasks are deleted successfully
    :param app: Flask app instance
    :param client: Test client that was created for testing the app
    """
    # Step 1: Register and log in a test user
    register_test_user(client, "testusername", "testpassword")

    client.post("/login", data={
        "username": "testusername",
        "password": "testpassword"
    }, follow_redirects=True)

    with app.app_context():
        with get_db_connection() as conn:
            # Get user_id
            user = conn.execute('SELECT * FROM users WHERE username = ?', ("testusername",)).fetchone()
            user_id = user['id']

            # Insert a test task manually
            conn.execute('INSERT INTO tasks (task, date, user_id) VALUES (?, ?, ?)', 
                         ("Test Task", "2024-04-27", user_id))
            conn.commit()

            # Fetch the task ID
            task = conn.execute('SELECT * FROM tasks WHERE user_id = ? AND task = ?', 
                                (user_id, "Test Task")).fetchone()
            task_id = task['id']

    # Step 2: Use Flask's test_request_context to fake a request with the session
    with app.test_request_context():
        # Set the user_id manually in the session
        session['user_id'] = user_id

        response = delete_task(task_id)

    # Step 3: Check that the response is a redirect
    assert response.status_code == 302  # Redirect to home

    # Step 4: Confirm the task was actually deleted
    with app.app_context():
        with get_db_connection() as conn:
            deleted_task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
            assert deleted_task is None  # Should not exist anymore

    # Step 5: Clean up user
    remove_test_user(client, app, "testusername")

def test_clear_database(app, client):
    """
    Test the clear_database function that occurs when the user clicks the clear tasks button
    in the app
    :param app: Flask app instance
    :param client: Test client that was created for testing the app
    """
    # clear_all_tasks button
    register_test_user(client, "testusername", "testpassword")

    # Log in the user
    response = client.post("/login", data={
        "username": "testusername",
        "password": "testpassword"
    }, follow_redirects=True)
    assert response.status_code == 200

    # Get user_id from session by querying DB
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', ("testusername",))
            user = cursor.fetchone()
            assert user is not None
            user_id = user["id"]

    # Add a few tasks for this user
    task_1 = "Task One"
    task_2 = "Task Two"
    task_date = "2025-04-30"

    with app.app_context():
        add_task(task_1, user_id, task_date)
        add_task(task_2, user_id, task_date)

    # Now clear all tasks for the logged-in user
    response = client.post("/clear", follow_redirects=True)
    assert response.status_code == 200

    # Verify that tasks for this user are now gone
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
            tasks = cursor.fetchall()
            assert len(tasks) == 0

    # Clean up the test user
    removed = remove_test_user(client, app, "testusername")
    assert removed is True

def test_logout(app, client):
    """
    Test the logout functionality to ensure that users can log out successfully
    :param app: Flask app instance
    :param client: Test client that was created for testing the app
    """
    # Register and log in a test user
    register_test_user(client, "testusername", "testpassword")
    
    response = client.post("/login", data={
    "username": "testusername",
    "password": "testpassword"
    })

    assert response.status_code == 302  # Check for redirect after successful login

    with client.session_transaction() as sess:
        assert "user_id" in sess

    logout_response = client.get("/logout", follow_redirects=True)
    assert logout_response.status_code == 200  # Check for successful logout
    
    with client.session_transaction() as sess:
        assert "user_id" not in sess

    removed = remove_test_user(client, app, "testusername")
    assert removed is True

