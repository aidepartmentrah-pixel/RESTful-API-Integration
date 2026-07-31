#!/bin/sh
# Takes a logical backup of the PostgreSQL database using pg_dump run inside
# the postgres container (no host PostgreSQL client tools required).
# Usage: backup_database.sh [output-directory]
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose
require_env_file

# shellcheck disable=SC1090
. "$ENV_FILE"

POSTGRES_USER="${POSTGRES_USER:-hospital}"
POSTGRES_DB="${POSTGRES_DB:-hospital_directory}"

BACKUP_DIR="${1:-$RELEASE_ROOT/backups}"
mkdir -p "$BACKUP_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="$BACKUP_DIR/hospital_directory_${timestamp}.sql.gz"

postgres_container="$(compose ps -q postgres)"
[ -n "$postgres_container" ] || fail "postgres container is not running. Start the stack first with start_stack.sh."

log "Backing up database '$POSTGRES_DB' to $backup_file ..."
docker exec "$postgres_container" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=plain | gzip > "$backup_file"

log "Backup complete: $backup_file ($(du -h "$backup_file" | cut -f1))"
log "Store this file outside the Docker host (external drive, second copy) — it lives outside any Docker volume."
log "To restore: restore_database.sh $backup_file"
