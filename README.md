# Hospital Directory Read API — Mock Implementation

Read-only mock implementation of the Hospital Directory Read API (`/api/directory/v1`), used by
HCAT and HCopilot during development. See the `docs/` source specification for the full
architectural decisions, OpenAPI contract, and field dictionary.

## Stack

- Python 3.12 / FastAPI / SQLAlchemy 2.0 / Pydantic 2
- PostgreSQL (schema managed by Alembic)
- Docker Compose: API + PostgreSQL + pgAdmin

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

This builds the API image, starts PostgreSQL, runs Alembic migrations, seeds fictional
development data (idempotent — skipped if data already exists), and starts the API.

| Service     | URL                                          |
|-------------|-----------------------------------------------|
| Mock API    | http://localhost:6000/api/directory/v1        |
| Swagger UI  | http://localhost:6000/api/directory/v1/docs   |
| pgAdmin     | http://localhost:5050                         |

Default API key (change in `.env`): `change_me`, sent via `X-API-Key` header.

Example:

```bash
curl http://localhost:6000/api/directory/v1/health

curl -H "X-API-Key: change_me" \
  "http://localhost:6000/api/directory/v1/doctors?q=cardio"
```

## Local development (without Docker)

```bash
python -m venv .venv
.venv/Scripts/activate       # Windows
pip install -r requirements-dev.txt

# requires a local PostgreSQL instance matching DATABASE_URL
alembic upgrade head
python -m seed.seed_data
uvicorn app.main:app --reload --port 8000
```

## Tests

Tests run against an in-memory SQLite database (via dependency override) and do not require
Docker or PostgreSQL:

```bash
pytest -q
```

## Project structure

```
app/
  api/            FastAPI routers (health, patients, doctors, workers)
  core/           config, database session, security (API key), error types
  models/         SQLAlchemy ORM models
  schemas/        Pydantic request/response schemas
  repositories/   query logic
  services/       validation + orchestration between routers and repositories
  main.py         app factory, routing, exception handlers
alembic/          schema migrations (source of truth for the DB schema)
seed/             fictional development data generator
tests/            pytest suite (health, auth, patients, doctors, workers)
```

## Contract compatibility

This mock API and the future production API must expose identical externally observable
behavior (paths, parameters, field names, types, status codes, auth). Only the data source
differs. See `Hospital_Directory_API_OpenAPI.yaml` for the authoritative contract.

## Real vendor evidence

`real-evidence/` holds raw, unedited captures from actual HTTP round trips against the real
vendor server (not this mock) — confirmed facts, with sources, not inference. Check there
before assuming something about the real server's behavior is unknown.
