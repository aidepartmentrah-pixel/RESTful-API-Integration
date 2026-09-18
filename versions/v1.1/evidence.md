# Evidence behind v1.1

Citations only — see the referenced files for the actual request/response
detail, not reproduced here to avoid a second copy that can drift from the
primary source.

| Fact | Confidence | Source |
|---|---|---|
| Patient search requires `patient_id`, or all three of `first_name`+`father_name`+`last_name` together — no partial name search | Vendor's own written contract | `vendor-deliverable/Hospital_Directory_API_OpenAPI_v1.1.yaml` |
| Real patient/doctor/worker IDs are dotted-numeric (e.g. `5690.47148`), not the `P-`/`D-`/`E-` prefix this mock used to generate | **CONFIRMED_REAL** — direct HTTP capture | `real-evidence/2026-08-17_first-real-server-capture/raw-http-capture.txt` |
| Real Arabic text is mojibake-corrupted in transport (UTF-8 read as Latin-1) — a real production bug, deliberately *not* reproduced in this mock | **CONFIRMED_REAL**, reconfirmed twice | Same file, reconfirmed in `2026-08-25_muslim-arabic-toolkit-run/report.md` |
| `sex` is a resolved display string, not a fixed 1-char code | **CONFIRMED_REAL** | `real-evidence/2026-08-17_first-real-server-capture/raw-http-capture.txt` |
| Real scale is far larger than this mock's seed data (~321 doctors, ~1667 workers vs. ~50/100 here) | **CONFIRMED_REAL** | Same file |
| `/workers` `q` parameter is silently ignored by the real server — this mock deliberately does not offer it, matching that finding | **CONFIRMED_REAL**, reconfirmed | `real-evidence/README.md` "Known mock/real divergences", reconfirmed in the 08-25 toolkit run |
| `/health` returns extra fields (`service`, `api_version`, `timestamp`) beyond bare `status` | **CONFIRMED_REAL** | Both real-evidence capture folders |

**Caveat worth repeating from the gap-analysis**: the 2026-08-25 toolkit
run's own `report.json` tags most of its rows `MOCK_ONLY`/`SPEC_UNVERIFIED`,
not `CONFIRMED_REAL` — only 2 of 49 checks in that run are genuinely
confirmed-real. Where this table cites that run, treat it as corroborating,
not primary, evidence — the 2026-08-17 raw capture is the higher-confidence
source throughout.

**Not covered by real evidence, still open**: the structured
`first_name`/`father_name`/`last_name` search shape has never actually been
tested against the real server — every real-server observation used a
single joined `q` string. This remains the single highest-value next
real-server test, unchanged from when it was first flagged.
