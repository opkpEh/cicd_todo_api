from unittest.mock import MagicMock
import sys

# Mock pymongo before importing app
mock_mongo = MagicMock()
sys.modules['pymongo'] = mock_mongo
sys.modules['pymongo.MongoClient'] = mock_mongo

import pytest
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_mock_db():
    """Set up mock database and collections"""
    # Create mock collections
    mock_users = MagicMock()
    mock_todos = MagicMock()

    # Configure mock responses
    mock_users.find_one.return_value = None
    mock_users.find.return_value = []
    mock_todos.find.return_value = []

    # Create mock db
    mock_db = MagicMock()
    mock_db.__getitem__.side_effect = lambda x: mock_users if x == 'users' else mock_todos

    # Configure MongoClient mock
    mock_mongo.MongoClient.return_value.__getitem__.return_value = mock_db

    yield {
        'users': mock_users,
        'todos': mock_todos,
        'db': mock_db
    }


def test_home_route(client):
    """Test the home route returns correct message and status code"""
    response = client.get('/')
    data = response.get_json()

    assert response.status_code == 200
    assert data['message'] == 'Welcome to TODO API'


def test_home_alternate_route(client):
    """Test the alternate /home route returns same response"""
    response = client.get('/home')
    data = response.get_json()

    assert response.status_code == 200
    assert data['message'] == 'Welcome to TODO API'