#!/bin/sh
# Shows logs for one service (default: api). Usage: show_logs.sh [service] [-f]
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker
require_compose

service="${1:-api}"
follow_flag=""
if [ "${2:-}" = "-f" ] || [ "${1:-}" = "-f" ]; then
    follow_flag="-f"
    [ "${1:-}" = "-f" ] && service="api"
fi

log "Showing logs for service: $service (services: postgres, migrate, api, pgadmin)"
compose logs $follow_flag --tail 200 "$service"
