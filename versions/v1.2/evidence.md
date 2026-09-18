# Evidence behind v1.2

Unlike `versions/v1.1/evidence.md`, none of this version has real-server
evidence — it's proposals, not confirmed vendor behavior, **even after
Period D built all 5 in the mock.** "Implemented" below means implemented
*in this mock only*; it is not evidence the real vendor system behaves
this way, or that 3iSoft has agreed to build it. That distinction is
stated plainly per item rather than implied.

| Item | Confidence | Source |
|---|---|---|
| `GET /patients/father-names` | **MOCK_ONLY** — implemented and verified against this mock's own seed data; never sent to the real server | `tests/test_father_names.py`; live-verified against `localhost:6001` |
| `GET /patients/first-names` | **MOCK_ONLY** — same as above, symmetrical endpoint | `tests/test_first_names.py`; live-verified against `localhost:6001` |
| `Worker.section_name` / `administration_name` | **MOCK_ONLY** — the mock's `department_name` convention (a plain stored display-name column, confirmed real behavior for that specific field, see `versions/v1.1/evidence.md`) was extended to `section`/`administration` by analogy, not by direct observation of the real system exposing these | `tests/test_worker_section_administration_names.py`; live-verified against `localhost:6001` |
| `Patient.encounter_type` | **MOCK_ONLY** — motivated by the confirmed real-server fact that `patient_id` is effectively per-admission, not per-deduplicated-person (see `versions/v1.1/evidence.md`, dotted-ID row); the field itself, and its allowed values, have never been observed on a real response | `tests/test_patient_encounter_type.py`; live-verified against `localhost:6001` |
| `GET /er/current-visits` | **MOCK_ONLY** — sourced today from a separate, non-JSON system ("meraj"); this is a new-resource ask, not a gap in existing behavior. `gender`/`age`/`chief_complaint` are entirely invented for mock realism — the requirement doc flags all three as open items, not vendor-confirmed shapes | `tests/test_er_current_visits.py`; live-verified against `localhost:6001` |

## What this means for the acceptance tests

`acceptance_tests/verify_v1.2_contract.ps1` reports each of these 5 items
as its own line: `PASS`, `FAIL`, or `NOT-YET-IMPLEMENTED` — never a blanket
pass/fail for the whole version. As of the end of Period D, a run against
`localhost:6001` reads:

```
father-names:            PASS
first-names:              PASS
worker-section-admin:     PASS
patient-encounter-type:   PASS
er-current-visits:        PASS
```

Before Period D, the last 4 correctly read `NOT-YET-IMPLEMENTED` — that
was the expected state at that stage, not a bug.

## Open items carried forward from v1.1

The structured `first_name`/`father_name`/`last_name` search shape
still hasn't been tested against the real server (see
`versions/v1.1/evidence.md`). Everything built on top of it in v1.2
(`father-names`, `first-names`) inherits that same open question.
