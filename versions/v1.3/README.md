# v1.3 — proposed, in active development

**Status: draft.** Not deployed anywhere real. v1.3 is **v1.2 unchanged
plus two endpoints for the BCI (heart) center's clinic platform**, built
and tested in this mock before being handed to 3iSoft as a formal,
evidence-backed ask. Nothing here is a commitment from the vendor.

- Spec: `Hospital_Directory_API_OpenAPI_v1.3.yaml` — v1.2 plus the two
  additions under the `BCI Radiology` tag, each `x-status: proposed`
  until built here.
- Requirement docs: `requirements/<n>-<slug>/requirement.md`.
- Evidence: `evidence.md` — read it first; both additions are MOCK_ONLY,
  backed only by the field names of captured radiology pages.
- Acceptance test: `acceptance_tests/verify_v1.3_contract.ps1`.

## The 2 additions

| # | Addition | Consumer | Status (this mock) |
|---|---|---|---|
| 1 | `GET /bci-radiology/visits/today` | BCI clinic platform | Proposed |
| 2 | `GET /bci-radiology/patients/{mrn}` | BCI clinic platform | Proposed |

## Traceability matrix

| Requirement | Unit test(s) | Acceptance-test check | Status |
|---|---|---|---|
| `requirements/1-bci-radiology-visits-today/` | `tests/test_bci_radiology_visits_today.py` | `bci-visits-today` line in `verify_v1.3_contract.ps1` | Proposed |
| `requirements/2-bci-radiology-patient/` | `tests/test_bci_radiology_patient.py` | `bci-patient` line | Proposed |

Kept in sync by hand with the `x-status` markers in the YAML.

## How this relates to v1.1 and v1.2

v1.1 (`localhost:6000`, project `mock-v11`) and v1.2-dev
(`localhost:6001`, project `mock-v12-dev`) are not touched. v1.3 is
developed in its own worktree (`RESTful-API-Integration-v1.3`, branch
`v1.3-bci-radiology`) and runs as **v1.3-dev on `localhost:6002`**,
Docker Compose project `mock-v13-dev`, with its own Postgres port.

v1.3 starts from the **committed** v1.2 (`ea21d11`, all 5 v1.2 additions).
Uncommitted v1.2 work in the main checkout is not included.

## Test data

The v1.3-dev mock is loaded with the BCI test world: invented patients
only, MRNs `9999.NNNNNN`, visit numbers `V9999-NNNN`, phones
`00-000-0NN`, doctors `Dr. Test-X`. Visit times are "today" relative to
the day the mock is asked.
