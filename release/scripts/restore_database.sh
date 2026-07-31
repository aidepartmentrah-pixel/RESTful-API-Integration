#!/bin/sh
# Restores a PostgreSQL backup produced by backup_database.sh.
# This DROPS AND RECREATES the target database — it is destructive to current data.
# Usage: restore_database.sh path/to/backup.sql.gz
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose
require_env_file

# shellcheck disable=SC1090
. "$ENV_FILE"

POSTGRES_USER="${POSTGRES_USER:-hospital}"
POSTGRES_DB="${POSTGRES_DB:-hospital_directory}"

backup_file="${1:-}"
[ -n "$backup_file" ] || fail "Usage: restore_database.sh path/to/backup.sql.gz"
[ -f "$backup_file" ] || fail "Backup file not found: $backup_file"

postgres_container="$(compose ps -q postgres)"
[ -n "$postgres_container" ] || fail "postgres container is not running. Start the stack first with start_stack.sh."

printf 'This will DROP and recreate database "%s" using %s.\n' "$POSTGRES_DB" "$backup_file"
printf 'All current data in that database will be lost. Type YES to continue: '
read -r confirmation
[ "$confirmation" = "YES" ] || fail "Restore cancelled."

log "Stopping the api service so it does not serve stale connections during restore ..."
compose stop api

log "Dropping and recreating database '$POSTGRES_DB' ..."
docker exec "$postgres_container" psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS \"$POSTGRES_DB\";"
docker exec "$postgres_container" psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE \"$POSTGRES_DB\" OWNER \"$POSTGRES_USER\";"

log "Restoring from $backup_file ..."
gunzip -c "$backup_file" | docker exec -i "$postgres_container" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

log "Restore complete. Restarting api service ..."
compose start api

log "Run verify_installation.sh to confirm the restored database is healthy."
