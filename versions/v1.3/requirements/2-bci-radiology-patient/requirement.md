# Proposed new endpoint — one BCI patient by MRN (for the BCI clinic platform)

## 1. Context

When a patient is picked from today's list (requirement 1), the clinic
platform needs a few more details than the list carries: the mother's
name, the phone numbers with whose number each is (for the follow-up
calls), the allergy flag, nationality and ID number. All of them are on
the radiology module's visit card (captured, field names only, see
`../../evidence.md`).

This is a lookup of one record, not a search. It is the companion of
`/bci-radiology/visits/today`: the `mrn` comes from that list.
The existing `/patients/{patient_id}` stays as it is (it has no mother's
name, phones or allergy flag, and its `patient_id` may not be the same
number; open item).

## 2. Proposed endpoint

### `GET /bci-radiology/patients/{mrn}`

`mrn` exactly as given in the visit list. It contains a dot
(`NNNN.NNNNNN`); match it exactly, never parse it. Same `X-API-Key`
auth.

### Response — `200 OK`

```json
{
  "mrn": "9999.100007",
  "first_name_ar": "عمار", "father_name_ar": "كاظم",
  "last_name_ar": "الجبوري", "mother_name_ar": "أمل",
  "first_name_en": "Ammar", "father_name_en": "Kazem",
  "last_name_en": "Al-Jubouri", "mother_name_en": "Amal",
  "birth_date": "1972-01-25",
  "sex": "Male",
  "nationality": "Iraqi",
  "id_number": "TEST-ID-0007",
  "has_allergy": false,
  "phones": [
    {"number": "00-000-009", "owner": "self"},
    {"number": "00-000-010", "owner": "brother"}
  ]
}
```

(Invented test data.) A single object, like `/patients/{patient_id}`;
no envelope.

## 3. Fields

The names, `birth_date` and `sex` follow requirement 1 exactly (same
names, same formats, same open item on `sex`).

| Field | On the captured pages? | Format | Notes |
|---|---|---|---|
| `mrn` | Yes: رقم المريض | string | Opaque. |
| `nationality` | Yes: الجنسية (not mandatory) | string, null if absent | Coded or free text: open item. |
| `id_number` | Yes: رقم الهوية (not mandatory) | string, null if absent | |
| `has_allergy` | Yes: لديه حساسية, on the patient part and the visit part of the card | boolean | Which one (patient or visit) and what it covers (contrast agents or any allergy): open item. |
| `phones` | Yes: "phone numbers *" with "owner of the number *", both mandatory | array of `{number, owner}`, may be empty | `number` as stored, not reformatted. `owner` is from a list of 5 options: their values are an open item. |

**Not requested:** birth place, civil-registry number and place,
husband's family, marital status, email, residence, floor, side, death
flag, the "has problems (blacklist)" flag, notes, anything about money.

**Encoding:** UTF-8, as requirement 1.

## 4. Errors

| Code | When |
|---|---|
| `401 UNAUTHORIZED` | Missing or wrong `X-API-Key` |
| `404 PATIENT_NOT_FOUND` | No patient with this MRN (same code as `/patients/{patient_id}`) |
| `500 SERVER_ERROR` | Unexpected error |
| `503 SERVICE_UNAVAILABLE` | The source cannot be read |

## 5. Open items for 3iSoft

1. **MRN:** per person or per visit; one person can have several MRNs (seen in practice): is there any link between them on 3iSoft's side?
2. **Phones:** do they belong to the patient file or to each visit card? The 5 values of "owner of the number".
3. **Allergy:** the patient's flag or the visit's; what it covers.
4. **Nationality:** coded or free text.
5. **Sex:** the exact values (as requirement 1).
6. **UTF-8** on this endpoint.
