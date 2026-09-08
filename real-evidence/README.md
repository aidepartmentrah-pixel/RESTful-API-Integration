# Real Vendor API Evidence

This folder holds raw, unedited evidence from actual HTTP round trips against
the **real** Hospital Directory API — not the mock, not inference, not a
guess. Claude has no network path to the real server (see
`2026-08-25_muslim-arabic-toolkit-run/README.md` for why); every fact below
was produced by a human running a test script from a machine that has real
access, and is traceable to a specific source file in this folder.

**If a future session says "we don't know what the real API does" — check
here first.** Something below might already answer it. If it's not here,
it's genuinely open, and that's worth saying explicitly rather than guessing.

## Confirmed facts

Each row cites the file that proves it. Open that file to see the exact
request and response, not a paraphrase.

### Patient search (`GET /patients`)

| Fact | Source |
|---|---|
| No criteria → `422 VALIDATION_ERROR` (not `400`) | `2026-08-17.../raw-http-capture.txt` |
| A `q` with fewer than **3** words → `422 VALIDATION_ERROR`. Exact message: *"Please enter the patient's full name (first, father and last name), not just part of the name"* | `2026-08-25.../report.md`, `patient_search` — 7/7 two-word queries rejected |
| A 3-word `q` (first + father + last) passes the gate and can match | `2026-08-25.../report.md`, `patient_search.matrix` — 1/1 three-word query tested, 10 matches |
| Real patient IDs are dotted-numeric (`5690.47148`, `8528.69`), not `P-XXXXX` | `2026-08-17.../raw-http-capture.txt` |
| Duplicate full names are real and common — a single full-name search matched 5 patients sharing the identical name | `2026-08-17.../raw-http-capture.txt` |
| The name `محمد عباس منصور` reproducibly returns `total=22`, on two different days | `2026-08-17.../raw-http-capture.txt` and `2026-08-25.../report.md` |
| `sex` is a full Arabic word (e.g. the word for "male"), not a 1-char `M`/`F` code — the mock's `String(1)` column can't even store this | `2026-08-17.../raw-http-capture.txt` |
| **Not yet fully confirmed:** matching past the 3-word gate may not require exact word order (`محمد حسن رحال` matched a record stored as `حسن محمد رحال`) — one data point, needs a dedicated re-test | `2026-08-25.../report.md`, `patient_search.matrix` |

### Doctor search (`GET /doctors`)

| Fact | Source |
|---|---|
| `q` genuinely filters server-side (different words → different, non-trivial counts) | `2026-08-25.../report.md`, `doctor_search` |
| `department_id`/`department_name` frequently `null` in real data | `2026-08-17.../raw-http-capture.txt` |
| Real scale: ~321–322 doctors total | both captures |

### Worker search (`GET /workers`)

| Fact | Source |
|---|---|
| `q` is silently ignored — a search and a no-search request return the identical total | `2026-08-17.../worker-search-diagnosis.md` (first suspected) and `2026-08-25.../report.md` (reconfirmed with a different query, `total=1668` both ways) |
| `job_title`/`department_*` frequently `null` in real data | `2026-08-17.../raw-http-capture.txt` |
| Real scale: ~1667–1668 workers total | both captures |

### Cross-cutting

| Fact | Source |
|---|---|
| Every Arabic string in every response body is mojibake-corrupted (UTF-8 read as Latin-1) — but the underlying search *matching* still works correctly underneath the corruption | `2026-08-17.../raw-http-capture.txt`, reconfirmed `2026-08-25.../report.md` |
| `POST` (or any non-GET) to any endpoint returns `500 SERVER_ERROR`, not the documented `405 METHOD_NOT_ALLOWED` | `2026-08-25.../report.md`, `errors` — all 4 resource groups |
| `Content-Type` is `application/json` only, missing the contract-required `; charset=utf-8` suffix | `2026-08-25.../report.md`, `encoding` |
| Missing API key and wrong API key return the identical `401` message | `2026-08-25.../report.md`, `auth` |
| `/health` returns extra fields the mock doesn't: `service`, `api_version`, `timestamp` | both captures |

## Known mock/real divergences these facts expose

- `app/services/patient_service.py` enforces a **2-word** minimum; the real
  server requires **3**. The 2-word choice was a deliberate compromise (the
  mock's `Patient` model has no father-name field) — now confirmed to not
  match reality.
- `app/repositories/worker_repository.py` filters on `q`; the real server
  ignores it entirely. The mock is currently *more* capable than the real
  system here, which is its own kind of mismatch — testing against the mock
  gives false confidence that worker search works.
- Neither the mock's `405` handling nor its `Content-Type` charset behavior
  has been checked against these two new real-server findings yet.

None of the above has been applied to the mock yet — this folder is the
evidence, not the fix. Ask for the mock/doc updates as a separate step.

## Folders

- `2026-08-17_first-real-server-capture/` — the first real-server round trip:
  established the mojibake bug, real ID format, real `sex` shape, real scale,
  and first suspicion of the worker `q` bug.
- `2026-08-25_muslim-arabic-toolkit-run/` — a much larger, purpose-built run
  using curated Muslim Arabic names: confirmed the real 3-word patient gate,
  reconfirmed the worker bug independently, and found the two new `POST`/
  `Content-Type` gaps.
