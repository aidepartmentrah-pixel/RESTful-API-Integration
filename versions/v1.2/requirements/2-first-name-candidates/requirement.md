# Proposed addendum to OpenAPI v1.1 — family-name search

## 1. Decision

Add this endpoint:

### `GET /patients/first-names`

This endpoint receives a family name (`last_name`) and returns the distinct
first-name candidates found under that family name.

It should **not** return full patient records. Returning every patient from a
family-name-only search would weaken the deliberate restriction already present
in `GET /patients`, where a patient can be retrieved only by `patient_id` or by
the complete `first_name + father_name + last_name` combination.

The new endpoint creates a safe, progressive search flow:

1. Search by family name using `GET /patients/first-names`.
2. Select a first name from the returned candidates.
3. Retrieve father-name candidates using `GET /patients/father-names`.
4. Select a father name.
5. Retrieve the actual patient record(s) using the existing `GET /patients`.

Example flow:

```text
Zahreddine
  -> Abbass
    -> Mohammad
      -> GET /patients?first_name=Abbass&father_name=Mohammad&last_name=Zahreddine
```

This means the existing restricted `/patients` endpoint does not need to be
changed.

## 2. Proposed endpoint

### `GET /patients/first-names`

Returns the distinct first-name values found for a supplied family name, so the
caller can ask the user to choose the correct first name before continuing to
father-name disambiguation.

### Request

| Parameter | Required | Description |
|---|---:|---|
| `last_name` | Yes | Case-insensitive substring match against the Arabic or English last-name column only, using the same matching semantics as `GET /patients`. |
| `limit` | No | Maximum number of distinct first-name candidates returned. Default `50`, minimum `1`, maximum `200`. |

Example:

```http
GET /patients/first-names?last_name=زهرالدين&limit=50
X-API-Key: <api-key>
```

`last_name` must contain a non-blank value after trimming. A missing or blank
value returns `422 VALIDATION_ERROR`:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "'last_name' is required"
}
```

The endpoint uses the same `X-API-Key` authentication as the other directory
endpoints. A missing or invalid key returns `401 UNAUTHORIZED`.

## 3. Successful response

### `200 OK`

```json
{
  "success": true,
  "last_name": "زهرالدين",
  "candidates": [
    {
      "first_name": "عباس",
      "patient_count": 12
    },
    {
      "first_name": "حسن",
      "patient_count": 8
    },
    {
      "first_name": "محمد",
      "patient_count": 5
    }
  ],
  "total_candidates": 3
}
```

Response rules:

- `candidates` contains one entry per distinct, non-blank first-name value among
  patients matching `last_name`.
- `first_name` uses the same display fallback as the existing patient contract:
  use the English value when stored; otherwise use the Arabic value.
- `patient_count` is the number of patient records found for that first-name and
  last-name combination, regardless of father name.
- Candidates are ordered by `patient_count` descending. Ties should be ordered
  alphabetically by the displayed `first_name` to keep the response stable.
- `total_candidates` is the number of distinct matching first-name candidates
  before applying `limit`.
- Blank first names are excluded because the caller cannot use them in the next
  step.
- No `patient_id`, birth date, sex, or complete patient record is returned from
  this endpoint.

If the family name has no matches, that is a normal successful response rather
than an error:

```json
{
  "success": true,
  "last_name": "اسم غير موجود",
  "candidates": [],
  "total_candidates": 0
}
```

## 4. Errors

| Status | When | Error code |
|---:|---|---|
| `401` | `X-API-Key` is missing or invalid | `UNAUTHORIZED` |
| `422` | `last_name` is missing/blank, or `limit` is outside `1..200` | `VALIDATION_ERROR` |
| `500` | Unexpected server error | `SERVER_ERROR` |

## 5. Relationship to the other patient endpoints

| Search stage | Endpoint | Returns |
|---|---|---|
| Family name entered | `GET /patients/first-names?last_name=...` | First-name candidates |
| First name selected | `GET /patients/father-names?first_name=...&last_name=...` | Father-name candidates |
| Full name confirmed | `GET /patients?first_name=...&father_name=...&last_name=...` | Actual patient records |
| Patient ID known | `GET /patients/{patient_id}` | One exact patient |

The first two endpoints are candidate/disambiguation endpoints. Only the final
two endpoints return patient records.

## 6. Suggested OpenAPI path definition

```yaml
/patients/first-names:
  get:
    tags:
      - Patients
    summary: List first-name candidates for a family name
    description: |
      Returns distinct first-name candidates among patients whose Arabic or
      English last-name column matches `last_name` case-insensitively as a
      substring. This is a narrowing step and does not return patient records.
    parameters:
      - name: last_name
        in: query
        required: true
        description: |
          Family name to match against the Arabic or English last-name column
          only. Matching is case-insensitive and uses substring semantics.
        schema:
          type: string
          minLength: 1
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          minimum: 1
          maximum: 200
          default: 50
    responses:
      '200':
        description: First-name candidates; an empty result is a normal 200.
      '401':
        $ref: '#/components/responses/Unauthorized'
      '422':
        description: Missing/blank last_name or an invalid limit.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
      '500':
        $ref: '#/components/responses/ServerError'
```

The final OpenAPI update should also define explicit reusable schemas for the
successful response and each candidate item, instead of leaving the `200`
response body untyped.

## 7. Backend acceptance criteria

- A valid family name returns distinct first-name candidates and their counts.
- Arabic and English last-name columns are both searched, but no unrelated name
  column is searched.
- Matching remains case-insensitive substring matching, consistent with v1.1.
- Whitespace-only `last_name` values are rejected.
- Blank first-name records are excluded.
- Duplicate patient rows affect `patient_count` but do not create duplicate
  candidate entries.
- Ordering is deterministic: count descending, then displayed first name.
- No match returns `200` with an empty `candidates` array.
- Authentication and error bodies follow the existing API conventions.
- The restrictions and behavior of `GET /patients` remain unchanged.

## 8. Final recommendation

Create `GET /patients/first-names?last_name=...` as the new endpoint. It is the
symmetrical companion to `GET /patients/father-names`, supports family-name-only
search through controlled narrowing, and avoids exposing a potentially large
list of patient records from a broad surname query.
