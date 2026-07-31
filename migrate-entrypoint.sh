#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python -c "
import os
import sys
import time

import psycopg2

for _ in range(30):
    try:
        psycopg2.connect(os.environ['DATABASE_URL'])
        sys.exit(0)
    except psycopg2.OperationalError:
        time.sleep(1)
print('PostgreSQL did not become available in time', file=sys.stderr)
sys.exit(1)
"

echo "Running database migrations..."
alembic upgrade head

echo "Seeding development data..."
python -m seed.seed_data

echo "Database initialization complete."
