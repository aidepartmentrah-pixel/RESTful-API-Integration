# v1.2 — proposed, in active development

**Status: draft.** This is not deployed anywhere real. It's the next
version being built out and tested in this repo before being handed to
3iSoft as a formal, evidence-backed set of asks. Nothing here is a
commitment from the vendor — it's an accountable request, with the tests
to prove each piece works before anyone is asked to build it for real.

- Spec: `Hospital_Directory_API_OpenAPI_v1.2.yaml` — v1.1 plus 5
  additions, each tagged `x-status: implemented` or `x-status: proposed`.
- Requirement docs (rationale, format decisions, open questions) for each
  addition: `requirements/<n>-<slug>/requirement.md`.
- Evidence citations: `evidence.md` — read this before trusting any
  specific field or endpoint below; most of this version has no
  real-server evidence at all.
- Acceptance test: `acceptance_tests/verify_v1.2_contract.ps1`.

## The 5 additions

All 5 are now implemented in this mock (Period D) — "implemented" means
built and verified here, **not** accepted by 3iSoft. Nothing below is a
vendor commitment; see `evidence.md` for what is/isn't backed by
real-server testing, which is a separate question from what's built here.

| # | Addition | Consumer | Status (this mock) |
|---|---|---|---|
| 1 | `GET /patients/father-names` | HCAT | Implemented (mock) |
| 2 | `GET /patients/first-names` | HCAT | Implemented (mock) |
| 3 | `Worker.section_name` / `administration_name` | HCAT | Implemented (mock) |
| 4 | `Patient.encounter_type` | HCAT | Implemented (mock) |
| 5 | `GET /er/current-visits` | HCopilot | Implemented (mock) |

## Traceability matrix

| Requirement | Unit test(s) | Acceptance-test check | Status |
|---|---|---|---|
| `requirements/1-father-name-candidates/` | `tests/test_father_names.py` | `father-names` line in `verify_v1.2_contract.ps1` | Implemented (mock), verified |
| `requirements/2-first-name-candidates/` | `tests/test_first_names.py` | `first-names` line | Implemented (mock), verified |
| `requirements/3-worker-section-administration-names/` | `tests/test_worker_section_administration_names.py` | `worker-section-admin` line | Implemented (mock), verified |
| `requirements/4-patient-encounter-type/` | `tests/test_patient_encounter_type.py` | `patient-encounter-type` line | Implemented (mock), verified |
| `requirements/5-er-current-visits-hcopilot/` | `tests/test_er_current_visits.py` | `er-current-visits` line | Implemented (mock), verified |

This table is the single source of truth for "is X actually done" — kept
in sync by hand with the `x-status` markers in the YAML (the spec-vs-code
drift check only catches disagreement between the YAML and the running
code, not between the YAML and this table).

## How this relates to `versions/v1.1/`

v1.1 is what HCAT and HCopilot build against today and is not touched by
this work. v1.2 is developed on a separate port (`localhost:6001`, Docker
Compose project `mock-v12-dev`) so v1.1's port (`localhost:6000`, project
`mock-v11`) stays untouched throughout. See the root-level plan for the
full port/worktree layout.
