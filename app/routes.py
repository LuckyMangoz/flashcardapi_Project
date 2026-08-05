from flask import Blueprint, request, jsonify
from app.database import get_gb
from app.models import StudyCard
from app.flashcard_generator import generate_cards
from app.config import MAX_CARDS, DEFAULT_CARDS_COUNT
from nltk import data

cards_bp = Blueprint('cards', __name__)


@cards_bp.route('/', methods=['GET'])
def index():
    return jsonify({
        'app': 'Flashcard Generator API',
        'version': '1.0',
        'routes': {
            'POST /cards/generate': 'Create flashcards from text',
        }
    })


@cards_bp.route('/cards/generate', methods=['POST'])
def create_cards():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'Missing required field: text'}), 400

    text = data['text']
    if not text.strip():
        return jsonify({'error': 'Text cannot be empty.'}), 400

    how_many = min(data.get('num_cards', DEFAULT_CARDS_COUNT), MAX_CARDS)
    how_many = max(1, how_many)

    category = data.get('category', 'general')
    generated = generate_cards(text, how_many)

    if not generated:
        return jsonify({
            'message': 'No flashcards could be generated from the given text',
            'cards': []
        }), 200

    saved = []
    with get_gb() as db:
        try:
            for card_data in generated:
                new_card = StudyCard(
                    prompt = card_data['question'],
                    response = card_data['answer'],
                    source = text[:500],
                    topic = category,
                    level = card_data.get('difficulty', 1)
                )
                db.add(new_card)
                db.commit()
                db.refresh(new_card)

                card_dict = new_card.to_dict()
                card_dict['type'] = card_data('type', 'unknown')
                saved.append(card_dict)

            return jsonify({
                'message': 'Successfully generated flashcards',
                'cards': saved
            }), 201

        except Exception as e:
            db.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500

