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


def test_list_all_flashcards(client):
    """Get /cards should return a paged list with its page and number of cards"""
    client.post("/cards/generate", json={
        'text': 'The Earth orbits the Sun.',
        'num_cards': 1,
    })

    response = client.get("/cards")
    assert response.status_code == 200
    data = response.get_json()
    assert 'cards' in data
    assert 'total' in data
    assert 'page' in data
    assert 'per_page' in data
    assert 'total_pages' in data
    assert isinstance(data['cards'], list)
    assert len(data['cards']) >= 1


def test_get_single_flashcard(client):
    """GET /cards/<id> should return correct card"""
    response = client.post('/cards/generate', json={
        'text': 'The Earth orbits the Sun.',
        'num_cards': 1,
    })
    card_id = response.get_json()['cards'][0]['id']

    # Retrieval
    response = client.get(f'/cards/{card_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == card_id
    assert 'prompt' in data
    assert 'response' in data


def test_get_nonexistent_flashcard(client):
    """GET /cards/<id> for a non‑existent ID should return 404."""
    response = client.get('/cards/99999')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_update_flashcard(client):
    """PUT /cards/<id> should update only the provided fields."""
    response = client.post('/cards/generate', json={
        'text': 'Water freezes at 0 degrees Celsius.',
        'num_cards': 1
    })
    card_id = response.get_json()['cards'][0]['id']

    # Partially update it
    response = client.put(f'/cards/{card_id}', json={
        'response': '0 degrees C'
    })
    assert response.status_code == 200
    updated = response.get_json()['card']
    assert updated['response'] == '0 degrees C'
    # Prompt should still be there and unchanged
    assert 'prompt' in updated
    assert updated['prompt'] != ''


def test_delete_flashcard(client):
    """DELETE /cards/<id> should remove the card and return 404 if successful."""
    # Create a card to delete
    response = client.post('/cards/generate', json={
        'text': 'The capital of France is Paris.',
        'num_cards': 1
    })
    card_id = response.get_json()['cards'][0]['id']

    # Deletion
    response = client.delete(f'/cards/{card_id}')
    assert response.status_code == 200
    assert 'message' in response.get_json()

    # Verify Deletion
    response = client.get(f'/cards/{card_id}')
    assert response.status_code == 404
