#!/bin/sh
# First-time install on the air-gapped server. Loads images from this
# package, starts the stack, and verifies it. Safe to re-run.
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$COMPOSE_DIR/.env.offline.template" ]; then
        fail "$ENV_FILE not found. Copy it from the template and fill in real secrets first:
    cp '$COMPOSE_DIR/.env.offline.template' '$ENV_FILE'
    nano '$ENV_FILE'   # set API_KEY, POSTGRES_PASSWORD, PGADMIN_DEFAULT_PASSWORD
Then re-run this script."
    else
        fail "$ENV_FILE not found and no template is present in $COMPOSE_DIR."
    fi
fi

log "Step 1/3: Loading Docker images from this release package ..."
"$(dirname -- "$0")/load_images.sh"

log "Step 2/3: Starting the stack (postgres, migrate, api, pgadmin) ..."
"$(dirname -- "$0")/start_stack.sh"

log "Step 3/3: Verifying the installation ..."
"$(dirname -- "$0")/verify_installation.sh"

host_port="$(grep '^HOST_PORT=' "$ENV_FILE" | cut -d= -f2)"
pgadmin_port="$(grep '^PGADMIN_HOST_PORT=' "$ENV_FILE" | cut -d= -f2)"

log "Install complete."
log "  API:     http://localhost:${host_port:-6000}/api/directory/v1"
log "  pgAdmin: http://localhost:${pgadmin_port:-5050}"
log "See documentation/VALIDATION_CHECKLIST.md for the full manual sign-off checklist."
