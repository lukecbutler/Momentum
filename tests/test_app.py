import pytest
import sqlite3
from app import *
from werkzeug.security import generate_password_hash


# @pytest.fixture
# def client():
#     """
#     Creating a test client to test the app and database
#     :yield: client
#     """
#     app.config['TESTING'] = True
#     client = app.test_client()
#     yield client
    
# def test_get_db_connection():
#     """
#     Test if get_db_connection() returns a valid SQLite connection
#     """
#     with get_db_connection() as conn:
#         assert isinstance(conn, sqlite3.Connection)

# def test_login_success(client):
#     """
#     Test the login functionality to ensure a user login is successful
#     :param client: Test client that was created for testing the app"""
#     # Mock a user in the database
#     with get_db_connection() as conn:
#         conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
#                     ("testuser", generate_password_hash("testpass")))
#         conn.commit()
    
#     response = client.post("/login", data={
#         "username": "testuser",
#         "password": "testpass"
#     })
#     assert response.status_code == 302  # Redirect to home
#     assert "/home" in response.location

# def test_register_duplicate_username(client):
#     """
#     Test the registration functionality to ensure that a duplicate username is not valid
#     :param client: Test client that was created for testing the app
#     """
#     # Mock an existing user
#     with get_db_connection() as conn:
#         conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
#                     ("testuser", "hash"))
#         conn.commit()
    
#     response = client.post("/register", data={
#         "username": "testuser",
#         "password": "newpass"
#     })
#     assert b"Username already exists" in response.data


# def test_home(client):
#     """
#     Test the home page to ensure that the all homepage functionality is present
#     :param client: Test client that was created for testing the app
#     """
#     # 
#     response = client.get('/')
#     assert response.status_code == 200


# def test_add_task_failure():
#     """
#     Test the add_task function to ensure that submissions of empty tasks are handled gracefully
#     """
#     test_task = None

#     # Add a task containing an empty string
#     result = add_task(test_task, user_id=1)
#     assert result is False

# def test_add_task_success():
#     """
#     Test the add_task function to ensure that tasks are successfully added to the database
#     """
#     test_task = "TEST TASK"

#     result = add_task(test_task, user_id=1)
#     assert result is True # Check return value

#     with get_db_connection() as conn:
#         cursor = conn.cursor()

#         # Check if the task was added to the database
#         assert any(test_task in row for row in cursor.execute('SELECT task FROM tasks').fetchall())

# def test_clear_database():
#     """
#     Test the clear_database function to ensure all items are cleared
#     """

#     with app.test_request_context():
#         clear_database()   

#     with get_db_connection() as conn:
#         count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]        
#         assert count == 0


def test_register(client):
    """
    Test the registration functionality to ensure that a new user can register successfully
    :param client: Test client that was created for testing the app
    """
    response = client.post("/register", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 302  # Redirect to login page
    assert "/login" in response.location
    assert b"login" in response.data.lower()




