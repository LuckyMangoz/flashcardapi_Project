import pytest
from app.main import create_app, init_db


@pytest.fixture
def client():
    """Create and configure a new app client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_route(client):
    """GET / should return 200 with JSON data"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert 'app' in data
    assert 'routes' in data


def test_generate_flashcards_no_text(client):
    """POST /cards/generate should return 400 without text"""
    response = client.post("/cards/generate", json={})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_generate_flashcards_empty_text(client):
    """POST /cards/generate should return 400 with empty text"""
    response = client.post('/cards/generate', json={'text': '  '})
    assert response.status_code == 400


def test_generate_flashcards_success(client):
    """POST /cards/generate should return 200 with JSON data"""
    response = client.post("/cards/generate", json={
        'text': 'Tyler, the Creator album Chromakopia (2024) recorded the strongest first-week sales of his career.',
        'num_cards': 2,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'cards' in data
    assert len(data['cards']) > 0

    first_card = data['cards'][0]
    assert 'prompt' in first_card
    assert 'response' in first_card
    assert 'type' in first_card
