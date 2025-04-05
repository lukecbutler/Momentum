import pytest
import sqlite3
from login import *

@pytest.fixture
def client():
    """
    Creating a test client to test the app and database
    :yield: client
    """
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_register_success_unit():
    """
    Test the register() function directly
    """
    # Create a fake HTTP request environment, simulate a POST request
    with app.test_request_context(method="POST",
                                  data={"username": "TESTUSER",
                                        "password": "TESTPASSWORD"}):
        result = register()

        assert users["TESTUSER"] == "TESTPASSWORD"


def test_register_duplicate_unit():
    """
    Test the registration process to ensure that the user cannot create
    a username that already exists in the database
    """
    with app.test_request_context(method="POST",
                                  data={"username": "TESTUSER",
                                        "password": "TESTPASSWORD"}):
        result = register()

        assert result == "Username already exists! Please choose a different one."


def test_login_success_unit():
    """
    Test the login() function directly
    """
    with app.test_request_context(method="POST",
                                  data={"username": "TESTUSER",
                                        "password": "TESTPASSWORD"}):
        result = login()
        assert result == f"Welcome, TESTUSER! You are now logged in."

def test_invalid_login_unit():
    """
    Test the login for invalid username or password
    """
    with app.test_request_context(method="POST",
                                  data={"username": "INVALIDUSER",
                                        "password": "INVALIDPASSWORD"}):
        result = login()
        assert result == "Invalid username or password."

# def test_registration_success_http(client):
#     """
#     INTEGRATION TESTING: 
#     Test the registration process to ensure that the user can create
#     a username and password successfully
#     :param client: Test client that was created for testing the app
#     """
#     test_user = {"username": "TESTUSER", "password": "TESTPASSWORD"}

#     response = client.post('/register', data=test_user)
    
#     assert response.status_code == 302 # Or 200 for success?
#     assert test_user["username"] in users
#     assert users[test_user["username"]] == test_user["password"] # Check if the password is stored correctly

#     # assert b"Login" in response.data # TODO: Feasibility of this?
