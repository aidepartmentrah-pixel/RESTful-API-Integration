-- Confirms the Alembic-managed schema exists and has the expected structure.
-- Usage: psql "$DATABASE_URL" -f validate_tables.sql

\echo 'Expected tables:'
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('patients', 'doctors', 'workers', 'alembic_version')
ORDER BY table_name;

\echo 'Alembic version (should be 0002, the latest revision in alembic/versions):'
SELECT version_num FROM alembic_version;

\echo 'Row counts:'
SELECT 'patients' AS table_name, count(*) FROM patients
UNION ALL
SELECT 'doctors', count(*) FROM doctors
UNION ALL
SELECT 'workers', count(*) FROM workers;
