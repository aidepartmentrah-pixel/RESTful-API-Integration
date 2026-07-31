#!/bin/sh
# Stops the stack without deleting the PostgreSQL data volume.
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose

log "Stopping stack (data volume is preserved) ..."
compose down

log "Stack stopped. The PostgreSQL data volume was NOT deleted."
log "To also delete data (irreversible, destroys the database), run:"
log "  docker compose -p '$COMPOSE_PROJECT_NAME' --project-directory '$COMPOSE_DIR' -f '$COMPOSE_FILE' --env-file '$ENV_FILE' down -v"
