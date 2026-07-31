-- This API stores no configuration rows in the database (API key, ports, and
-- base URL are supplied via environment variables per Document 1 sections 16/23,
-- not via a database configuration table). This script instead validates the
-- database-level settings that the API's UTF-8/Arabic requirement depends on
-- (Document 1 section 15, Document 3 section 2.3).
-- Usage: psql "$DATABASE_URL" -f validate_configuration.sql

\echo 'Database encoding (expect UTF8):'
SELECT datname, pg_encoding_to_char(encoding) AS encoding
FROM pg_database
WHERE datname = current_database();

\echo 'Server encoding / client encoding (expect UTF8):'
SHOW server_encoding;
SHOW client_encoding;

\echo 'Arabic text round-trip check (expect the Arabic sample below unmodified):'
SELECT full_name
FROM (
    SELECT full_name, full_name ~ '[؀-ۿ]' AS has_arabic
    FROM patients
) t
WHERE has_arabic
LIMIT 3;
