#!/bin/sh
# Starts the full stack (postgres, migrate, api, pgadmin) using only local
# images loaded by load_images.sh. Never builds and never contacts a registry.
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose
require_env_file

log "Starting stack (postgres -> migrate -> api, pgadmin) ..."
compose up -d

log "Waiting for the migrate service to finish (schema + seed data) ..."
if ! compose wait migrate 2>/dev/null; then
    # Older docker compose versions do not support 'compose wait'; fall back to polling.
    # Use 'ps -a' throughout: a one-shot container that has already exited is
    # hidden by 'ps' without -a, which would otherwise look like it never ran.
    i=0
    while [ "$i" -lt 60 ]; do
        status="$(compose ps -a --format '{{.Name}} {{.State}}' 2>/dev/null | awk '/-migrate-/{print $2}')"
        case "$status" in
            exited) break ;;
        esac
        i=$((i + 1))
        sleep 2
    done
fi

migrate_exit_code="$(docker inspect -f '{{.State.ExitCode}}' "$(compose ps -a -q migrate)" 2>/dev/null || echo unknown)"
if [ "$migrate_exit_code" != "0" ]; then
    fail "Database migration/seed step did not complete successfully (exit code: $migrate_exit_code). Run show_logs.sh migrate for details."
fi
log "Database initialization completed successfully."

log "Waiting for the api container to report healthy (Docker HEALTHCHECK needs a startup grace period) ..."
i=0
api_status=""
while [ "$i" -lt 60 ]; do
    api_id="$(compose ps -q api)"
    if [ -n "$api_id" ]; then
        api_status="$(docker inspect -f '{{.State.Health.Status}}' "$api_id" 2>/dev/null || echo unknown)"
        [ "$api_status" = "healthy" ] && break
    fi
    i=$((i + 1))
    sleep 2
done

if [ "$api_status" != "healthy" ]; then
    fail "api container did not become healthy within the timeout (last status: $api_status). Run show_logs.sh api for details."
fi
log "api container is healthy."

log "Current container status:"
compose ps

log "Stack started. Run verify_installation.sh to confirm the API and database are healthy."
