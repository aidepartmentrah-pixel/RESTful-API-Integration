# Proposed new endpoint — today's orthopedic OPD visits (for the Orthopedic OPD app)

> **Status: DRAFT — idea captured 18 Nov 2026, not designed yet.**
> Not in the v1.3 spec, not in the mock, no tests, not sent to 3iSoft.
> This file holds the idea and the questions to decide when we design it.

## 1. Context

The Orthopedic OPD application (`orthopedic-opd-ai-test` repo) manages the
orthopedic outpatient clinic: patient files, appointments, PROM
assessments, follow-up calls and the AI assistant for treatment plans.

Today staff **type every patient in by hand**. The app's `Patient` record
requires a name, MRN, birth date, sex, phone, appointment date and time
(`backend/models.py`), all of which the hospital system already holds.

The idea is the same as the ER roster (v1.2 requirement 5) and today's BCI
visits (v1.3 requirement 1): 3iSoft gives the list of **today's
orthopedic clinic visits with the patients' names**, and staff pick a
patient from the list instead of typing.

## 2. Proposed endpoint (first sketch)

### `GET /orthopedic-opd/visits/today`

Every orthopedic OPD visit registered today, as one complete,
unpaginated snapshot. "Today" = the calendar day in Asia/Beirut at the
moment of the call. No parameters. Same `X-API-Key` auth and error
conventions as the rest of the contract. Path to match 3iSoft's
preference.

Suggested item, mirroring the BCI visit so both clinic apps can share one
client:

```json
{
  "success": true,
  "items": [
    {
      "visit_id": "V9999-0101",
      "mrn": "9999.200001",
      "first_name_ar": "عباس", "father_name_ar": "محمد",
      "last_name_ar": "زهرالدين", "mother_name_ar": null,
      "first_name_en": "Abbass", "father_name_en": "Mohammad",
      "last_name_en": "Zahreddine", "mother_name_en": null,
      "birth_date": "1985-03-12",
      "sex": "Male",
      "visit_time": "2026-11-18T09:30:00+02:00",
      "visit_kind": "scheduled",
      "doctor_name": "Dr. Test-O",
      "status": "registered"
    }
  ],
  "total": 1
}
```

(Invented example data.) Order: `visit_time` ascending, then `visit_id`.

Same rules as BCI: an empty list means "no orthopedic visits today",
never "the source is down" (that is `503`); no pagination, because the app
compares the whole list between calls to see who arrived.

## 3. To decide when we design it

1. **Where the data lives in 3iSoft.** For ER it is `meraj` (separate JSF
   system); for BCI it is the radiology module. Which module holds
   orthopedic clinic appointments/visits? We need page captures (field
   names only) like we did for BCI before writing the real field table.
2. **How 3iSoft tells an orthopedic visit apart** (clinic, department,
   doctor list?).
3. **Phone number.** The Ortho app needs it for follow-up calls and the
   patient-app login (OTP). Put it in the visit list, or a second
   endpoint by MRN like BCI requirement 2 (`/bci-radiology/patients/{mrn}`)?
   A by-MRN endpoint is the more privacy-friendly choice.
4. **Appointment vs arrival.** The Ortho app plans appointments ahead.
   Is "today only" enough, or do we also need upcoming appointments (for
   example the next 7 days) so pre-visit calls can be scheduled?
5. **Body area / reason for visit.** The Ortho app records a `bodyArea`.
   Does 3iSoft hold a referral reason or complaint we could request?
6. **Reuse with BCI.** Could BCI and Orthopedic share one generic
   endpoint (for example `/clinics/{clinic}/visits/today`) instead of one
   endpoint per department? Fewer endpoints for 3iSoft to build, but a
   bigger single ask.
7. **MRN.** Same open item as BCI: is the MRN per person or per visit,
   and is it the Directory API's `patient_id`?
8. **Data access.** The department's request for read access to
   orthopedic patient data (`طلب صلاحية الوصول إلى قاعدة بيانات مرضى قسم
   العظام`, in the Ortho repo) should be approved before real data flows.

## 4. Next steps (when we pick this up)

1. Capture the relevant 3iSoft pages (field names only) → `evidence.md`.
2. Answer section 3 together, then write the final field table.
3. Add it to the v1.3 spec as `x-status: proposed`, then build it in the
   mock with tests and an acceptance check, like requirements 1 and 2.
