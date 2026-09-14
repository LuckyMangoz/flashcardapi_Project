# Flashcard Generator API

**Version V1.0.0 (Core API only, no authentication / AI / frontend)**

A REST API that generates study flashcards from a block of text, using NLTK
sentence tokenization and rule-based pattern matching. Cards are stored in
PostgreSQL with full CRUD.


---

## Tech Stack

| Technology     | Purpose                                    |
|----------------|--------------------------------------------|
| **Flask**      | Lightweight web framework for HTTP routing |
| **SQLAlchemy** | ORM for database operations                |
| **PostgreSQL** | Persistent data storage                    |
| **Docker**     | Containerized database setup               |
| **NLTK**       | Sentence tokenization                      |
| **pytest**     | Automated API testing                      |

---

## Prerequisites

- Python 3.10 or newer (developed on 3.14)
- Git
- Docker Desktop (running)
- IntelliJ IDEA (or your preferred IDE)

## Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/LuckyMangoz/flashcardapi_Project.git
cd flashcardapi_Project
```


**2. Create a virtual environment**

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, use `source .venv/bin/activate` instead.

**3. Set up environment variables**

```bash
cp .env.example .env
```

The values match `docker-compose.yml`, so it works as-is for local development.
You only need to edit `.env` if you change the database credentials in
`docker-compose.yml`.

```bash
DB_USER=LuckyMango
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=flashcard_project

DEBUG=True
MAX_CARDS=20
DEFAULT_CARDS_COUNT=5
```

You can also set `DATABASE_URL` as a single connection string. If you do, it
overrides every `DB_*` value above.

**4. Start PostgreSQL**

```bash
docker compose up -d
docker ps
```

Wait a few seconds after starting before connecting — Postgres takes a moment
to accept connections.

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Create the database tables**

```bash
python setup_db.py
```

**7. Run the server**

```bash
python -m app.main
```

The API will be available at http://localhost:5000

---

## API Endpoints

| Method | Endpoint          | Description       |
|--------|-------------------|-------------------|
| GET    | `/`               | API information   |
| POST   | `/cards/generate` | Generate flashcards from text |
| GET    | `/cards`          | List all flashcards (paginated) |
| GET    | `/cards/<id>`     | Get a single flashcard |
| PUT    | `/cards/<id>`     | Update a flashcard |
| DELETE | `/cards/<id>`     | Delete a flashcard |

### `POST /cards/generate`
 
| Field       | Type    | Required | Default | Notes                          |
|-------------|---------|----------|---------|--------------------------------|
| `text`      | string  | yes      | —       | Cannot be empty or whitespace  |
| `num_cards` | integer | no       | `5`     | Capped at `MAX_CARDS` (20)     |
| `category`  | string  | no       | general | Stored and returned as `topic` |
 
### `GET /cards`
 
| Query param | Type    | Default | Notes          |
|-------------|---------|---------|----------------|
| `page`      | integer | `1`     |                |
| `per_page`  | integer | `10`    | Capped at `50` |
 
### `PUT /cards/<id>`
 
Accepts any of `prompt`, `response`, `topic`, `level`. Fields you omit are left
unchanged.

---

## Example Request

```bash
curl -X POST http://localhost:5000/cards/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Linus Torvalds developed the Linux kernel.", "num_cards": 1}'
```

## Example Response

```json
{
  "message": "Successfully generated flashcards",
  "cards": [
    {
      "id": 1,
      "prompt": "Who developed the Linux kernel?",
      "response": "Linus Torvalds",
      "source": "Linus Torvalds developed the Linux kernel.",
      "topic": "general",
      "level": 2,
      "type": "person",
      "creation_date": "2026-09-11T21:15:04.221847",
      "updated_date": null
    }
  ]
}
```

Note that `type` appears in this response but is not stored. Fetching the same
card with `GET /cards/<id>` will not include it.

---

## Running Tests

With the virtual environment active and PostgreSQL running:

```bash
pytest tests/test_api.py -v
```

If `pytest` isn't found, the virtual environment isn't active:

```bash
.\.venv\Scripts\python -m pytest tests/test_api.py -v
```

### Expected output

```text
tests/test_api.py::test_home_route PASSED
tests/test_api.py::test_generate_flashcards_no_text PASSED
tests/test_api.py::test_generate_flashcards_empty_text PASSED
tests/test_api.py::test_generate_flashcards_success PASSED
tests/test_api.py::test_list_all_flashcards PASSED
tests/test_api.py::test_get_single_flashcard PASSED
tests/test_api.py::test_get_nonexistent_flashcard PASSED
tests/test_api.py::test_update_flashcard PASSED
tests/test_api.py::test_delete_flashcard PASSED

9 passed
```

---


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

---

## Known Limitations

- **Card quality varies with sentence structure.** Definitions get inverted into
  questions that can be hard to answer without the source text. Date questions
  are assembled from fragments and are sometimes ungrammatical.
- **Names with surnames are not detected.** Person matching requires two
  consecutive capitalised words, so "Guido van Rossum" produces no person card.
- **No authentication.** Anyone who can reach the port can read, update or
  delete any card.
- **`type` is returned but not persisted.** It appears on generation and is
  absent on every subsequent fetch.
- **Schema changes use `create_all()`**, which creates missing tables but never
  alters existing ones.
- **Tests run against the development database** and leave rows behind.
---

## Roadmap

- Replace the rule-based generator with an LLM-backed one, keeping the rule
  engine as a backup
- Persist the card type
- Separate test database
- Deck support to organise cards
- A web frontend for creating and studying cards, with the API deployed so it
  can be used from a browser
- User authentication

---

## License

MIT
