-- This API has no application-level user accounts or login (Document 1 section
-- 16: "Version 1 does not require... user login"). The relevant "user" here is
-- the PostgreSQL role the API connects as. This script confirms that role
-- exists and can reach the expected tables.
-- Usage: psql "$DATABASE_URL" -f validate_users.sql

\echo 'Current connected role:'
SELECT current_user, current_database();

\echo 'Table privileges for the current role:'
SELECT table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = current_user
  AND table_name IN ('patients', 'doctors', 'workers')
ORDER BY table_name, privilege_type;
