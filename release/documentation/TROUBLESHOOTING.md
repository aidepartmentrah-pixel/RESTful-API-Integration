# Troubleshooting

Run `sh scripts/verify_installation.sh` first — it tells you which specific
check is failing. Then find that symptom below.

## "postgres container is healthy" — FAILED

```bash
sh scripts/show_logs.sh postgres
```

Common causes:
- `POSTGRES_PASSWORD` in `.env` was changed after the data volume was already
  initialized with the old password. PostgreSQL only sets the password on
  first initialization of an empty volume — changing `.env` afterward does not
  change the password inside the existing volume. Either revert `.env` to the
  original password, or (if this is a fresh, disposable install) remove the
  volume with `docker compose ... down -v` and reinstall.
- Disk full — check `df -h`.

## "migrate service completed successfully" — FAILED

```bash
sh scripts/show_logs.sh migrate
```

Common causes:
- Database not reachable yet (rare — the service waits on `postgres`'s
  healthcheck) — re-run `sh scripts/start_stack.sh`.
- A migration failed against existing data. Do not repeatedly re-run the
  installer against a broken schema — restore the last known-good backup
  instead (`BACKUP_RESTORE.md`) and check `database/rollback/rollback_notes.md`.

## "api container is healthy" — FAILED

```bash
sh scripts/show_logs.sh api
```

Common causes:
- `migrate` never completed (see above) — `api` will not become healthy until
  it does, by design (`depends_on: migrate: condition: service_completed_successfully`).
- Wrong `DATABASE_URL` derivation — check that `POSTGRES_USER`/`POSTGRES_PASSWORD`/
  `POSTGRES_DB` in `.env` are consistent between the `postgres` and `api`/`migrate`
  service (they read from the same `.env`, so this should not normally happen
  unless `.env` was hand-edited inconsistently).

## "health endpoint returns 200" — FAILED, but containers look healthy

- Check the port isn't blocked by a host firewall: `sudo ufw status` (if `ufw`
  is in use) or your platform's firewall tool.
- Confirm `HOST_PORT` in `.env` matches the port you're testing against.

## "missing API key returns 401" — FAILED (got something else)

- If you got `200`, something is misconfigured — the health check test itself
  sends no key and must be rejected. Re-check `app`/`API_KEY` wiring; this
  would indicate a modified image, not a config issue, and should be reported.

## "authenticated doctors search returns 200" — FAILED

- Confirm `API_KEY` in `.env` is non-empty and matches what you're sending
  from HCAT/HCopilot's configuration.
- A `401` here means the key sent doesn't match `API_KEY` in `.env` exactly
  (check for accidental trailing whitespace/newline when it was pasted in).

## pgAdmin won't log in

- Confirm you're using `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD`
  from `.env`, not a previously-registered login — pgAdmin only re-reads these
  on first container initialization, same caveat as the PostgreSQL password
  above.

## Nothing works and you want to start clean (mock/dev environment only)

```bash
sh scripts/stop_stack.sh
docker compose -p hospital-directory-api --project-directory compose -f compose/docker-compose.yml --env-file compose/.env down -v
sh scripts/install_offline.sh
```

**`down -v` deletes the database volume.** Do this only for the disposable
mock/dev dataset — never on a deployment holding real data without a fresh
backup already safely stored elsewhere.

## Still stuck

Collect these before escalating:

```bash
docker compose -p hospital-directory-api --project-directory compose -f compose/docker-compose.yml --env-file compose/.env ps -a > /tmp/status.txt
sh scripts/show_logs.sh postgres > /tmp/postgres.log
sh scripts/show_logs.sh migrate  > /tmp/migrate.log
sh scripts/show_logs.sh api      > /tmp/api.log
```
