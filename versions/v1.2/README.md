# v1.2 — delivered by 3iSoft, verified on the real servers

**Status: delivered.** 3iSoft delivered v1.2 on 18 Nov 2026 ("HIS API —
v1.2 Additions") and we verified it on the real servers the same day from
the hospital's offline PC: **70 passed, 1 failed** — the only failure was
the ER call made with the Directory key, because the ER API has its own key
(not received yet). The mock in this repo now matches what was delivered.

- Spec: `Hospital_Directory_API_OpenAPI_v1.2.yaml` — v1.1 plus the
  delivered additions (`x-status: delivered`).
- Test: `offline_test_kit/` — one test for both the real servers and the
  mock (see *Testing* below). `acceptance_tests/verify_v1.2_contract.ps1`
  runs it against the mock.
- Evidence: `evidence.md`.
- Our original request (what we asked for): `requirements/`, and the
  vendor PDF `Hospital Directory API v1.2 - Requirements.pdf`. Two items
  were built differently from that request — see the table below.

## Where the real APIs are

| API | Address | Key |
|---|---|---|
| Directory API | `http://malin:8080/his-general/api/directory/v1` | Directory key (`dev-secret-key` works) |
| ER API | `http://meraj:8080/his-er/api/er/v1` — **meraj, not malin** | Its **own** key (not received yet) |

`localhost:18080` in 3iSoft's documents is their developer's machine.
`/his-er/...` on malin answers 500 with an error page — don't use it.

## What v1.2 adds

| # | Asked for | Delivered by 3iSoft | Consumer |
|---|---|---|---|
| 1 | `GET /patients/father-names` | **As asked.** Exact limit error message: `limit must be between 1 and 200`. | HCAT |
| 2 | `section_name` / `administration_name` on `/workers` | **Built differently:** new `GET /hr-workers` and `/hr-workers/{employee_id}` with the HR tree (administration > section > department), filters by unit name with Arabic spelling unification. `/workers` is unchanged from v1.1. | HCAT |
| 3 | `GET /er/current-visits` on the Directory API | **Built differently:** `GET /current-visits` on the separate **ER API** (`/his-er/api/er/v1`, own key). Gender `ذكر`/`انثى`, age in years, complaint as free text, every field always present (null when empty). | HCopilot |

## The mock (v1.2-dev, port 6001)

Serves the same paths as the real servers, so a client switches between
them by changing only the host:

| | Mock | Real |
|---|---|---|
| Directory API | `http://localhost:6001/his-general/api/directory/v1` | `http://malin:8080/his-general/api/directory/v1` |
| ER API | `http://localhost:6001/his-er/api/er/v1` | `http://meraj:8080/his-er/api/er/v1` |

The mock's older prefix `http://localhost:6001/api/directory/v1` still
works (Directory API only) so nothing that already uses it breaks.

Keys come from `.env`: `API_KEY` (Directory) and `ER_API_KEY` (ER). Both are
`dev-secret-key` for now; `ER_API_KEY` changes when 3iSoft sends the real
ER key.

Mock data: `/hr-workers` uses an Arabic HR tree (`hr_units`, migration
`0008_hr`), with a name used by two departments and one inactive unit so
the filter rules can be tested. Workers are placed in departments,
directly in sections or administrations, or nowhere — like the real data.

## Testing

```
pytest -q                                                     # unit tests
powershell -File versions/v1.2/acceptance_tests/verify_v1.2_contract.ps1   # the mock
```

`offline_test_kit/` is the folder to copy to the hospital's offline PC:
edit `settings.txt` (real servers) and double-click `RUN-TEST.bat`.
`settings.local-mock.txt` holds the mock's settings. Results are saved in
`offline_test_kit/results/` (not committed). Last runs: real servers
70/1 (ER key missing), mock 83/0.

## Dropped (meeting, 4 Nov 2026)

| Was | Item | Why dropped |
|---|---|---|
| #2 | `GET /patients/first-names` (family-name-only search) | A family name can match hundreds of first names — too broad to be a useful narrowing step. |
| #4 | `Patient.encounter_type` (inpatient/outpatient) | The source system does not record it. |

`tests/test_v1_2_dropped_items.py` fails if either reappears.

## Traceability

| Item | Unit tests | Offline-kit section |
|---|---|---|
| father-names | `tests/test_father_names.py` | Part 2A |
| hr-workers | `tests/test_hr_workers.py` | Part 2B |
| ER current-visits | `tests/test_er_current_visits.py` | Part 2C |
| Paths and `/workers` unchanged | `tests/test_paths_and_workers_v1_2.py` | Part 1 |

## Open questions for 3iSoft

1. **The ER key** — needed to finish the ER test.
2. **"In preparation"** — the ER list only holds visits in that state. Do
   patients leave the list while still physically in the ER (e.g. under
   treatment)? HCopilot would mark them as departed.
3. **Two departments** — `/workers.department_name` (his-general) and
   `/hr-workers.department_name` (HR tree) may differ. Which should HCAT
   show? Will `/workers` stay?
4. Is the ER "visit date/time" the arrival time?
5. Could the ER API return `503` when its source is unreachable (so an
   outage never looks like an empty ER)?
6. Their father-names example (`limit=10`, 5 candidates, `total_candidates:
   7`) does not add up; the real server behaves correctly (total counts
   all matches before the limit).

## How this relates to `versions/v1.1/`

v1.1 runs on `localhost:6000` (project `mock-v11`), v1.2-dev on
`localhost:6001` (project `mock-v12-dev`). Both accept the real Directory
path `/his-general/api/directory/v1` as well as `/api/directory/v1`.
