# Proposed addendum to OpenAPI v1.1 — worker section/administration names

## 1. The problem this solves

`GET /workers` and `GET /workers/{employee_id}` already return `section_id`
and `administration_id` on every `Worker` object — but per the v1.1 spec's
own description, both are *"Always `null` today — not exposed by the HR
application yet."* Even once populated, the contract as written only ever
gives a bare ID: there is no `section_name` or `administration_name`
field anywhere in the schema, unlike `department`, which already has both
`department_id` **and** `department_name`.

HCAT has its own internal organizational structure with its own IDs. A raw
ID number from this API means nothing inside HCAT — there is no shared ID
space to resolve it against. A HCAT user has already reported being unable
to identify which section/administration a worker belongs to for exactly
this reason: the ID alone carries zero information on their end.

`department_name` already proves the vendor's system can do this
resolution — its own description says it's *"resolved from his-general's
Department table for `department_id`."* This proposal asks for the same
treatment to be extended to the two fields that were left behind.

## 2. Proposed change

Not a new endpoint — an edit to the existing `Worker` schema, returned by
both `GET /workers` and `GET /workers/{employee_id}`.

### Add two fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `section_name` | string | Yes | Display name resolved from `section_id`, same convention as `department_name`. `null` when `section_id` is `null` or unresolvable. |
| `administration_name` | string | Yes | Display name resolved from `administration_id`, same convention as `department_name`. `null` when `administration_id` is `null` or unresolvable. |

### Also requested: actually populate `section_id`/`administration_id`

The two ID fields already exist in the contract but are documented as
always null. This proposal is only useful once real values are returned —
so the ask is really two parts: (1) start populating `section_id` and
`administration_id` from the HR application, and (2) add the matching
`_name` fields alongside them, the same way `department` already works.

## 3. OpenAPI fragment (ready to merge into v1.1 → v1.2)

```yaml
    Worker:
      type: object
      required:
      - employee_id
      - full_name
      - is_active
      properties:
        employee_id:
          type: string
          example: '205'
        full_name:
          type: string
          nullable: true
        job_id:
          type: string
          nullable: true
        job_title:
          type: string
          nullable: true
        department_id:
          type: string
          nullable: true
        department_name:
          type: string
          nullable: true
        section_id:
          type: string
          nullable: true
        section_name:
          type: string
          nullable: true
          description: |
            Display name resolved from section_id, same fallback/resolution
            convention as department_name. Null when section_id is null or
            unresolvable.
        administration_id:
          type: string
          nullable: true
        administration_name:
          type: string
          nullable: true
          description: |
            Display name resolved from administration_id, same convention
            as department_name. Null when administration_id is null or
            unresolvable.
        is_manager:
          type: boolean
          nullable: true
        is_active:
          type: boolean
```

## 4. What this does NOT change

- No change to `/workers`' request parameters, auth, pagination, or error
  behavior.
- No change to `department_id`/`department_name`, which already work.
- Does not touch `/patients` or `/doctors`.

## 5. Errors

No new error conditions — this is purely additive fields on an existing,
already-working response shape.
