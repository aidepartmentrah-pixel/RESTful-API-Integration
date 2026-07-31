-- This API has no separate lookup tables; specialty/department/job values are
-- free-text columns on doctors/workers. This script checks the seeded data has
-- enough diversity to exercise search, per Document 4 section 5 ("Seed Data").
-- Usage: psql "$DATABASE_URL" -f validate_lookup_data.sql

\echo 'Distinct doctor specialties (expect multiple):'
SELECT specialty_name, count(*) FROM doctors GROUP BY specialty_name ORDER BY specialty_name;

\echo 'Distinct worker job titles (expect multiple):'
SELECT job_title, count(*) FROM workers GROUP BY job_title ORDER BY job_title;

\echo 'Distinct worker departments (expect multiple):'
SELECT department_id, count(*) FROM workers GROUP BY department_id ORDER BY department_id;

\echo 'Active vs inactive doctors (expect both present):'
SELECT is_active, count(*) FROM doctors GROUP BY is_active;

\echo 'Active vs inactive workers (expect both present):'
SELECT is_active, count(*) FROM workers GROUP BY is_active;

\echo 'Patient sex distribution (expect both M and F present):'
SELECT sex, count(*) FROM patients GROUP BY sex ORDER BY sex;

\echo 'Patients missing a birth_date but with an age supplied (expect at least one):'
SELECT count(*) FROM patients WHERE birth_date IS NULL AND age IS NOT NULL;
