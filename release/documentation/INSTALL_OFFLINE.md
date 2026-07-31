# Offline Install Guide — Hospital Directory Mock API

This guide is written for an IT operator with limited Linux/Docker experience,
installing this package on a Debian server that has **no internet access** and
**Docker + the Docker Compose plugin already installed**.

## What you received

This entire `release/` folder, copied from a USB drive or DVD, e.g. to:

```
/opt/hospital-directory-api/release/
```

Everything the install needs is inside it — no downloads happen at any point.

## Step 0 — Copy the release folder onto the server

```bash
mkdir -p /opt/hospital-directory-api
cp -r /media/usb/release /opt/hospital-directory-api/
cd /opt/hospital-directory-api/release
```

## Step 1 — Create your environment file

Never use the shipped template as-is — it has no real password in it on purpose.

```bash
cp compose/.env.offline.template compose/.env
nano compose/.env
```

Fill in at minimum:

| Variable | What to put |
|---|---|
| `API_KEY` | A long random string. HCAT and HCopilot must be configured with this same value. |
| `POSTGRES_PASSWORD` | A strong password. Only used inside the Docker network. |
| `PGADMIN_DEFAULT_PASSWORD` | A strong password for the pgAdmin web login. |

Leave `API_IMAGE_NAME` / `API_IMAGE_TAG` matching what is printed by
`scripts/load_images.sh` (see `documentation/RELEASE_NOTES.md` for this
release's version).

Save and exit (in `nano`: `Ctrl+O`, Enter, `Ctrl+X`).

## Step 2 — Run the installer

```bash
sh scripts/install_offline.sh
```

This does three things, in order, and stops with a clear error if any step fails:

1. **Loads the Docker images** shipped in `docker-images/*.tar` (`docker load`) —
   this is the only supported way images get onto this server; there is no
   `docker pull`.
2. **Starts the stack** (`postgres` → `migrate` → `api`, plus `pgadmin`) and
   waits for the one-shot `migrate` container to finish applying the database
   schema and seeding data.
3. **Verifies** the installation: checks all containers are healthy, hits
   `/api/directory/v1/health`, and confirms authenticated/unauthenticated
   requests behave as expected.

Expected final output:

```
[...] All checks passed.
[...] Install complete.
[...]   API:     http://localhost:6000/api/directory/v1
[...]   pgAdmin: http://localhost:5050
```

## Step 3 — Confirm from a browser or another machine on the network

```
http://<server-ip>:6000/api/directory/v1/health
http://<server-ip>:6000/api/directory/v1/docs      (Swagger UI)
http://<server-ip>:5050                             (pgAdmin)
```

## If something goes wrong

Run `sh scripts/verify_installation.sh` again — it prints exactly which check
failed. Then see `documentation/TROUBLESHOOTING.md`.

## Re-running the installer

`install_offline.sh` is safe to re-run — it does not delete existing data.
If containers are already running, `start_stack.sh` just reconciles state.

## What this installer does NOT do

- It does not open firewall ports — the platform/network team is responsible
  for restricting access to this server per Document 1 section 17.
- It does not configure HTTPS. HTTPS termination in front of this API (e.g. via
  a reverse proxy) is a hospital-IT decision outside this package's scope.
- It does not register HCAT/HCopilot — those applications are configured
  separately with `HOSPITAL_API_BASE_URL` and `HOSPITAL_API_KEY` pointing at
  this server (see Document 1 section 23).
