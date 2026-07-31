# Backup and Restore Guide

## Backup

```bash
sh scripts/backup_database.sh [optional output directory]
```

- Defaults to writing into `release/backups/`.
- Produces a gzip-compressed `pg_dump` (`hospital_directory_YYYYMMDD_HHMMSS.sql.gz`).
- Runs entirely via `docker exec` into the running `postgres` container — no
  PostgreSQL client tools are required on the host.
- The backup file lives on the host filesystem, **outside** the Docker volume.
  Copy it to a second location (external drive, another server) — a backup
  that only exists on the same disk as the live database does not protect you
  against disk failure.

Recommended cadence: before every update (see `UPDATE_OFFLINE.md`), and on
whatever regular schedule your hospital's data retention policy requires.

## Restore

```bash
sh scripts/restore_database.sh path/to/hospital_directory_20260714_120000.sql.gz
```

This is **destructive**: it drops and recreates the target database, so it
asks for a typed `YES` confirmation before doing anything. Steps performed:

1. Stops the `api` container (so nothing serves requests against a
   half-restored database).
2. Drops and recreates the `hospital_directory` database (name from `.env`).
3. Restores the dump into the fresh database.
4. Restarts the `api` container.

Afterward, run:

```bash
sh scripts/verify_installation.sh
```

to confirm the restored database is healthy and the API is serving correctly.

## What backup/restore does NOT cover

- **Docker images** — those are restored separately by re-running
  `scripts/load_images.sh` from a release package, not by `restore_database.sh`.
- **`.env` secrets** — back these up separately (e.g. a password manager),
  since `backup_database.sh` only dumps the database, not `compose/.env`.
- **Point-in-time recovery** — these are logical `pg_dump` snapshots, not WAL
  archiving. If you need point-in-time recovery, that is a larger PostgreSQL
  operations topic outside this mock API package's scope.
