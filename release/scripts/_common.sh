#!/bin/sh
# Shared helpers sourced by the other release scripts. Not meant to be run directly.
set -eu

# Resolve paths relative to this script's location so scripts work regardless
# of the operator's current working directory.
RELEASE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
COMPOSE_DIR="$RELEASE_ROOT/compose"
IMAGES_DIR="$RELEASE_ROOT/docker-images"
ENV_FILE="$COMPOSE_DIR/.env"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

# Explicit project name -- MUST NOT be left to Docker Compose's default
# (the basename of the directory holding the compose file, which is
# literally "compose" here). Any other release package built the same way
# would default to that identical name too, so installing two such releases
# on the same offline server would merge them into one Compose project and
# tangle their containers/networks together. This name also becomes the
# actual container name prefix (e.g. hospital-directory-api-api-1) since
# none of this project's services declare an explicit container_name.
COMPOSE_PROJECT_NAME="hospital-directory-api"

log()  { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1"; }
fail() { printf '\nERROR: %s\n' "$1" >&2; exit 1; }

require_docker() {
    command -v docker >/dev/null 2>&1 || fail "docker was not found on PATH. Install Docker Engine first."
    docker info >/dev/null 2>&1 || fail "docker is installed but not usable (is the daemon running? do you have permission — try with sudo or add your user to the 'docker' group?)."
}

require_compose() {
    docker compose version >/dev/null 2>&1 || fail "The 'docker compose' plugin was not found. Install docker-compose-plugin."
}

require_env_file() {
    [ -f "$ENV_FILE" ] || fail "$ENV_FILE not found. Copy compose/.env.offline.template to compose/.env and fill in real values first."
}

compose() {
    require_env_file
    docker compose -p "$COMPOSE_PROJECT_NAME" --project-directory "$COMPOSE_DIR" -f "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}
