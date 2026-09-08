# HCAT integration reference — Hospital Directory API v1.1

What HCAT's client code needs to send and expect, per the vendor's v1.1
contract, now implemented in this mock. See
`2026-09-08_v1.1-gap-analysis.md` for the full reasoning; this file is just
the copy-pasteable target.

## Base

- Every endpoint except `/health` requires header `X-API-Key: <shared secret>`.
- Every response is `application/json`.
- All IDs (`patient_id`, `doctor_id`, `employee_id`) are **plain numeric
  strings — treat as opaque**. Do not parse them, do not assume a fixed
  length or prefix, do not reformat them for display beyond showing them
  as-is.

## `GET /patients` — search

Send **one of these two shapes only**:

- `patient_id=<value>` (exact match), **or**
- `first_name=<value>&father_name=<value>&last_name=<value>` (all three
  required together).

Anything else — a lone name field, or first+last without father — gets
`422 VALIDATION_ERROR`:
```json
{"error": "VALIDATION_ERROR", "message": "Provide 'patient_id', or all three of 'first_name', 'father_name' and 'last_name'"}
```
If HCAT's UI collects first/father/last as three separate boxes (as it
already does today), send them as three separate query parameters — do
**not** join them into a single string. `father_name` is a search input
only; it is never present in the response.

Each field matches as a case-insensitive substring against only its own
column (never cross-matched), against either the Arabic or English stored
variant. `limit` (default 100, max 500) / `offset` (default 0) as usual.

**Important, unresolved:** this structured-fields shape is what the
vendor's written contract (v1.1) specifies, but it has not yet been tested
against the real production server — every real-server observation so far
used a single joined free-text string instead. If HCAT switches to this
shape against production and gets unexpected results (e.g. everything
rejected, or `father_name` seemingly ignored), that's the first thing to
suspect and report back, not a bug in HCAT's request construction.

### Patient response shape
```json
{
  "patient_id": "10025",
  "full_name": "Ø£Ø­ÙØ¯ Ø¹ÙÙ Ø­Ø³Ù",
  "first_name": "Ahmad",
  "last_name": "Hassan",
  "birth_date": "1990-01-15",
  "age": 36,
  "sex": "Male"
}
```
All fields always present; unavailable values are `null`, never omitted or
an empty string. `sex` is a resolved display string, not a fixed code —
don't hardcode an `M`/`F` enum against it.

## `GET /patients/{patient_id}`

Exact lookup. Non-numeric or unknown id → `404 PATIENT_NOT_FOUND` (never
`400`).

## `GET /doctors` — search (unchanged behavior, optional)

- `q` (optional): case-insensitive substring, OR-matched across full name,
  first/father/last name, assistant number, and the numeric id as text. Omit
  for the default active-doctors list.
- `active_only` (default `true`), `limit`/`offset` as usual.
- `department_id`/`department_name` are **always `null` today** — don't
  build UI that assumes they're populated.

## `GET /workers` — listing only, **no search parameter**

`q` and `active_only` **do not exist on this endpoint** — don't send them,
they have no effect. Only `limit` (default **10**, not 100) and `offset`.
Always returns active workers only. If HCAT needs filtered worker search,
that has to be implemented client-side (fetch pages and filter locally) —
this is a real, currently-open gap on the real server, not something this
contract update resolves.

`GET /workers/{employee_id}`: `is_active` is **always `true`** on this
specific route regardless of the worker's actual status (an HR API quirk,
not a bug) — don't treat it as authoritative; use the list endpoint's
`is_active` for actual status.

## `GET /health` — no auth required
```json
{"status": "healthy", "service": "his-general-directory", "api_version": "1.0.0", "timestamp": "2026-09-08T10:15:00Z"}
```
`503` + `status: "unhealthy"` when the backing database is unreachable.

## Error shape (every non-2xx)
```json
{"error": "<CODE>", "message": "<human text>"}
```
| Status | Code |
|---|---|
| 401 | `UNAUTHORIZED` |
| 404 | `PATIENT_NOT_FOUND` / `DOCTOR_NOT_FOUND` / `WORKER_NOT_FOUND` / `NOT_FOUND` (unknown route) |
| 405 | `METHOD_NOT_ALLOWED` |
| 422 | `VALIDATION_ERROR` |
| 500 | `SERVER_ERROR` |
| 503 | `SERVICE_UNAVAILABLE` |

## Things this update does NOT fix — still HCAT's own concern against the real server

These are real production bugs on the vendor's side, confirmed by direct
testing, that this mock deliberately does **not** reproduce (the mock
represents the contract, not the vendor's current bugs):

- **Mojibake Arabic text**: every Arabic string in every real response is
  UTF-8 read back as Latin-1. Fix by re-encoding as Latin-1 then decoding as
  UTF-8 on receipt.
- **IDs are dotted-numeric** on the real server (e.g. `5690.47148`), not the
  plain-numeric shape this contract describes — keep treating IDs as opaque
  strings regardless.
- **`Content-Type` on the real server omits `charset=utf-8`** — don't rely
  on the header for decoding; decode as UTF-8 (after the mojibake fix
  above) unconditionally.
- **`POST` to any real endpoint returns `500`, not `405`** — not relevant
  unless HCAT ever sends a non-GET request, which it shouldn't.

None of this changes what HCAT sends — only how it should interpret and
recover from what the real server (not this mock) sends back.
