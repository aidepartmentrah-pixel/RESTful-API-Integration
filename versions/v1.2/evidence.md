# Evidence behind v1.2

v1.2 was delivered by 3iSoft ("HIS API — v1.2 Additions", 18 Nov 2026) and
tested on the **real servers** the same day, from the hospital's offline
PC, with `offline_test_kit/` (about 80 checks, written from 3iSoft's
document). The mock was then changed to match.

| Item | Confidence | Source |
|---|---|---|
| `GET /patients/father-names` | **REAL_SERVER_VERIFIED** — fields, sorting, `total_candidates` vs `limit`, both 422 messages, no-match 200, Arabic UTF-8, 401 | Offline run 18 Nov 2026 11:26, all Part 2A checks PASS |
| `GET /hr-workers`, `/hr-workers/{id}` | **REAL_SERVER_VERIFIED** — 12 fields, paging, 404, 422 limits, filters (hierarchy, spelling unification, AND, unknown/empty name), 401. 1748 workers; 81 of the first 500 have no administration | Offline run 18 Nov 2026, all Part 2B checks PASS |
| `/workers` unchanged | **REAL_SERVER_VERIFIED** — no section/administration names | Offline run, Part 1 INFO |
| ER `GET /current-visits` | **PARTLY VERIFIED** — on `meraj:8080/his-er/api/er/v1`; answers 401 `UNAUTHORIZED` without a key and rejects the Directory key. **Field checks not run yet: no ER key.** | Offline run 18 Nov 2026 11:26 (ER without key PASS; with Directory key 401); browser check of meraj |
| ER on malin | **REAL_SERVER_OBSERVED** — `malin:8080/his-er/...` returns HTTP 500 with a non-JSON page, with or without a key | Offline run 18 Nov 2026 11:05 |
| `/health` | `api_version` still reports `1.0.0` on the real server | Offline run, Part 1 INFO |

The mock's ER fields (Arabic gender, age, free-text complaint, Beirut
offset) follow 3iSoft's document; they become REAL_SERVER_VERIFIED once the
ER key arrives and the offline test's Part 2C passes.

## Test runs

| When | Target | Result |
|---|---|---|
| 18 Nov 2026 11:05 | real (ER on malin) | 69 passed, 2 failed — ER 500 |
| 18 Nov 2026 11:26 | real (ER on meraj) | 70 passed, 1 failed — ER key missing |
| 18 Nov 2026 | mock v1.2-dev (port 6001), after matching | 83 passed, 0 failed |

The test itself was checked against a stand-in built from 3iSoft's
document, broken in 12 different ways (sorting, totals, messages, fields,
hierarchy, spelling, empty filter, ER order/fields/encoding/key/offset):
every break was caught.

## Dropped items (4 Nov 2026 meeting)

`GET /patients/first-names` and `Patient.encounter_type` — see the
README's *Dropped* section. `tests/test_v1_2_dropped_items.py` guards
against either coming back.
