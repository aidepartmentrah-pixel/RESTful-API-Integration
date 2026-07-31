-- Confirms the schema is on the expected Alembic revision.
-- Compare the output against the head revision id in alembic/versions/ (currently "0001").
-- Usage: psql "$DATABASE_URL" -f validate_database_version.sql

\echo 'Current Alembic revision applied to this database:'
SELECT version_num FROM alembic_version;

\echo 'PostgreSQL server version:'
SELECT version();
