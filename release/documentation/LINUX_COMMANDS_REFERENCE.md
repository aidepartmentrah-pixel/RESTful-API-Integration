# Linux Commands Reference (for operators new to Linux/Docker)

Every command below is safe to copy-paste exactly as written, run from inside
the `release/` folder unless noted otherwise.

## Checking things

```bash
# Is Docker installed and running?
docker --version
docker info

# What containers exist and what state are they in?
docker compose -p hospital-directory-api --project-directory compose -f compose/docker-compose.yml --env-file compose/.env ps -a

# Follow live logs for one service (Ctrl+C to stop watching)
sh scripts/show_logs.sh api -f
sh scripts/show_logs.sh postgres -f
sh scripts/show_logs.sh migrate

# Disk space used by Docker
docker system df
```

## Starting / stopping

```bash
sh scripts/start_stack.sh     # start everything
sh scripts/stop_stack.sh      # stop everything, KEEPS data
```

## Editing the environment file

```bash
nano compose/.env
```

- Arrow keys to move, type to edit.
- `Ctrl+O` then Enter to save.
- `Ctrl+X` to exit.
- After editing, run `sh scripts/start_stack.sh` again to apply changes (Compose
  only recreates containers whose configuration actually changed).

## Copying files onto/off the server

```bash
# From a USB drive mounted at /media/usb
cp -r /media/usb/release /opt/hospital-directory-api/

# Checking a file's checksum matches what shipped on the DVD
sha256sum -c checksums/SHA256SUMS.txt
```

## Common gotchas

| Symptom | Likely cause |
|---|---|
| `permission denied` running `docker ...` | Your user isn't in the `docker` group. Run with `sudo`, or ask an admin to add you: `sudo usermod -aG docker $USER` then log out/in. |
| `docker: command not found` | Docker Engine isn't installed on this server — that's a prerequisite this package assumes is already done. |
| A script says `.env not found` | You skipped copying `compose/.env.offline.template` to `compose/.env`. See `INSTALL_OFFLINE.md` Step 1. |
| Port already in use | Something else on the server is using port 6000/5433/5050. Change `HOST_PORT`/`POSTGRES_HOST_PORT`/`PGADMIN_HOST_PORT` in `compose/.env`. |

See `TROUBLESHOOTING.md` for deeper diagnostics.
