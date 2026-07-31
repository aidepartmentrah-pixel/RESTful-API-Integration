# Migrations

Schema migrations are managed by **Alembic** — the migration files live in
`alembic/versions/` at the repository root, not in this folder. This folder
exists to document the migration workflow in the same place the validation
and rollback scripts live.

## Why no separate SQL install scripts

Alembic already provides a working, idempotent way to create the schema on an
empty database (`alembic upgrade head`) and the mock API's `docker-entrypoint.sh`
already runs it automatically. Duplicating that logic as hand-written
`001_create_schema.sql`-style scripts would create two sources of truth for the
same schema and risk drifting out of sync. Per the deployment decisions for this
project, Alembic remains the single schema authority; this folder only documents
how to operate it.

## Running migrations

```bash
# Apply all migrations up to the latest revision
alembic upgrade head

# Show current revision applied to the database
alembic current

# Show full migration history
alembic history --verbose
```

In Docker Compose, this happens automatically via the one-shot `migrate` service
(see `docker-compose.yml`), which the `api` service waits on before starting.

## Creating a new migration

```bash
# After changing a model in app/models/, generate a migration automatically
alembic revision --autogenerate -m "describe the change"

# Or write one by hand (required if autogenerate can't detect the change)
alembic revision -m "describe the change"
```

Review the generated file in `alembic/versions/` before committing — autogenerate
does not always produce the correct migration (e.g. for column renames).

## Applying migrations offline

The offline release package's `migrate` container image already bundles Alembic,
the migration files, and all Python dependencies — no internet access or package
manager is needed on the air-gapped server. See
`release/documentation/INSTALL_OFFLINE.md` for the full offline install flow.
