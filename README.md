# Flashcard Generator API

**Version V1.0.0 (Core API only, no authentication / AI / frontend)**

A REST API that automatically generates flashcards from any text using pattern-matching and NLTK sentence tokenization
Built with Flask, SQLAlchemy and PostgreSQL

---

## Tech Stack

| Technology     | Purpose                                    |
|----------------|--------------------------------------------|
| **Flask**      | Lightweight web framework for HTTP routing |
| **SQLAlchemy** | ORM for database operations                |
| **PostgreSQL** | Persistent data storage                    |
| **Docker**     | Containerized database setup               |
| **NLTK**       | Robust sentence tokenization               |
| **pytest**     | Automated API testing                      |

---

## Prerequisites

- Python 3.8+
- Git
- Docker Desktop (running)
- IntelliJ IDEA (or your preferred IDE)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/LuckyMangoz/flashcard-api.git
   cd flashcard-api

2. **Set up environment variables**
   ```bash 
   cp .env.example .env
   ```
   Edit .env with your settings (defaults work with Docker):
   ``` bash
   DATABASE_URL=postgresql://postgres:password@localhost:5432/flashcard_db
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=flashcard_db
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=change-this-in-production
   MAX_CARDS_PER_REQUEST=10
   DEFAULT_CARDS_COUNT=5

3. **Start PostgreSQL**
   ```bash 
   docker-compose up-d
   # Verify if its running
   docker ps

4. **Install dependencies**
   ```bash 
   pip install -r requirements.txt

5. **Create the database tables**
   ```bash 
   python setup_db.py

6. **Run the server**
   ```bash 
   python -m app.main

The API will be available at http://localhost:5000

---

## API Endpoints

| Method | Endpoint          | Description                     |
|--------|-------------------|---------------------------------|
| GET    | `/`               | API information & health check  |
| POST   | `/cards/generate` | Generate flashcards from text   |
| GET    | `/cards`          | List all flashcards (paginated) |
| GET    | `/cards/<id>`     | Get a single flashcard          |
| PUT    | `/cards/<id>`     | Update a flashcard              |
| DELETE | `/cards/<id>`     | Delete a flashcard              |

---

## Example Request

```bash
curl -X POST http://localhost:5000/cards/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Python is a programming language created by Guido van Rossum in 1991.", "num_cards": 3}'
```

## Example response

```bash
{
  "message": "Successfully created 3 card(s).",
  "cards": [
    {
      "id": 1,
      "prompt": "What is a programming language?",
      "response": "Python",
      "type": "definition",
      "level": 1,
      "topic": "general"
    }
  ]
}
```

## Running tests

```bash 
pytest tests/test_api.py -v
or
.\.venv\Scripts\python -m pytest tests/test_api.py -v
```

# Expected Output

```text
tests/test_api.py::test_home_route PASSED
tests/test_api.py::test_generate_no_text PASSED
tests/test_api.py::test_generate_empty_text PASSED
tests/test_api.py::test_generate_success PASSED
```

## Project Structure

```text
flashcard-api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Flask app entry point
│   ├── config.py                # Environment-based configuration
│   ├── database.py              # SQLAlchemy engine & sessions
│   ├── models.py                # StudyCard model
│   ├── routes.py                # API endpoints
│   └── flashcard_generator.py   # Rule-based card generation
├── tests/
│   ├── __init__.py
│   └── test_api.py              # pytest suite
├── docker-compose.yml           # PostgreSQL container
├── setup_db.py                  # One‑off table creation
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Future Plans (V1.1+)

Add deck support to organise flashcards

Implement user authentication

Integrate AI for the question generation

Build a frontend client

# License

MIT
