# Proposed new endpoint — live ER visit roster (for HCopilot)

## 1. Context

HCopilot currently requires a nurse to manually search for and select a
patient (via the Hospital Directory API's structured search) before
starting ISBAR data collection. The goal is to replace that with a live
roster of who's currently in the ER, pulled directly from the ER
system — a nurse picks a name off the list instead of typing a search.

This is **not** an extension of the existing Hospital Directory API.
Direct inspection (browser network capture against the ER page,
`visit-er-list.xhtml`) confirms the ER system runs on a separate host
(`meraj:8080`) on a completely different stack (JSF/PrimeFaces,
server-rendered HTML) than the Hospital Directory API (`malin:8080`,
clean JSON REST). These are two different systems. This proposal is for
a new, narrowly-scoped endpoint — not a redesign of anything existing.

**What HCopilot already owns and is explicitly NOT part of this ask:**
bed allocation (the ER system has no concept of it — HCopilot assigns
beds itself), triage time (internal clinical workflow data, not tracked
by 3iSoft), and departure-time entry (HCopilot's own "soft departure"
action, cross-checked against this feed — see §5).

## 2. Proposed endpoint

### `GET /er/current-visits` (exact path to match whatever convention 3iSoft prefers)

Returns every patient currently present in the ER, as a complete,
unpaginated snapshot — the full list on every call, not a page of it.
See §4 for why pagination is deliberately excluded.

### Request

No parameters. Same `X-API-Key` auth as every other endpoint in this
integration.

### Response — `200 OK`

```json
{
  "success": true,
  "items": [
    {
      "er_visit_id": "48213",
      "first_name": "عباس",
      "father_name": "محمد",
      "last_name": "زهرالدين",
      "arrival_time": "2026-09-18T14:32:00+03:00",
      "gender": null,
      "age": null,
      "chief_complaint": null
    }
  ],
  "total": 1
}
```

No `limit`/`offset` — see §4. Ordered by `arrival_time` ascending
(earliest arrival first); needs vendor confirmation this is achievable,
but *some* explicit, stable order should be specified so the list
doesn't reshuffle unpredictably between polls.

## 3. Field-by-field format specification

Precision matters here more than usual — these values feed KPI math
(wait times, length of stay) already computed and displayed on
HCopilot's own dashboard, so a format mismatch wouldn't error, it would
silently produce wrong numbers.

| Field | Status | Format | Notes |
|---|---|---|---|
| `er_visit_id` | Confirmed exists (visible on page) | **string**, not integer | Same rule as every other id in the Hospital Directory contract: "identifiers are for identity, never arithmetic," even if stored as a number internally. Used as the correlation/diff key (see §5), never as HCopilot's own primary key. |
| `first_name` | Confirmed exists | string | Plain value, no Arabic/English split needed — unlike `Patient`, this endpoint isn't searched by name, only displayed and correlated by `er_visit_id`. |
| `father_name` | Confirmed exists (page calls it "middle name"; using the vendor's own established term here for consistency with the Directory API contract) | string | Same reasoning as `first_name`. |
| `last_name` | Confirmed exists | string | Same reasoning as `first_name`. |
| `arrival_time` | Confirmed exists, but currently split into two page fields (date of creation + time of creation) | ISO-8601 with timezone offset, `YYYY-MM-DDTHH:MM:SS±HH:MM` | Ask for **one combined field**, not two. Also confirm explicitly: (a) is "creation time" really arrival time, and (b) what timezone the server writes — assumed Beirut (UTC+3), needs vendor confirmation, not an assumption to build on. |
| `gender` | **Open item** — not shown on the page, presumed to exist in the underlying record | string, `null` if absent | Do not assume a shape. The Hospital Directory API's own `sex` field is a confirmed example of vendor documentation (English example `"Male"`) not matching real production data (a full Arabic word) — the exact same conceptual field has already been wrong once in this vendor's own contract. Ask what this will actually contain before building UI around it. |
| `age` | **Open item** — not shown on the page | integer, `null` if absent — **or, preferably, ask for `birth_date` instead** | A raw `age` value goes stale mid-stay if it crosses a birthday. The existing Patient contract already prefers deriving age from `birth_date` for this reason — same logic applies here. |
| `chief_complaint` | **Open item** — not on the live page, but known to exist server-side (it populates a printed PDF) | string, `null` if absent | Ask explicitly whether this is free text or a coded value on their side. HCopilot's own Statistics dashboard already groups visits by complaint category — a code would be far more reliable to group on than free text, and this project has already hit real problems from fuzzy-matching free text elsewhere (patient names). |

**Excluded on purpose:** `doctor_name` — the field exists on the ER
page, but is confirmed empty in practice (ER clerks never fill it in).
Not worth asking for data that's known to be blank.

**Encoding — call this out explicitly, don't assume it'll be fine.**
`Content-Type: application/json; charset=utf-8`, correct UTF-8
throughout. This vendor's system has a **confirmed** existing defect
elsewhere (Arabic text corrupted via UTF-8-read-as-Latin-1, verified by
direct capture against the real Hospital Directory API). This endpoint
is entirely Arabic names and text — flag the known defect and ask them
to verify it doesn't recur here, rather than discovering it after go-live.

## 4. Why no pagination

Every other list endpoint in this contract has `limit`/`offset`. This
one deliberately doesn't, because the departure-detection mechanism
(§5) requires a **complete** snapshot on every poll — a paginated
partial view would make someone who simply fell off the current page
look like they'd left the ER. ER headcount is bounded (dozens, not
thousands), so returning everything every time is cheap and correct.
This is a deliberate deviation from the pattern elsewhere in the
contract, not an oversight — worth saying so explicitly when this is
proposed, so it doesn't read as an inconsistency.

## 5. How this gets used (for context, not part of the ask)

- **Live roster display**: poll this endpoint, render `items` directly.
- **Change detection**: compare `total` between polls — cheap, no
  reason for a separate lightweight endpoint just to check "did
  anything change."
- **Departure detection**: on each poll, diff this call's set of
  `er_visit_id`s against the previous poll's set. Anyone present last
  time and missing now is treated as departed — a plain set
  subtraction, not a search, and fast regardless of headcount size.
  This is the "double departure" check described in HCopilot's own
  design: a nurse's manual departure action is authoritative when it
  happens, this feed catches anyone the nurse forgot.
- **Identity strategy**: `er_visit_id` is stored as a reference field
  on HCopilot's own stay record, never adopted as HCopilot's own
  primary key — same pattern already used for the Hospital Directory
  API's `patient_id` (`ext__<id>` encoding in `hospital_directory_client.py`).

## 6. What this does NOT change

- No change to the Hospital Directory API (`/patients`, `/doctors`,
  `/workers`) — this is a new endpoint on a separate system.
- No bed, triage, or departure-time fields requested — all confirmed
  internal to HCopilot.
- No write/update capability requested — read-only, matching the
  existing contract's own "strictly read-only" principle.

## 7. Open items to resolve with the vendor before/while building

1. Exact timezone of `arrival_time` values (assumed UTC+3, unconfirmed).
2. Shape of `gender` — enum, coded value, or resolved display string
   (given the `sex` precedent already being inconsistent).
3. Whether `age` or `birth_date` is available, and which is preferred.
4. Whether `chief_complaint` is coded or free text on their side.
5. Whether stable ordering (e.g. `arrival_time` ascending) is something
   they can guarantee.
6. Confirm UTF-8 encoding is correct on this endpoint specifically —
   don't assume it inherits the fix from wherever the existing mojibake
   defect gets resolved (if it does).
