# Proposed addendum to OpenAPI v1.1 — patient encounter type (inpatient/outpatient)

## 1. Context worth confirming with the vendor directly

Before the actual ask: HCAT's own integration notes
(`Version 1.1/HOSPITAL_DIRECTORY_API_INTEGRATION.md`, §6) record this as
confirmed through real testing against the production system:

> "Identity model — patients are visit-scoped, not person-scoped... the
> same real person can appear more than once under separate `patient_id`s
> (e.g. repeat admissions, each entered slightly differently)."

In other words, each `patient_id` already behaves like one admission
record in practice, not a deduplicated person, regardless of what the
`Patient` label in the contract suggests. This has been inferred from
client-side behavior (repeat admissions producing separate ids), never
stated by the vendor directly. **Worth asking them to confirm this
explicitly** — it's the basis for the request below, and for how HCAT's
own dedup logic already has to work around it.

## 2. The problem this solves

A HCAT user has asked whether a given patient result is an inpatient or
outpatient encounter. There's currently no field for this on `Patient` at
all.

This is *not* the same kind of ask as the visit-level fields (room, bed,
admission date, etc.) that were deliberately dropped from `Patient` when
it moved from a visit-scoped to a person-scoped model
(`API_Implementation_Requirements.md` §2.1) — those were dropped because a
single value can't honestly describe a person with many different
admissions. But per §1 above, each `patient_id` here already corresponds
to one specific record/encounter, not a merged person. So an
encounter-type field describing *that one record* is coherent in a way a
person-level field wouldn't be — it's answering "what kind of visit does
this row represent," not "what kind of patient is this person, in
general."

## 3. Proposed change

Not a new endpoint — an edit to the existing `Patient` schema, returned by
`GET /patients` (list) and `GET /patients/{patient_id}` (single).

### Add one field

| Field | Type | Nullable | Description |
|---|---|---|---|
| `encounter_type` | string | Yes | `"inpatient"` or `"outpatient"` (exact allowed values to be confirmed by the vendor — may already exist as a coded value in the source system, same as `sex`). `null` when not recorded. |

## 4. OpenAPI fragment (ready to merge into v1.1 → v1.2)

```yaml
    Patient:
      type: object
      required:
      - patient_id
      - full_name
      properties:
        patient_id:
          type: string
        full_name:
          type: string
          nullable: true
        first_name:
          type: string
          nullable: true
        last_name:
          type: string
          nullable: true
        birth_date:
          type: string
          format: date
          nullable: true
        age:
          type: integer
          nullable: true
        sex:
          type: string
          nullable: true
        encounter_type:
          type: string
          nullable: true
          description: |
            Whether this specific record represents an inpatient or
            outpatient encounter. Allowed values to be confirmed by the
            source-system owner (see open items) -- may resolve through
            the same codes service `sex` already uses. Describes this one
            record/admission, not a permanent trait of the person (see
            the identity-model note in the companion document).
          example: outpatient
```

## 5. Open items to raise with the vendor, not guess at

1. Exact allowed values (`inpatient`/`outpatient` only, or more encounter
   types — e.g. emergency, day-case?).
2. Whether `patient_id` is confirmed to be one-per-admission as observed,
   or whether there's a separate stable person-level identifier (MRN or
   equivalent) the vendor could expose instead/in addition — this would
   be more valuable than `encounter_type` alone, since it would let HCAT
   group a person's admissions authoritatively instead of by
   name+birth_date heuristics.

## 6. What this does NOT change

- No change to `/patients`' search rules, auth, pagination, or error
  behavior.
- Does not reopen room/bed/phone/admission-date/mother-name — those stay
  out per the existing person-vs-visit design decision; this field is
  narrower and justified separately (§2).
- Does not touch `/doctors` or `/workers`.
