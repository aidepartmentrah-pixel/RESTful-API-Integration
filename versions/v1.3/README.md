# v1.3 — proposed, in active development

**Status: draft.** Not deployed anywhere real. v1.3 is **v1.2 unchanged
plus two endpoints for the BCI (heart) center's clinic platform**, built
and tested in this mock before being handed to 3iSoft as a formal,
evidence-backed ask. Nothing here is a commitment from the vendor.

- Spec: `Hospital_Directory_API_OpenAPI_v1.3.yaml` — v1.2 plus the two
  additions under the `BCI Radiology` tag, each `x-status: implemented`
  (built and verified in this mock only, not accepted by 3iSoft).
- Requirement docs: `requirements/<n>-<slug>/requirement.md`.
- Evidence: `evidence.md` — read it first; both additions are MOCK_ONLY,
  backed only by the field names of captured radiology pages.
- Acceptance test: `acceptance_tests/verify_v1.3_contract.ps1`.

## The 2 additions

| # | Addition | Consumer | Status (this mock) |
|---|---|---|---|
| 1 | `GET /bci-radiology/visits/today` | BCI clinic platform | Implemented (mock) |
| 2 | `GET /bci-radiology/patients/{mrn}` | BCI clinic platform | Implemented (mock) |

## Traceability matrix

| Requirement | Unit test(s) | Acceptance-test check | Status |
|---|---|---|---|
| `requirements/1-bci-radiology-visits-today/` | `tests/test_bci_radiology_visits_today.py` | `bci-visits-today` line in `verify_v1.3_contract.ps1` | Implemented (mock), verified |
| `requirements/2-bci-radiology-patient/` | `tests/test_bci_radiology_patient.py` | `bci-patient` line | Implemented (mock), verified |

Kept in sync by hand with the `x-status` markers in the YAML.

## How this relates to v1.1 and v1.2

v1.1 (`localhost:6000`, project `mock-v11`) and v1.2-dev
(`localhost:6001`, project `mock-v12-dev`) are not touched. v1.3 is
developed in its own worktree (`RESTful-API-Integration-versions1.3`,
branch `v1.3-bci-radiology`) and runs as **v1.3-dev on `localhost:6002`**,
Docker Compose project `mock-v13-dev`, with its own Postgres port.

v1.3 includes v1.2 as of `dc42452`: the 3 v1.2 additions kept after the
4 Nov 2026 meeting (`first-names` and `encounter_type` were dropped).

## Test data

The v1.3-dev mock is loaded with the BCI test world: invented patients
only, MRNs `9999.NNNNNN`, visit numbers `V9999-NNNN`, phones
`00-000-0NN`, doctors `Dr. Test-X`. Visit times are "today" relative to
the day the mock is asked.

## Merged v1.2 scope cut (5 Nov 2026)

The v1.2 scope cut was merged into this branch. Two consequences:

- **Migration renumbered.** v1.2's `0007` drops `patients.encounter_type`;
  the BCI tables migration became `0008` (revises `0007`), so the chain is
  `0001 .. 0008` with one head. The existing v1.3-dev database was
  aligned by hand (column dropped, `alembic_version` set to `0008`); the
  BCI test data was kept.
- **Spec cleaned.** `/patients/first-names` and `Patient.encounter_type`
  are gone from the v1.3 spec too, and `father-names` carries the agreed
  rules (ties ordered, `total_candidates` counted before `limit`).

## Running and testing

```
docker compose -p mock-v13-dev up -d --build   # API on :6002, Postgres on :5436, pgAdmin on :5053
pytest -q                                      # the mock's own suite (v1.1/v1.2 tests included)
powershell -File versions/v1.3/acceptance_tests/verify_v1.3_contract.ps1 [-CheckSourceDown]
```

Copy `.env.example` to `.env` and set `HOST_PORT=6002`, `POSTGRES_HOST_PORT=5436`,
`PGADMIN_HOST_PORT=5053`, `API_IMAGE_TAG=1.3.0-dev` and your own `API_KEY`
(the acceptance script reads the key from `.env`). The migrate step runs
`seed/seed_bci_test_world.py`, which adds only the invented `9999.*` rows
(`--remove` deletes only those). `seed/bci_test_world.json` is a copy of
the BCI project's `testdata/patients.json`; the BCI repo has a test that
the two are identical. The data is in its own tables (`bci_patients`,
`bci_visits`), not in `patients`. Visit times are stored as clock times
and dated "today" (Asia/Beirut) when the API answers.

## Arabic examples

The `/er/current-visits` and `father-names` examples inherited from v1.2
used to show mojibake (`Ø¹Ø¨Ø§Ø³`, UTF-8 read as Latin-1). They were
repaired in both the v1.2 and v1.3 spec files; all examples are UTF-8.
