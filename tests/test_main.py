from unittest.mock import patch
from src import app
import pytest
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def mock_mongo():
    with patch('pymongo.MongoClient') as mock_client:
        mock_db = mock_client.return_value['todo_app']
        mock_users = mock_db['users']
        mock_todos = mock_db['todos']
        yield {
            'client': mock_client,
            'db': mock_db,
            'users': mock_users,
            'todos': mock_todos
        }


def test_home_route(client):
    response = client.get('/')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['message'] == 'Welcome to TODO API'


def test_home_alternate_route(client):
    response = client.get('/home')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['message'] == 'Welcome to TODO API'