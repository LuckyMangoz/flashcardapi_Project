# Debug log

## 2026-09-10 — Following my own README breaks the app

### What I did
Ran my README instructions on a clean volume:

    docker compose down -v
    docker compose up -d
    copy .env.example .env
    python setup_db.py

### What happened
    FATAL: password authentication failed for user "postgres"

But the server log said something else:

    docker logs flashcard-postgres --tail 20
    FATAL: role "postgres" does not exist

The error I saw and the real problem were different. Python said the password was wrong
The server log said the user "postgres" doesn't exist on this database so Python's
error message was misleading. This is understandable as then attackers cannot guess
valid accounts. Reading 'docker logs' took ten seconds and gave the correct error message.

### Root cause
`.env.example` and the README were written during the initial setup and
never touched again. Both still use the tutorial's values:

    .env.example        -> postgres   / flashcard_db
    docker-compose.yml  -> LuckyMango / flashcard_project
    config.py defaults  -> LuckyMango / flashcard_project

When I started this project I made my own .env file, then updated
config.py and docker-compose.yml to match it. I disregarded
.env.example, so it still shows the old values, and the README still
claims the defaults work with Docker.

I never noticed because .env.example and the README are the only files
I don't actually use. Everything else runs when I start the app or the
tests, so mistakes show up straight away. Those two only matter to
someone installing the project fresh.

What makes it confusing is that with no .env at all the app still
works, because config.py falls back to defaults that happen to be
correct:

    DB_USER = os.getenv("DB_USER", "LuckyMango")

So the app works with no config file, and breaks with the documented
one. Confirmed by deleting .env entirely then calling setup_db.py works.

I need to fix the setup guide so it actually works for a new user.

### Other things found
1. `setup_db.py` catches the error, prints a friendly message, and exits
   with code 0. So a setup that failed reports success, and anything
   running it automatically would think it worked.


2. The healthcheck runs `pg_isready -U postgres`, but the real user is
   LuckyMango. Postgres logs a FATAL every 5 seconds forever, and the
   container still says healthy. pg_isready only checks the server is
   running, never the login. My real error was buried in all that noise.
   A check that can't fail means nothing.


3. Fixing .env.example by hand wouldn't be enough. Line 1 sets
   DATABASE_URL, and `get_database_url()` reads that first, so it
   overrides every DB_ value below it.


4. Four variables in .env.example do nothing: FLASK_ENV, FLASK_DEBUG,
   SECRET_KEY, MAX_CARDS_PER_REQUEST. config.py doesn't read any of
   them. So setting MAX_CARDS_PER_REQUEST=10 quietly leaves the limit at
   20, since the real variable is MAX_CARDS. ADMIN_KEY is read but never
   used anywhere in the app.


5. My own .env had stray spaces (`DB_USER =LuckyMango`) and Windows line
   endings. python-dotenv cleans both up, so nothing broke, but
   `source .env` in a shell fails on those lines. The file only worked
   with one tool. Already cleaned up.


6. `.pytest_cache` isn't in .gitignore. Not committed yet, but one
   `git add .` would do it.


7. `docker compose` warns the `version` line is obsolete, every command.

### Environment note (not a repo bug)
`python` was running the global 3.14 install, not the venv. Both had the
project's packages, which is why setup_db.py worked but pytest wasn't
found. Fixed with `.venv\Scripts\Activate.ps1`. Needs to stay activated.