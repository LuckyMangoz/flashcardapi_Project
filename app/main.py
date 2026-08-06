from flask import Flask
from app.config import get_database_url
from app.database import db_engine, db_base
from app.routes import cards_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(get_database_url)
    app.register_blueprint(cards_bp)
    return app

def init_db():
    print("Initializing DB")
    db_base.metadata.create_all(bind=db_engine)

if __name__ == '__main__':
    init_db()
    app = create_app()
    print("Starting Flashcard API server")
    app.run(host='0.0.0.0', port=5000, debug=True)