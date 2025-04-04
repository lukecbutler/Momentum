import pytest
import sqlite3
from app import *


@pytest.fixture
def client():
    """
    Creating a test client to test the app and database
    :yield: client
    """
    app.config['TESTING'] = True
    client = app.test_client()
    yield client
    
def test_get_db_connection():
    """
    Test if get_db_connection() returns a valid SQLite connection
    """
    with get_db_connection() as conn:
        assert isinstance(conn, sqlite3.Connection)

def test_home(client):
    """
    Test the home page to ensure that the all homepage functionality is present
    :param client: Test client that was created for testing the app
    """
    # 
    response = client.get('/')
    assert response.status_code == 200

    assert b"Add Task" in response.data  # Check if the "Add Task" button is present

def test_add_task_failure():
    """
    Test the add_task function to ensure that submissions of empty tasks are handled gracefully
    """
    test_task = ""

    # Add a task containing an empty string
    result = add_task(test_task)
    assert result is False

def test_add_task_success():
    """
    Test the add_task function to ensure that tasks are successfully added to the database
    """
    test_task = "TEST TASK"

    result = add_task(test_task)
    assert result is True # Check return value

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if the task was added to the database
        assert any(test_task in row for row in cursor.execute('SELECT task FROM tasks').fetchall())

# TODO: Complete test clear database function
def test_clear_database():
    """
    Test the clear_database function to ensure all items are cleared
    """

    with app.test_request_context():
        clear_database()   

    with get_db_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]        
        assert count == 0
        
        




