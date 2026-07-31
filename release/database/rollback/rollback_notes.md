# Rollback Notes — Hospital Directory Mock API Database

## Schema rollback (Alembic)

The schema is managed entirely by Alembic. Rolling back the schema by one revision
is safe and reversible **only for schema structure** — it does not restore data
that a downgrade's `DROP TABLE`/`DROP COLUMN` would discard.

```bash
# Roll back one revision
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade 0001

# Roll back everything (drops all tables)
alembic downgrade base
```

Because migration `0001_initial_schema.py` creates the tables from nothing,
`alembic downgrade base` drops `patients`, `doctors`, and `workers` entirely.
Do not run this against a database containing real production data — see below.

Note: `0002_patient_person_model.py` replaced the original visit-based
`patient_visits` table with the person-level `patients` table. Its
`downgrade()` recreates `patient_visits` empty (best-effort) — it does not
reconstruct the original per-visit rows, since that data no longer exists in
`patients`.

## Data rollback

**Alembic does not back up or restore data.** If a migration or a bad deployment
has altered or lost data, the only safe rollback is restoring from a database
backup taken before the change, using `restore_postgres_database.sh` /
`release/scripts/restore_database.sh` and a `pg_dump` archive produced by
`backup_postgres_database.sh` / `release/scripts/backup_database.sh`.

There is no scripted way to "undo" data changes without a backup. Do not attempt
to hand-write a corrective script against production data — restore from backup
instead.

## Mock API specifically

The mock API's data is entirely fictional and reseeded via `python -m seed.seed_data`,
which is idempotent (it skips seeding if any `patients` row already exists).
For the mock/dev environment, "rollback" is usually simplest as:

```bash
docker compose down -v   # drops the postgres_data volume — mock data only
docker compose up -d     # migrate service recreates schema and reseeds
```

**Do not run `docker compose down -v` against the production deployment** — it
destroys the PostgreSQL data volume unconditionally. This is only acceptable for
the mock API's disposable, fictional dataset.

## Production API

The production API is implemented and operated by the external data company
against the hospital's real data source (Document 1 section 2, "Real API").
This mock API's schema and rollback procedures do not apply to that system.
