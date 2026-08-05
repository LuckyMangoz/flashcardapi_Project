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
            'GET /cards': 'List all flashcards',
            'GET /cards/<id>': 'Get a single flashcard',
            'PUT /cards/<id>': 'Update a flashcard',
            'DELETE /cards/<id>': 'Delete a flashcard',
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
                    prompt=card_data['question'],
                    response=card_data['answer'],
                    source=text[:500],
                    topic=category,
                    level=card_data.get('difficulty', 1)
                )
                db.add(new_card)
                db.commit()
                db.refresh(new_card)

                card_dict = new_card.to_dict()
                card_dict['type'] = card_data.get('type', 'unknown')
                saved.append(card_dict)

            return jsonify({
                'message': 'Successfully generated flashcards',
                'cards': saved
            }), 201

        except Exception as e:
            db.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500


@cards_bp.route('/cards', methods=['GET'])
def list_cards():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 50)

    with get_gb() as db:
        total = db.query(StudyCard).count()
        cards = db.query(StudyCard) \
            .order_by(StudyCard.creation_date.desc()) \
            .offset((page - 1) * per_page) \
            .limit(per_page) \
            .all()

    return jsonify({
        'cards': [c.to_dict() for c in cards],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })


@cards_bp.route('/cards/<int:card_id>', methods=['GET'])
def get_card(card_id):
    with get_gb() as db:
        card = db.query(StudyCard).filter(StudyCard.id == card_id).first()

    if not card:
        return jsonify({'error': 'Card not found.'}), 404

    return jsonify(card.to_dict())


@cards_bp.route('/cards/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    with get_gb() as db:
        card = db.query(StudyCard).filter(StudyCard.id == card_id).first()

        if not card:
            return jsonify({'error': 'Card not found.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON body provided.'}), 400

        if 'prompt' in data:
            card.prompt = data['prompt']
        if 'response' in data:
            card.response = data['response']
        if 'topic' in data:
            card.topic = data['topic']
        if 'level' in data:
            card.level = data['level']

        try:
            db.commit()
            db.refresh(card)
            return jsonify({'message': 'Card updated.', 'card': card.to_dict()})
        except Exception as e:
            db.rollback()
            return jsonify({'error': f'Update failed: {str(e)}'}), 500


@cards_bp.route('/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    with get_gb() as db:
        card = db.query(StudyCard).filter(StudyCard.id == card_id).first()

        if not card:
            return jsonify({'error': 'Card not found.'}), 404

        try:
            db.delete(card)
            db.commit()
            return jsonify({'message': 'Card deleted.', 'id': card_id})
        except Exception as e:
            db.rollback()
            return jsonify({'error': f'Deletion failed: {str(e)}'}), 500
