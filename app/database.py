# Connection Bridge

from sqlalchemy import create_engine
from app.config import get_database_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_database_url
from contextlib import contextmanager

db_engine = create_engine(get_database_url(), echo=False)
db_session = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
db_base = declarative_base()


@contextmanager
def get_gb():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
