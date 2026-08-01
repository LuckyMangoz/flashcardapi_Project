import os

from dotenv import load_dotenv

load_dotenv()

# Settings

DB_USER = os.getenv("DB_USER", "LuckyMango")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "flashcard_project")

ADMIN_KEY = os.getenv("ADMIN_KEY", "dev")
DEBUG = os.getenv("DEBUG", "False") == "True"

MAX_CARDS = int(os.getenv("MAX_CARDS", "20"))
DEFAULT_CARDS_COUNT = int(os.getenv("DEFAULT_CARDS_COUNT", "5"))


def get_database_url():
    """Returns the PostgreSQL connection string"""
    return os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
