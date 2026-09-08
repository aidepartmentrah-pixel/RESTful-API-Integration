# Hospital Directory API - Muslim Arabic Name Characterization Report

Target: `http://malin:8080/his-general/api/directory/v1`  
Run at: 2026-08-25_13-34-28  
PASS: 21   FAIL: 5   OBSERVED: 23   Total: 49

**Tags**: `CONFIRMED_REAL` = matches an already-confirmed real-vendor fact. `MOCK_ONLY` = this mock's own behavior, no claim about the real vendor. `SPEC_UNVERIFIED` = the written contract requires this but it isn't vendor-confirmed. `OPEN_QUESTION` = the contract itself says this is unresolved. `KNOWN_REAL_BUG` = already confirmed present on the real server in earlier testing, included so it isn't mistaken for a new finding.

## Failures

- **[SPEC_UNVERIFIED] errors :: POST /patients -> 405 METHOD_NOT_ALLOWED** -- status=500 error=SERVER_ERROR
- **[SPEC_UNVERIFIED] errors :: POST /doctors -> 405 METHOD_NOT_ALLOWED** -- status=500 error=SERVER_ERROR
- **[SPEC_UNVERIFIED] errors :: POST /workers -> 405 METHOD_NOT_ALLOWED** -- status=500 error=SERVER_ERROR
- **[SPEC_UNVERIFIED] errors :: POST /health -> 405 METHOD_NOT_ALLOWED** -- status=500 error=SERVER_ERROR
- **[SPEC_UNVERIFIED] encoding :: Content-Type is application/json; charset=utf-8** -- Content-Type='application/json'

## health

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| PASS | SPEC_UNVERIFIED | GET /health -> 200, no auth | 200 | status=healthy fields=status,service,api_version,timestamp |

## auth

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| PASS | MOCK_ONLY | No API key -> 401 | 401 | error=UNAUTHORIZED |
| OBSERVED | MOCK_ONLY | Missing-key vs wrong-key message identical |  | no-key message='Missing or invalid API key' |
| PASS | MOCK_ONLY | Wrong API key -> 401, same message as missing key | 401 | wrong-key message='Missing or invalid API key' |
| PASS | MOCK_ONLY | Correct API key -> not 401 | 200 | status=200 |

## patient_search

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| PASS | CONFIRMED_REAL | No criteria -> 422 VALIDATION_ERROR | 422 | error=VALIDATION_ERROR message=At least one of 'q' or 'patient_id' is required |
| PASS | CONFIRMED_REAL | Single Arabic word 'Ø¹ÙÙ' -> 422 VALIDATION_ERROR | 422 | error=VALIDATION_ERROR message=Please enter the patient's full name (first, father and last name), not just part of the name -- real vendor message is confirmed to read '...full name (first, father and last name)...'; compare wording here |
| OBSERVED | MOCK_ONLY | Exact lookup by known patient_id | 404 | full_name='' sex='' fields=error,message |
| PASS | SPEC_UNVERIFIED | Unknown patient_id -> 404 PATIENT_NOT_FOUND | 404 | error=PATIENT_NOT_FOUND |
| OBSERVED | KNOWN_REAL_BUG | Known-real full name smoke test ('ÙØ­ÙØ¯ Ø¹Ø¨Ø§Ø³ ÙÙØµÙØ±') |  | HTTP 200, total=22 -- confirmed to match 22 real patients in an earlier real-server run; 0 results here means either the mock (expected, no such fixture) or a real-server regression |

