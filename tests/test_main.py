from src import app
import pytest
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data['message'] == 'Welcome to TODO API'

def test_home_route2(client):
    response= client.get('/home')
    data= json.loads(response.data)

    assert response.status_code == 200
    assert data['message'] == 'Welcome to TODO API'