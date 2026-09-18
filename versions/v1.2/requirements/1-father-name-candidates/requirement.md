# Proposed addendum to OpenAPI v1.1 — father-name candidate lookup


## 2. Proposed endpoint

### `GET /patients/father-names`

Returns the distinct father-name values on file for a given first+last
name pair, so a caller can present them for the user to pick from (or
re-query `/patients` directly once a value is confirmed) — replacing 32
blind guesses with one authoritative lookup.

#### Request

| Parameter | Required | Description |
|---|---|---|
| `first_name` | Yes | Case-insensitive substring match, same semantics as `/patients`'s `first_name` (matches the Arabic or English first-name column). |
| `last_name` | Yes | Case-insensitive substring match, same semantics as `/patients`'s `last_name`. |
| `limit` | No | Max number of distinct father-name candidates to return. Default 50, min 1, max 200. |

Both `first_name` and `last_name` are required — a request missing either
returns `422 VALIDATION_ERROR`:
```json
{"error": "VALIDATION_ERROR", "message": "Both 'first_name' and 'last_name' are required"}
```
Same auth as every other endpoint: `X-API-Key` header, `401 UNAUTHORIZED`
if missing/invalid.

#### Response — `200 OK`

```json
{
  "success": true,
  "first_name": "عباس",
  "last_name": "زهرالدين",
  "candidates": [
    {"father_name": "محمد", "patient_count": 20},
    {"father_name": "حسن", "patient_count": 20},
    {"father_name": "أحمد", "patient_count": 1}
  ],
  "total_candidates": 3
}
```

- `candidates`: one entry per **distinct** father-name value found among
  patients matching `first_name` + `last_name`. Ordered by `patient_count`
  descending (most common first), so a UI can preserve the same
  "most-likely-first" ordering the old 32-name list was trying to
  approximate — except now it's ordering real data instead of a guess.
- `father_name`: the display value for that father name (English variant
  if the source system has one, otherwise Arabic — same fallback rule
  already used for `Patient.first_name`/`Patient.last_name` in v1.1).
- `patient_count`: how many patient records exist under this exact
  first+father+last combination. This number alone communicates whether a
  candidate is a single real person or a heavily-duplicated one (e.g. many
  admissions under one identity) — the caller does not need to fetch the
  full record list just to know that.
- No `patient_id` and no individual patient records here by design — this
  is a narrowing/disambiguation step. Once the caller has a confirmed
  `father_name`, it re-queries the existing `GET /patients` with all three
  fields to get the actual patient records (ids, birth dates, etc.).
- An unmatched `first_name`/`last_name` pair is **not an error**: `200`
  with `candidates: []` and `total_candidates: 0`, same "empty result is a
  normal 200, not a 404" convention as every other search endpoint in this
  contract.

#### Errors

| Status | When | `error` code |
|---|---|---|
| 401 | Missing/invalid `X-API-Key` | `UNAUTHORIZED` |
| 422 | `first_name` or `last_name` missing/empty, or `limit` out of range | `VALIDATION_ERROR` |
| 500 | Unexpected server error | `SERVER_ERROR` |