## patient_search.matrix

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| OBSERVED | MOCK_ONLY | Exact full name match | 422 | HTTP 422, 0 result(s) for 'Ø¹ÙÙ Ø±Ø­Ø§Ù' |
| OBSERVED | MOCK_ONLY | Reversed word order | 422 | HTTP 422, 0 result(s) for 'Ø±Ø­Ø§Ù Ø¹ÙÙ' |
| OBSERVED | MOCK_ONLY | One-letter typo (Rahal -> Rajal) | 422 | HTTP 422, 0 result(s) for 'Ø¹ÙÙ Ø±Ø¬Ø§Ù' |
| OBSERVED | MOCK_ONLY | Shadda-diacritic variant vs plain spelling | 422 | HTTP 422, 0 result(s) for 'Ø¹ÙÙÙ Ø±Ø­Ø§Ù' |
| OBSERVED | MOCK_ONLY | Padded with extra internal whitespace | 422 | HTTP 422, 0 result(s) for 'Ø¹ÙÙ  Ø±Ø­Ø§Ù' |
| OBSERVED | MOCK_ONLY | Definite-article (Al-) name, exact | 422 | HTTP 422, 0 result(s) for 'ÙØ­ÙØ¯ Ø§ÙØ­Ø§Ø¬' |
| OBSERVED | MOCK_ONLY | Definite-article name, article stripped | 422 | HTTP 422, 0 result(s) for 'ÙØ­ÙØ¯ Ø­Ø§Ø¬' |
| OBSERVED | SPEC_UNVERIFIED | 3-word first+father+last pattern | 200 | HTTP 200, 10 result(s) for 'ÙØ­ÙØ¯ Ø­Ø³Ù Ø±Ø­Ø§Ù' -> Ø­Ø³Ù ÙØ­ÙØ¯ Ø±Ø­Ø§Ù \| Ø­Ø³Ù ÙØ­ÙØ¯ Ø±Ø­Ø§Ù \| Ø­Ø³Ù ÙØ­ÙØ¯ Ø±Ø­Ø§Ù |
| OBSERVED | SPEC_UNVERIFIED | 3-word kunya-compound given name | 200 | HTTP 200, 0 result(s) for 'Ø£Ø¨Ù Ø¨ÙØ± Ø®ÙÙÙ' |
| OBSERVED | SPEC_UNVERIFIED | 3-word theophoric compound given name | 200 | HTTP 200, 1 result(s) for 'Ø¹Ø¨Ø¯ Ø§ÙØ±Ø­ÙÙ Ø§ÙÙÙÙÙ' -> Ø¹Ø¨Ø¯Ø§ÙØ±Ø­ÙÙ Ø§ÙØ´ÙØ® Ø¹ÙÙ Ø§ÙÙÙÙÙ |
| OBSERVED | SPEC_UNVERIFIED | Duplicate full_name pair both returned, not deduped | 422 | 0 result(s) for 'Ø¹ÙÙ Ø­Ø±Ø¨' -- contract requires every match returned, never merged |

## doctor_search

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| PASS | MOCK_ONLY | List doctors, default (active_only=true) | 200 | total=322 |
| PASS | MOCK_ONLY | Partial (single word) Arabic search for doctor 'Ø¹ÙÙ Ø±Ø­Ø§Ù' | 200 | q='Ø¹ÙÙ' -> 10 result(s) (doctors/workers are documented to accept partial q, unlike patients) |
| PASS | MOCK_ONLY | Partial (single word) Arabic search for doctor 'Ø­Ø³Ù Ø²Ø¹ÙØªØ±' | 200 | q='Ø­Ø³Ù' -> 10 result(s) (doctors/workers are documented to accept partial q, unlike patients) |
| PASS | MOCK_ONLY | Partial (single word) Arabic search for doctor 'ÙØ§Ø·ÙØ© ÙØ§Ø³Ù' | 200 | q='ÙØ§Ø·ÙØ©' -> 3 result(s) (doctors/workers are documented to accept partial q, unlike patients) |
| PASS | MOCK_ONLY | Partial (single word) Arabic search for doctor 'Ø®Ø§ÙØ¯ Ø¹ÙØªØ§ÙÙ' | 200 | q='Ø®Ø§ÙØ¯' -> 1 result(s) (doctors/workers are documented to accept partial q, unlike patients) |
| OBSERVED | MOCK_ONLY | Partial (single word) Arabic search for doctor 'Ø¹Ø§Ø¦Ø´Ø© Ø§ÙÙÙØ³ÙÙ' | 200 | q='Ø¹Ø§Ø¦Ø´Ø©' -> 0 result(s) (doctors/workers are documented to accept partial q, unlike patients) |
| PASS | SPEC_UNVERIFIED | Unknown doctor_id -> 404 DOCTOR_NOT_FOUND | 404 | error=DOCTOR_NOT_FOUND |

