# Evidence behind v1.3

None of v1.3 has real-server evidence. Both additions are **MOCK_ONLY**:
proposals, implemented (once built) in this mock only. "Implemented"
never means 3iSoft agreed or that the real system behaves this way.

**What evidence exists:** the *field names* (labels, column headers, list
sizes, mandatory marks) of three captured pages of the radiology module
on `meraj:8080`: the finished-visits list (`finishedVisits.xhtml`), the
visit card (`visitOut-card.xhtml`) and the appointment booking page
(`appointment-list.xhtml`), captured on the offline network on
2026-10-21. A script printed structure only; no patient values were
kept. The raw captures are not in this repo and never will be (they
can hold session cookies). The BCI project keeps the structure notes
(its model notes 6, 6.5 and 7).

| Item | Confidence | What the captured pages show |
|---|---|---|
| `GET /bci-radiology/visits/today` | **MOCK_ONLY** | Labels for the visit number (الرقم), patient number (رقم المريض), own, father's, family and mother's names, treating physician (الطبيب المعالج), visit date (date only, **no time of day**), machine. **Not seen:** a list of today's registered, not yet finished visits (the "active visits" page is empty and unused); clinic visits without a machine; a scheduled/walk-in marker; a frozen visit in a list. |
| `GET /bci-radiology/patients/{mrn}` | **MOCK_ONLY** | Visit-card labels: names, birth date, sex, ID number (رقم الهوية), nationality (الجنسية), has allergy (لديه حساسية), phones with "owner of the number" (both mandatory, owner from a list of 5). **Not seen:** the patient-file page said to hold the phones; the 5 owner values. |

## Field by field

| Field | Level |
|---|---|
| `visit_id`, `mrn`, the four Arabic names, `doctor_name` | SEEN (labels) |
| English names | SEEN only as a foreign-names dialog on the card |
| `birth_date`, `sex`, `nationality`, `id_number`, `has_allergy`, `phones` | SEEN (labels on the card) |
| `visit_time` | Date SEEN; time of day NOT SEEN |
| `visit_kind` | NOT SEEN (inferred from the booking page) |
| `status` = `frozen` | From the author's notes only; the capture script did not find the freeze action |

## Carried forward

- From v1.1 `evidence.md`: the real Directory API's `sex` holds a full Arabic word, not the documented `"Male"`; the dotted patient id behaves per admission; a UTF-8 defect is confirmed on the real server.
- Whether رقم المريض in the radiology module equals the Directory's `patient_id` has never been checked.

## Acceptance tests

`acceptance_tests/verify_v1.3_contract.ps1` reports each addition on its
own line: `PASS`, `FAIL` or `NOT-YET-IMPLEMENTED`. Until the mock is
built (BCI slice 0.9), both lines read `NOT-YET-IMPLEMENTED`; that is the
expected state, not a bug.
