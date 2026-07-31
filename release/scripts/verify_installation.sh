#!/bin/sh
# Confirms the offline deployment is actually working: containers running,
# database migrated, API healthy and answering authenticated requests.
# Exits non-zero and prints which check failed.
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose
require_env_file

# shellcheck disable=SC1090
. "$ENV_FILE"

HOST_PORT="${HOST_PORT:-6000}"
API_KEY="${API_KEY:-}"

checks_failed=0

container_health() {
    service="$1"
    id="$(compose ps -q "$service")"
    [ -n "$id" ] || return 1
    docker inspect -f '{{.State.Health.Status}}' "$id" 2>/dev/null
}

printf '%-55s' "postgres container is healthy"
if [ "$(container_health postgres)" = "healthy" ]; then echo "OK"; else echo "FAILED"; checks_failed=$((checks_failed + 1)); fi

printf '%-55s' "migrate service completed successfully"
migrate_id="$(compose ps -a -q migrate)"
if [ -n "$migrate_id" ] && [ "$(docker inspect -f '{{.State.ExitCode}}' "$migrate_id")" = "0" ]; then
    echo "OK"
else
    echo "FAILED"
    checks_failed=$((checks_failed + 1))
fi

printf '%-55s' "api container is healthy"
if [ "$(container_health api)" = "healthy" ]; then echo "OK"; else echo "FAILED"; checks_failed=$((checks_failed + 1)); fi

if command -v curl >/dev/null 2>&1; then
    printf '%-55s' "health endpoint returns 200"
    code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$HOST_PORT/api/directory/v1/health" || true)"
    if [ "$code" = "200" ]; then echo "OK"; else echo "FAILED (got $code)"; checks_failed=$((checks_failed + 1)); fi

    printf '%-55s' "missing API key returns 401"
    code="$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:$HOST_PORT/api/directory/v1/doctors" || true)"
    if [ "$code" = "401" ]; then echo "OK"; else echo "FAILED (got $code)"; checks_failed=$((checks_failed + 1)); fi

    printf '%-55s' "authenticated doctors search returns 200"
    if [ -n "$API_KEY" ]; then
        code="$(curl -s -o /dev/null -w '%{http_code}' -H "X-API-Key: $API_KEY" "http://localhost:$HOST_PORT/api/directory/v1/doctors" || true)"
        if [ "$code" = "200" ]; then echo "OK"; else echo "FAILED (got $code)"; checks_failed=$((checks_failed + 1)); fi
    else
        echo "SKIPPED (API_KEY not set in .env)"
    fi
else
    log "curl not found on host; skipping HTTP-level checks. Container healthchecks above already exercise /health."
fi

echo
if [ "$checks_failed" -eq 0 ]; then
    log "All checks passed."
    exit 0
else
    log "$checks_failed check(s) failed. See documentation/TROUBLESHOOTING.md."
    exit 1
fi
