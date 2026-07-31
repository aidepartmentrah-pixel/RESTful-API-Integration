#!/bin/sh
# Updates an existing offline installation to a new release: loads the new
# images, re-runs migrations against the EXISTING database (data is preserved),
# and recreates only the containers whose image actually changed.
#
# Before running this, copy the new release's docker-images/*.tar files over
# (or alongside) this release's docker-images/ directory, and update
# API_IMAGE_TAG in compose/.env to the new version if it changed.
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose
require_env_file

log "This updates the running stack in place. The PostgreSQL data volume is preserved."
log "A backup is strongly recommended first (backup_database.sh) in case the update needs to be rolled back."
printf 'Continue with update? Type YES to proceed: '
read -r confirmation
[ "$confirmation" = "YES" ] || fail "Update cancelled."

log "Step 1/3: Loading Docker images from this release package ..."
"$(dirname -- "$0")/load_images.sh"

log "Step 2/3: Re-running migrations and recreating containers with the new image ..."
compose up -d

migrate_id="$(compose ps -a -q migrate)"
migrate_exit_code="$(docker inspect -f '{{.State.ExitCode}}' "$migrate_id" 2>/dev/null || echo unknown)"
if [ "$migrate_exit_code" != "0" ]; then
    fail "Migration step failed (exit code: $migrate_exit_code). The api container was NOT necessarily updated. Check show_logs.sh migrate, then see documentation/ROLLBACK notes (database/rollback/rollback_notes.md) before retrying."
fi

log "Step 3/3: Verifying the updated installation ..."
"$(dirname -- "$0")/verify_installation.sh"

log "Update complete. Existing database data was preserved (no volume was recreated)."
