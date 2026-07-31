# Database Structure Report

## Connection

- `app/core/config.py` reads `DATABASE_URL` from the environment (or `.env`
  for non-Docker local dev). No connection string is hardcoded anywhere in
  application code.
- `app/core/database.py` creates the SQLAlchemy engine/session and exposes
  `get_db()` as a FastAPI dependency.

## ORM models (`app/models/`)

| Table | Model | Purpose |
|---|---|---|
| `patients` | `Patient` | One row per patient **person** (`patient_id` is unique). Prior to migration `0002` this table was `patient_visits`, one row per *visit* with a patient repeated across rows — that model was dropped per the revised requirements (see `vendor-deliverable/API_Implementation_Requirements.md` section 1). |
| `doctors` | `Doctor` | One row per doctor. |
| `workers` | `Worker` | One row per hospital worker/employee. |

All externally-facing identifiers (`patient_id`, `doctor_id`, `employee_id`)
are stored and exposed as strings, per Document 1 section 7 — even though
nothing here requires it numerically, this avoids ever having to retrofit
string IDs later.

## Migrations

Managed by Alembic (`alembic/`, config in `alembic.ini`). Current head revision:
`0002` (`alembic/versions/0002_patient_person_model.py`) — `0001` created the
original visit-based schema; `0002` drops `patient_visits` and creates
`patients` in the person-level shape described above. See
`postgres/migrations/README.md` for day-to-day Alembic usage.

There are no raw hand-written SQL install scripts for schema creation — Alembic
is the single source of truth (see that README for why).

## Seed / bootstrap data

`seed/seed_data.py` (run via `python -m seed.seed_data`, invoked automatically
by the `migrate` container). It is idempotent: it checks for any existing
`patients` row and skips seeding entirely if found, so re-running it against
an already-seeded database is a no-op. It generates fictional Arabic/English
patient, doctor, and worker records per Document 4 section 5.

## Lookup / configuration data

This project has **no separate lookup tables or configuration tables** in the
database:

- Doctor specialties and departments, and worker job titles/departments, are
  free-text columns on the `doctors`/`workers` rows themselves, not foreign
  keys into a lookup table. `database/postgres/validation/validate_lookup_data.sql`
  checks the diversity of these values instead of checking lookup table
  contents.
- All configuration (API key, ports, base URL, database credentials) is
  supplied via environment variables per Document 1 sections 16/23, not stored
  in the database. `database/postgres/validation/validate_configuration.sql`
  instead validates database-level settings (encoding, Arabic round-trip).

## Users / access

No application-level user accounts or login exist (Document 1 section 16).
The only "user" relevant to the database layer is the PostgreSQL role the API
connects as (`POSTGRES_USER` in `.env`). See
`database/postgres/validation/validate_users.sql`.

## Fixes made while packaging this release

- Split the previously-combined "wait for postgres, migrate, seed, start api"
  logic (all in one `docker-entrypoint.sh`) into a dedicated one-shot `migrate`
  service (`migrate-entrypoint.sh`) that the `api` service now depends on via
  `condition: service_completed_successfully`. This avoids re-running
  migrations/seeding on every `api` container restart and gives operators a
  single, clearly-named place to look when database initialization fails.
- Added `database/postgres/validation/*.sql`, `database/postgres/rollback/rollback_notes.md`,
  and `database/postgres/migrations/README.md`, none of which existed before
  this packaging pass.
