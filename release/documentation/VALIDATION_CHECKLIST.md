# Validation Checklist

Use this to sign off a fresh install or an update before declaring it ready
for HCAT/HCopilot to point at. Everything here is also exercised automatically
by `scripts/verify_installation.sh`, but this checklist adds a few manual
checks that script can't fully judge on its own.

## Automated

- [ ] `sh scripts/verify_installation.sh` reports "All checks passed."

## Infrastructure

- [ ] `docker compose ... ps -a` shows `postgres` and `api` as `healthy`, and
      `migrate` as `Exited (0)`.
- [ ] `sh scripts/show_logs.sh migrate` shows `Database initialization complete.`
      with no error output above it.

## API contract spot-checks

Replace `<key>` with the real `API_KEY` from `.env`.

- [ ] `curl http://localhost:6000/api/directory/v1/health` → `200`, body has
      `"status":"healthy"`.
- [ ] `curl http://localhost:6000/api/directory/v1/doctors` (no key) → `401`.
- [ ] `curl -H "X-API-Key: <key>" http://localhost:6000/api/directory/v1/doctors?limit=5`
      → `200`, `items` non-empty, `total` > 5.
- [ ] `curl -H "X-API-Key: <key>" "http://localhost:6000/api/directory/v1/patients"`
      (no search criteria) → `400` with `"error":"MISSING_SEARCH_CRITERIA"`.
- [ ] `curl -H "X-API-Key: <key>" "http://localhost:6000/api/directory/v1/patients?q=a"`
      → `200`, results are person-level records (`patient_id`, `full_name`,
      `first_name`, `last_name`, `birth_date`, `age`, `sex` only — no
      `visit_id`/`arrival_time`/`departure_time`).
- [ ] `curl -H "X-API-Key: <key>" "http://localhost:6000/api/directory/v1/patients/P-10001"`
      → `200`, single object, no envelope. A bogus ID → `404` with
      `"error":"PATIENT_NOT_FOUND"`.
- [ ] A response containing Arabic text (search for a common Arabic name
      fragment) renders correctly when viewed in a browser or `curl | jq`,
      not as `?` or mojibake.
- [ ] `curl -sI ... | grep -i content-type` → `application/json; charset=utf-8`
      on both a success and an error response.

## Data diversity (per Document 4 section 5)

Run these with `psql` inside the postgres container, or via pgAdmin's query tool:

```bash
docker exec -i <postgres-container> psql -U hospital -d hospital_directory < database/validation/validate_lookup_data.sql
```

- [ ] Multiple doctor specialties present.
- [ ] Both active and inactive doctors present.
- [ ] Both active and inactive workers present.
- [ ] Both `sex` values (M/F) present among patients.
- [ ] At least one patient has a null `birth_date` with a non-null `age`
      (confirms `age` isn't silently derived-only).

## Operational readiness

- [ ] A backup was taken after this install/update:
      `sh scripts/backup_database.sh`, file exists under `release/backups/`.
- [ ] `.env` secrets (`API_KEY`, `POSTGRES_PASSWORD`, `PGADMIN_DEFAULT_PASSWORD`)
      are NOT the template's blank/default values.
- [ ] The API port (`HOST_PORT`) is reachable only from the intended internal
      network, not from the public internet (Document 1 section 17).
- [ ] HCAT and HCopilot's `HOSPITAL_API_BASE_URL` and `HOSPITAL_API_KEY`
      configuration values point at this server and match `.env`.

Sign-off:

| Field | Value |
|---|---|
| Installed by | |
| Date | |
| Release version (see RELEASE_NOTES.md) | |
| Result | Pass / Fail |
