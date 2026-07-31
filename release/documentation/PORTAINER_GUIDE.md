# Deploying via Portainer

This stack can be deployed either via the command-line scripts in
`scripts/` (see `INSTALL_OFFLINE.md`) or via Portainer, if the offline server
runs Portainer for container management. Both approaches use the same
`compose/docker-compose.yml` and `compose/.env` — pick whichever your team is
more comfortable operating day-to-day.

## Prerequisite: images must already be loaded

Portainer cannot pull these images from a registry on an air-gapped server.
Load them first from the command line (this one step still needs a terminal):

```bash
sh scripts/load_images.sh
```

Confirm they're present: open Portainer → **Images**, and check that
`hospital-directory-api:1.0.0` (or the version in `RELEASE_NOTES.md`),
`postgres:16-alpine`, and `dpage/pgadmin4:latest` are all listed.

## Creating the stack

1. Open Portainer → your environment → **Stacks** → **Add stack**.
2. Name it, e.g. `hospital-directory-api`.
3. Under **Build method**, choose **Web editor**.
4. Open `compose/docker-compose.yml` from this release package in a text
   editor, copy its full contents, and paste them into Portainer's editor.
5. Scroll to **Environment variables**. Add each variable from
   `compose/.env.offline.template`, using your real values (the same ones you
   would put in `.env` for the CLI method) — at minimum `API_KEY`,
   `POSTGRES_PASSWORD`, `PGADMIN_DEFAULT_PASSWORD`, plus `API_IMAGE_NAME` /
   `API_IMAGE_TAG` matching the loaded images.
6. Click **Deploy the stack**.

## Verifying after deploy

1. **Stacks** → your stack → confirm `postgres` and `api` show a green/healthy
   indicator, and `migrate` shows **Exited (0)** (this is expected — it is a
   one-shot job, not a long-running service).
2. Click into the `migrate` container → **Logs** → confirm it ends with
   `Database initialization complete.` with no errors above it.
3. From a terminal (Portainer doesn't replace this check), run:
   ```bash
   sh scripts/verify_installation.sh
   ```

## Viewing logs

**Containers** → select a container (`api`, `postgres`, `migrate`, or
`pgadmin`) → **Logs**. Enable **Auto-refresh** to tail live output.

## Restarting a service

**Containers** → select the container → **Restart**. Note: restarting `api`
does not re-run migrations (that only happens when the `migrate` container is
recreated, e.g. on a stack update with a new image).

## Updating the stack later

1. Load the new release's images: `sh scripts/load_images.sh` (pointed at the
   new release folder).
2. **Stacks** → your stack → **Editor** → update `API_IMAGE_TAG` in the
   environment variables if the version changed → **Update the stack**.
3. Portainer recreates only the containers whose image changed — `postgres`
   and its volume are left alone.
4. Repeat the "Verifying after deploy" steps above.

For anything Portainer's UI doesn't cover well (backup/restore, destructive
`down -v`), fall back to the CLI scripts — see `BACKUP_RESTORE.md`.

## Stopping the stack

**Stacks** → your stack → **Stop**. This does not delete the PostgreSQL
volume. To remove the stack entirely including its volumes, use **Delete** and
explicitly confirm volume removal — treat this the same as `docker compose
down -v` (irreversible for the mock/dev dataset).
