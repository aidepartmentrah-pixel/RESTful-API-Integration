# 2026-08-25 — Muslim Arabic toolkit run, real server

**Run by:** the project owner, from the machine with real network access.
**Target:** `http://malin:8080/his-general/api/directory/v1` (the real vendor
server — confirmed by the URL in `report.md`/`report.json`, not the mock).
**Tooling:** `Test-HospitalDirectoryAPI-Full.ps1` — a self-contained
PowerShell toolkit built around 20 curated Lebanese Muslim Arabic full names
(علي رحال, محمد الحاج, فاطمة قاسم, etc.), covering patient/doctor/worker
search, auth, pagination, error shapes, and encoding. Lives on Desktop in
`HCAT_Muslim_Arabic_API_Test_Toolkit\`; not yet copied into this repo — ask
if you want it added under `scripts/`.
**Files:** `report.md` / `report.json` — the exact output the toolkit wrote,
pasted back verbatim, unedited.

## What this run added to the confirmed set

Everything below is a direct read of `report.md` — see that file for the
exact request/response behind each line.

- **Patient search needs 3 words, not 2.** All 7 two-word Arabic queries
  (exact, reversed, typo, diacritic, padded, with/without the `ال` article)
  got `422`. The one 3-word query got through and matched 10 records. The
  mock's `patient_service.py` currently enforces a 2-word minimum as a
  deliberate compromise (its `Patient` model has no father-name field) — that
  compromise is now known to not match reality and should be revisited.
- **The exact real rejection message is confirmed verbatim**: *"Please enter
  the patient's full name (first, father and last name), not just part of
  the name"* — word-for-word, not paraphrased.
- **Doctor search genuinely filters server-side** — different single words
  returned different, non-trivial counts (خالد→1, فاطمة→3, علي→10, عائشة→0).
- **Worker search reconfirmed non-functional**: `q='بلال'` and no `q` both
  returned `total=1668` — identical. First suspected on 2026-08-17 (see
  `../2026-08-17_first-real-server-capture/worker-search-diagnosis.md`), now
  independently reconfirmed with a completely different query word.
- **`POST` to any endpoint returns `500 SERVER_ERROR`, not `405
  METHOD_NOT_ALLOWED`.** New finding — the contract requires a clean 405; the
  real server errors out instead. All 4 resource groups tested, all 4 failed
  the same way.
- **`Content-Type` is `application/json` only — missing `; charset=utf-8`.**
  New finding — the written contract requires the charset suffix.
- **The known-real full name `محمد عباس منصور` still returns exactly
  `total=22`** — reproduces the 2026-08-17 finding exactly, on a different
  day, confirming that number is stable, not a fluke.
- **Interesting, not yet fully confirmed:** the 3-word query `محمد حسن رحال`
  (Mohammad Hassan Rahal) matched real records stored as `حسن محمد رحال`
  (Hassan Mohammad Rahal) — same three words, different order. If that
  holds up under a dedicated test (query a name you know is real, in
  scrambled order), it means patient matching past the 3-word gate may not
  require exact word order. One targeted follow-up test would settle it.

## Non-findings (expected, not bugs)

- The exact-lookup-by-ID and byte-round-trip checks against `P-90001` came
  back `404` / empty — expected, since `P-90001` is a mock-only fixture ID
  that doesn't exist on the real server. Not evidence of anything.
- The `sex` field check came back empty for the same reason (404 on a
  mock-only ID) — the real shape of `sex` (a full Arabic word, not `M`/`F`)
  is still established by the 2026-08-17 capture, not this one.
