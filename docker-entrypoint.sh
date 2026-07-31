#!/bin/sh
set -e

echo "Starting API server..."
exec uvicorn app.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"
