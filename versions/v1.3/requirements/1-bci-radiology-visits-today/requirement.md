# Proposed new endpoint — today's BCI visits (for the BCI clinic platform)

## 1. Context

The BCI (heart) center's clinic platform needs the list of patients who
have a visit registered **today**, so a nurse or doctor picks a patient
from the list instead of typing names. Nobody should type a name that
3iSoft already holds.

The data is not in the Hospital Directory API. It lives in the
radiology module (`his-radiology`) on `meraj:8080`, a JSF application
with no JSON API. The captured pages (field names only, see
`../../evidence.md`) are the finished-visits list and the visit card.
Like the ER ask (v1.2 requirement 5), this is a new, narrow, read-only
endpoint on the same Directory API host, auth and conventions, however
3iSoft sources it internally.

**Today only.** Old visits are not requested. When a visit appears in
the list (at booking, at registration, at payment) is 3iSoft's business:
the platform takes whatever the list holds, with the names it gives.

**What BCI owns and does NOT ask for:** clinic notes, reports, the
operation record, follow-up calls. Nothing is written back.

## 2. Proposed endpoint

### `GET /bci-radiology/visits/today`

Every BCI visit registered today, as one complete, unpaginated
snapshot. "Today" is the calendar day in **Asia/Beirut** at the moment
of the call. No parameters. Same `X-API-Key` auth as every other
endpoint.

### Response — `200 OK`

```json
{
  "success": true,
  "items": [
    {
      "visit_id": "V9999-0007",
      "mrn": "9999.100007",
      "first_name_ar": "عمار", "father_name_ar": "كاظم",
      "last_name_ar": "الجبوري", "mother_name_ar": "أمل",
      "first_name_en": "Ammar", "father_name_en": "Kazem",
      "last_name_en": "Al-Jubouri", "mother_name_en": "Amal",
      "birth_date": "1972-01-25",
      "sex": "Male",
      "visit_time": "2026-11-04T08:00:00+02:00",
      "visit_kind": "scheduled",
      "doctor_name": "Dr. Test-A",
      "status": "registered"
    }
  ],
  "total": 1
}
```

(Invented test data: MRNs `9999.*`, visit numbers `V9999-*`.)

**Order:** `visit_time` ascending, then `visit_id`, so the list does not
reshuffle between calls.

## 3. Fields

| Field | On the captured pages? | Format | Notes |
|---|---|---|---|
| `visit_id` | Yes: "الرقم" (number) on the finished-visits list, the link to the card | string | Opaque, never arithmetic. Stored by BCI as a link, never as its own key. |
| `mrn` | Yes: "رقم المريض" (patient number), shaped `NNNN.NNNNNN` | string | Opaque; contains a dot. Key for requirement 2. Whether it is per person or per visit is an open item. |
| `first_name_ar`, `father_name_ar`, `last_name_ar`, `mother_name_ar` | Yes: الإسم، إسم الأب، الشهرة، إسم الأم | string, null if absent | `last_name` is the family name (الشهرة), the word the Directory contract already uses. Mother's family name (شهرة الأم) is not requested. |
| `first_name_en` … `mother_name_en` | Partly: the visit card has a foreign-names dialog | string, null when not stored | Many patients have Arabic only. |
| `birth_date` | Yes: تاريخ الولادة on the card | `YYYY-MM-DD`, null if absent | Preferred to `age` (age goes stale). |
| `sex` | Yes: الجنس on the card | string, null if absent | **Shape to confirm.** The real Directory API returns a full Arabic word where its documentation says `"Male"`. The client must accept both. |
| `visit_time` | Partly: the card and list show a **date** (تاريخ الزيارة / التاريخ); **no time of day seen** | ISO-8601 with the Asia/Beirut offset of that day (`+02:00` winter, `+03:00` summer) | Ask for date and time in one field. |
| `visit_kind` | No direct field. The appointment page has "book from the waiting list" and urgent flags | `scheduled` (came from an appointment) or `walk_in`; null if unknown | How 3iSoft can tell is an open item. |
| `doctor_name` | Yes: "الطبيب المعالج" (treating physician) | string, null if absent | As 3iSoft displays it. The booking page shows doctors as "name / specialty / number": an id may follow later. |
| `status` | Partly: a "freeze the visit" action with a reason (note only, not seen by the capture script) and "cancel the order" | string: `registered`, or `frozen` | Passed through as given; other values may exist. No special handling. |

**Not requested:** invoice number, prices, discounts, guarantor,
insurance status, performed items, HL7 file number, anesthesia doctor,
the "has problems (blacklist)" flag, residence, marital status, email.

**Encoding:** `Content-Type: application/json; charset=utf-8`. Most
values are Arabic. The vendor has a confirmed UTF-8 defect elsewhere
(Arabic read as Latin-1); please check this endpoint specifically.

## 4. Errors

Same shapes as the rest of the contract (`{"error", "message"}`).

| Code | When |
|---|---|
| `401 UNAUTHORIZED` | Missing or wrong `X-API-Key` |
| `500 SERVER_ERROR` | Unexpected error |
| `503 SERVICE_UNAVAILABLE` | The source of visits cannot be read |

**Never `200` with an empty list when the source is down.** An empty
list must mean "no BCI visits today", nothing else; the clinic would
otherwise read a failure as an empty day.

## 5. Why no pagination

Like `/er/current-visits`: the clinic sees about 50 patients a day, and
the platform compares the whole list between calls to see who arrived.
A partial page would make patients look absent.

## 6. Open items for 3iSoft

1. **BCI only:** which rule tells a BCI visit from a RAH visit (machine name, center number "رقم المركز", or doctor)? 3iSoft applies it on its side.
2. **Clinic visits:** do clinic visits without a machine exist as visits in the radiology module, or somewhere else? Every captured finished visit has a machine.
3. **Time of day:** is the visit time stored, or only the date? Which moment is it (booking, registration, arrival)?
4. **Time zone:** confirm the server writes Asia/Beirut local time.
5. **Scheduled or walk-in:** can it be derived (the visit came from an appointment booking or not)?
6. **Status values:** how frozen and cancelled visits appear; the full list of values.
7. **MRN:** is رقم المريض per person or per visit, and is it the Directory API's `patient_id`?
8. **Sex:** the exact values returned.
9. **UTF-8** on this endpoint.
10. **Doctor:** is a doctor id available as well as the name?
