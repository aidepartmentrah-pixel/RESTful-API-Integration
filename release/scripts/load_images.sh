#!/bin/sh
# Loads all Docker images shipped on this DVD/USB into the local Docker image
# store. Never contacts the network — only reads local .tar files.
set -eu
. "$(dirname -- "$0")/_common.sh"

require_docker

[ -d "$IMAGES_DIR" ] || fail "$IMAGES_DIR not found."

found_any=0
for tar_file in "$IMAGES_DIR"/*.tar; do
    [ -e "$tar_file" ] || continue
    found_any=1
    log "Loading $(basename "$tar_file") ..."
    docker load -i "$tar_file"
done

[ "$found_any" -eq 1 ] || fail "No .tar image files found in $IMAGES_DIR."

log "Images loaded. Current images:"
docker images
