# 2026-08-17 — First real-server capture

**Run by:** Dr. Hussein Hazemi, from a machine with real network access
(`http://malin:8080/his-general/api/directory/v1`).
**Tooling:** `test_hospital_directory_api_3.ps1` (an earlier, less structured
ancestor of `scripts/verify_contract_alignment.ps1` / the Muslim-Arabic
toolkit — see the 2026-08-25 run in this same folder for the modern version).
**Files:**
- `raw-http-capture.txt` — full, unedited console output of that run.
- `worker-search-diagnosis.md` — the analysis written immediately after,
  once the worker results looked wrong.

## What this run established, first

- **Real IDs are dotted-numeric** (`5690.47148`, `8528.69`, `8528.1309`), not
  the mock's `P-10001`/`D-1001`/`E-5001` style.
- **Every Arabic string in every response body is mojibake-corrupted** —
  classic UTF-8-bytes-read-as-Latin-1 (`Ø¹Ø¨Ø§Ø³` instead of `عباس`). Confirmed
  present on `full_name`, `first_name`, `last_name`, `specialty_name`,
  `department_name` — i.e. every free-text field, not just patient names.
- **Search matching still works underneath the corruption.** The query
  `محمد عباس منصور` was typed correctly (UTF-8, properly percent-encoded) and
  correctly matched 22 real patients (`"total": 22`) — the corruption is in
  how the response is serialized back out, not in how the server reads or
  matches the query.
- **The real `sex` field is a full Arabic word** (`"Ø°ÙØ±"` decodes to `ذكر`,
  "male"), not a 1-character `M`/`F` code. The mock's `Patient.sex` column is
  `String(1)` and cannot store this shape.
- **Real scale**: 321 doctors, 1667 workers (compare the mock's 50/100).
- **`department_id`/`department_name`/`job_title` are frequently `null`** in
  real doctor and worker records — sparse data is normal, not a bug.
- **`/health` returns more fields than the mock**: `status`, `service`,
  `api_version`, `timestamp` — the mock only returns `status`.
- **Worker `q` looked non-functional** — the first sign of what got fully
  confirmed on 2026-08-25 (see `worker-search-diagnosis.md`).