## worker_search

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| OBSERVED | KNOWN_REAL_BUG | Does worker q= actually filter? (q vs no-q total comparison) |  | q='Ø¨ÙØ§Ù' total=1668; no-q total=1668; SAME=True -- CONFIRMED on the real server that q is silently ignored (identical totals); the mock currently DOES filter on q, which is itself a mock/real divergence worth closing |
| OBSERVED | MOCK_ONLY | Partial Arabic search for worker 'Ø¨ÙØ§Ù ÙÙÙÙ' | 200 | q='Ø¨ÙØ§Ù' -> 10 result(s) |
| OBSERVED | MOCK_ONLY | Partial Arabic search for worker 'Ø±ÙØ§ Ø­ÙØ§Ø¯Ø©' | 200 | q='Ø±ÙØ§' -> 10 result(s) |
| OBSERVED | MOCK_ONLY | Partial Arabic search for worker 'ÙØµØ·ÙÙ Ø¨ÙØ¶ÙÙ' | 200 | q='ÙØµØ·ÙÙ' -> 10 result(s) |
| OBSERVED | MOCK_ONLY | Partial Arabic search for worker 'Ø³ÙØ§Ø¡ Ø¹Ø³ÙØ±Ø§Ù' | 200 | q='Ø³ÙØ§Ø¡' -> 10 result(s) |
| OBSERVED | MOCK_ONLY | Partial Arabic search for worker 'ÙÙØ± Ø¬Ø§Ø¨Ø±' | 200 | q='ÙÙØ±' -> 10 result(s) |
| PASS | SPEC_UNVERIFIED | Unknown employee_id -> 404 WORKER_NOT_FOUND | 404 | error=WORKER_NOT_FOUND |

## pagination

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| PASS | SPEC_UNVERIFIED | limit=0 | 422 | expected 422=True, got status=422 |
| PASS | SPEC_UNVERIFIED | limit=1 | 200 | expected 422=False, got status=200 |
| PASS | SPEC_UNVERIFIED | limit=500 | 200 | expected 422=False, got status=200 |
| PASS | SPEC_UNVERIFIED | limit=501 | 422 | expected 422=True, got status=422 |
| PASS | SPEC_UNVERIFIED | limit=9999 | 422 | expected 422=True, got status=422 |
| PASS | SPEC_UNVERIFIED | offset=-1 | 422 | status=422 |
| PASS | SPEC_UNVERIFIED | offset=0 | 200 | status=200 |

## errors

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| FAIL | SPEC_UNVERIFIED | POST /patients -> 405 METHOD_NOT_ALLOWED | 500 | status=500 error=SERVER_ERROR |
| FAIL | SPEC_UNVERIFIED | POST /doctors -> 405 METHOD_NOT_ALLOWED | 500 | status=500 error=SERVER_ERROR |
| FAIL | SPEC_UNVERIFIED | POST /workers -> 405 METHOD_NOT_ALLOWED | 500 | status=500 error=SERVER_ERROR |
| FAIL | SPEC_UNVERIFIED | POST /health -> 405 METHOD_NOT_ALLOWED | 500 | status=500 error=SERVER_ERROR |

## encoding

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| FAIL | SPEC_UNVERIFIED | Content-Type is application/json; charset=utf-8 |  | Content-Type='application/json' |
| OBSERVED | MOCK_ONLY | Byte-exact round-trip of stored Arabic full_name |  | expected='Ø¹ÙÙ Ø±Ø­Ø§Ù' actual='' exact-match=False |

## sex_values

| Verdict | Tag | Title | Status | Finding |
|---|---|---|---|---|
| OBSERVED | OPEN_QUESTION | Shape of the 'sex' field on a known record |  | sex='' (length 0) -- CONFIRMED real-server data uses a full Arabic word (e.g. the word for 'male'), not a 1-char M/F code; the mock's Patient.sex column is String(1), which cannot even store that shape |
