# Offline Update Guide

Use this when a new release package (new image tars, possibly new database
migrations) needs to replace a currently running installation, **without**
losing the existing PostgreSQL data.

## Before you start

1. **Back up first.** Always:
   ```bash
   sh scripts/backup_database.sh
   ```
   This writes a timestamped `.sql.gz` file under `release/backups/`. Copy it
   somewhere off this server before continuing.

2. Confirm which version is currently installed and which version you are
   installing — check `documentation/RELEASE_NOTES.md` in both the old and
   new release folders.

## Step 1 — Bring the new release's image tars onto the server

Copy the new release's `docker-images/*.tar` files into this release's
`docker-images/` directory (or point directly at the new release folder and
run its own `update_offline.sh` — either works, as long as `compose/.env`
carries over unchanged).

## Step 2 — Update `API_IMAGE_TAG` if the version changed

Edit `compose/.env` and set `API_IMAGE_TAG` to match the new version (see the
new release's `RELEASE_NOTES.md`). Leave every other value (passwords, ports,
API key) unchanged unless you are intentionally rotating them.

## Step 3 — Run the updater

```bash
sh scripts/update_offline.sh
```

This will:

1. Ask for confirmation (type `YES`).
2. Load the new images from `docker-images/`.
3. Run `docker compose up -d`, which recreates only the containers whose image
   actually changed (Docker Compose diffs the image digest) — `postgres` and
   its data volume are left untouched unless you deliberately changed the
   `postgres` image tag, which this package does not do between updates.
4. Re-run the `migrate` one-shot container against the **existing** database.
   Alembic only applies migrations newer than the database's current revision
   — it does not recreate tables that already exist.
5. Run `verify_installation.sh` automatically at the end.

## If the migration step fails

The script stops and tells you the migrate container's exit code. Do not
proceed to use the new `api` image — the previous `api` container is still
present (Compose does not remove a service that failed to become healthy). At
this point:

- Check `sh scripts/show_logs.sh migrate` for the actual error.
- If the new migration is broken, see `database/rollback/rollback_notes.md`
  and restore the backup taken in Step "Before you start" with
  `restore_database.sh`.

## Rolling back an update

There is no automatic "undo" for a schema migration. To roll back:

1. Restore the pre-update backup: `sh scripts/restore_database.sh <backup file>`.
2. Reinstall the previous release's images (its `docker-images/*.tar`) and set
   `API_IMAGE_TAG` in `.env` back to the previous version.
3. Run `sh scripts/start_stack.sh` again.

See `database/rollback/rollback_notes.md` for the full explanation of why data
rollback always means "restore a backup," not a scripted reversal.
