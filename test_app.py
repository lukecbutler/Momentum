import pytest
import sqlite3
import random
from app import get_db_connection, init_db, add_task

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

@pytest.fixture
def in_memory_db(monkeypatch):
    """
    Fixture to create an in-memory SQLite database for testing.
    """
    def mock_get_db_connection():
        return sqlite3.connect(":memory:")  # In-memory database

    monkeypatch.setattr("app.get_db_connection", mock_get_db_connection)

    # Initialize DB and insert a single user for all tests
    init_db()

    yield get_db_connection  # This will be the in-memory connection

def test_init_db(in_memory_db):

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

def test_add_task_success(in_memory_db):
    # TODO: The problem is that the add_task is calling the database
    # that is being used in the app.py file, not the in-memory one.
    # This is a problem because the in-memory one is not being used in the app.py file.
    # TODO: FIGURE THIS OUT TOMORROW

    # Insert user into the users table for the foreign key reference
    test_user = random.randint(1, 1000000)  # Random user ID for testing
    with get_db_connection() as conn:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (test_user, 'testpass1'))
        conn.commit()

    # Now, test adding a task
    task = "Test Task"
    user_id = test_user  # The user_id of the user we just added
    task_date = "2025-04-26"
    
    result = add_task(task, user_id, task_date)

    # Check that the task was added successfully
    assert result == True
    
    # Verify that the task was inserted into the tasks table
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT task, date, user_id FROM tasks WHERE user_id = ?", (user_id,))
        task_data = cursor.fetchone()
        
        assert task_data is not None
        assert task_data[0] == task  # Task name
        assert task_data[1] == task_date  # Task date
        assert task_data[2] == user_id  # User id












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

# def test_home(client):
#     """
#     Test the home page to ensure that the all homepage functionality is present
#     :param client: Test client that was created for testing the app
#     """
#     # 
#     response = client.get('/')
#     assert response.status_code == 200

#     assert b"Add Task" in response.data  # Check if the "Add Task" button is present

# def test_add_task_failure():
#     """
#     Test the add_task function to ensure that submissions of empty tasks are handled gracefully
#     """
#     test_task = ""

#     # Add a task containing an empty string
#     result = add_task(test_task)
#     assert result is False

# def test_add_task_success():
#     """
#     Test the add_task function to ensure that tasks are successfully added to the database
#     """
#     test_task = "TEST TASK"

#     result = add_task(test_task)
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