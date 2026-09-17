# Flashcard Generator API

**v1.1 — LLM-backed card generation with a rule-based fallback. No authentication or frontend yet.**
 
A REST API that generates study flashcards from a block of text. Cards are
stored in PostgreSQL with full CRUD.

---

## How it works
 
There are two generators:
 
- **Gemini** (`app/generators/llm.py`) sends the text to the Gemini API and asks
  for flashcards in a fixed JSON shape.
- **Rules** (`app/generators/rules.py`) uses NLTK to split the text into
  sentences, then matches regex patterns for definitions, people, dates and
  locations, falling back to fill in the blank.


- `CARD_GENERATOR` in `.env` picks which one runs. It defaults to `rules`, so the
   project works straight after cloning with no API key. In the case the LLM fails
   it falls back to the rules engine.
 
---
 
## Why the generator was rewritten

The regex generator made bad cards, but “bad” wasn’t actionable. So I wrote a rubric and a fixed set of 20 texts (Git, Docker, OOP, data structures, SQL), 
ran both generators, shuffled the results into one A/B file, and graded them.

**A card is usable only if** it can be answered without the source, is correct, reads like a real question, and tests one fact.

| Generator | Cards made | Usable | Usable per text |
|-----------|-----------|--------|-----------------|
| Rules     | 20 | 12 (60%) | 0.60 |
| Gemini    | 40 | 39 (98%) | 1.95 |

**Per-text matters more:** rules makes at most one card per sentence, so even perfect patterns cap it at 1.0. 
Half the rules failures were one grammar bug: the date pattern pastes a fragment into “When did ___?” without fixing the verb (“When did GitHub was founded?”). 
Another card blanked “index” in a sentence starting “Indexes”, giving away its own answer.

Full results, rubric, and limits: [docs/evaluation.md](docs/evaluation.md).
 
---
---

## Tech Stack

| Technology     | Purpose                                    |
|----------------|--------------------------------------------|
| **Flask**      | Lightweight web framework for HTTP routing |
| **SQLAlchemy** | ORM for database operations                |
| **PostgreSQL** | Persistent data storage                    |
| **Docker**     | Containerized database setup               |
| **Gemini**     | LLM card generation via `google-genai`     |
| **NLTK**       | Sentence tokenization for the rules engine |
| **pytest**     | Automated API testing                      |

---

## Prerequisites

- Python 3.10 or newer (developed on 3.14)
- Git
- Docker Desktop (running)
- A Gemini API key, (free & optional). Works without one.

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

CARD_GENERATOR=rules
LLM_API_KEY=
LLM_MODEL=
```

You can also set `DATABASE_URL` as a single connection string. If you do, it
overrides every `DB_*` value above.

To use Gemini, set 'CARD_GENERATOR=llm' and fill in 'LLM_API_KEY' and 'LLM_MODEL'
with a key and model ID from Google AI Studio. (Model I used: gemini-3.5-flash-lite)

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

| Method | Endpoint          | Description                     |
|--------|-------------------|---------------------------------|
| GET    | `/`               | API information                 |
| POST   | `/cards/generate` | Generate flashcards from text   |
| GET    | `/cards`          | List all flashcards (paginated) |
| GET    | `/cards/<id>`     | Get a single flashcard          |
| PUT    | `/cards/<id>`     | Update a flashcard              |
| DELETE | `/cards/<id>`     | Delete a flashcard              |

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
  -d '{"text": "Linus Torvald created Git in 2005.", "num_cards": 2}'
```

## Example Response

With 'CARD_GENERATOR=llm'. Rules engine would return one card from
the example sentence.

```json
{
  "message": "Successfully generated flashcards",
  "cards": [
    {
      "id": 1,
      "prompt": "Who created Git in 2005?",
      "response": "Linus Torvalds",
      "source": "Linus Torvalds created Git in 2005.",
      "topic": "general",
      "level": 1,
      "creation_date": "2026-09-13T21:15:04.221847",
      "updated_date": null
    },
    {
      "id": 2,
      "prompt": "In what year was Git created?",
      "response": "2005",
      "source": "Linus Torvalds created Git in 2005.",
      "topic": "general",
      "level": 1,
      "creation_date": "2026-09-13T21:15:04.221847",
      "updated_date": null
    }
  ]
}
```

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
tests/test_generator.py::test_good_response_is_parsed PASSED
tests/test_generator.py::test_empty_question_is_skipped PASSED
tests/test_generator.py::test_api_failure_falls_back_to_rules PASSED
 
12 passed
```

---


## Project Structure

```text
flashcardapi_Project/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Flask app entry point
│   ├── config.py                # Environment-based configuration
│   ├── database.py              # SQLAlchemy engine & sessions
│   ├── models.py                # StudyCard model
│   ├── routes.py                # API endpoints
│   └── generators/
│       ├── __init__.py          # Picks a generator, falls back to rules
│       ├── llm.py               # Gemini card generation
│       └── rules.py             # Regex card generation
├── tests/
│   ├── __init__.py
│   ├── test_api.py              # Endpoint tests
│   ├── test_generator.py        # Generator tests, Gemini API mocked
│   └── fixtures/
│       ├── __init__.py
│       └── eval_texts.py        # Fixed evaluation set
├── scripts/
│   └── evaluate.py              # Evaluation harness
├── docs/
│   ├── evaluation.md            # Rubric, method and results
│   └── debug_log.md             # Issues found while working on this
├── docker-compose.yml           # PostgreSQL container
├── setup_db.py                  # One-off table creation
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Known Limitations

Things I know are wrong. Some are on the roadmap below.

- **Gemini is non-deterministic** — the same text can produce different cards on different runs.


- **Gemini answers from its own knowledge when input is thin.** 
Two test texts were single words, and it made correct cards from facts not in the input.


- **The Gemini Interactions API is in beta** and can change.


- **The rules fallback makes noticeably worse cards:** inverted definitions, 
ungrammatical date questions, and names with a lowercase particle ("Guido van Rossum") not matched at all.


- **The rules fallback is capped at one card per sentence**, so it can never split a sentence with two facts.


- **`num_cards` is not type checked** — a string returns 500 instead of 400.


- **No authentication.** Anyone who can reach the port can read, edit, or delete any card.


- **`create_all()` adds missing tables but won't alter existing ones**, 
so adding a column means dropping the table.


- **Tests run against the dev database** and leave their rows behind.
---

## Roadmap

- Input validation, so bad requests return 400 instead of 500
- A separate test database
- Deck support to organise cards
- A web frontend for creating and studying cards, with the API deployed so it
  can be used from a browser
- User authentication

---

## License

MIT
