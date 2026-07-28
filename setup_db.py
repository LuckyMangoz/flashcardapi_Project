from app.database import db_engine, db_base
from app.models import StudyCard

def init_db():
    try:
        print("Setting up database...")
        db_base.metadata.create_all(db_engine)
        print("Tables complete")
        print(f"Table '{StudyCard.__tablename__}' is available.")

    except Exception as e:
        print(f"Error, something went wrong: {e}")

if __name__ == "__main__":
    init_db()