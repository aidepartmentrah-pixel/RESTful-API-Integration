#!/bin/sh
# Bash/curl port of verify_v1.2_contract.ps1, for Debian/air-gapped hosts
# without PowerShell. Same checks, same two parts (full v1.1 suite, then
# the 5 proposed v1.2 additions reported PASS / FAIL / NOT-YET-IMPLEMENTED),
# same exit-code contract (0 only if $FAIL_COUNT is 0 — NOT-YET-IMPLEMENTED
# never counts as a failure).
#
# NOT YET SMOKE-TESTED on a real Debian/air-gapped host — verify here
# before trusting it there (see the root plan's note on Period F's .sh
# runner, same caveat applies to this script).
#
# Requires: curl, jq.
#
# Usage: sh verify_v1.2_contract.sh [base_url] [api_key] [first_name] [father_name] [last_name]
set -u

BASE_URL="${1:-http://localhost:6001/api/directory/v1}"
API_KEY="${2:-change_me}"
PATIENT_FIRST_NAME="${3:-Danielle}"
PATIENT_FATHER_NAME="${4:-Alexander}"
PATIENT_LAST_NAME="${5:-Hill}"

command -v curl >/dev/null 2>&1 || { echo "ERROR: curl not found on PATH." >&2; exit 2; }
command -v jq   >/dev/null 2>&1 || { echo "ERROR: jq not found on PATH."   >&2; exit 2; }

PASS_COUNT=0
FAIL_COUNT=0
FAILURES=""

BODY_FILE="$(mktemp)"
trap 'rm -f "$BODY_FILE"' EXIT

urlencode() {
    # POSIX-portable percent-encoding via jq (already a hard dependency).
    jq -rn --arg s "$1" '$s|@uri'
}

# Sets $STATUS and writes the response body to $BODY_FILE.
api_get() {
    path="$1"
    with_auth="$2"
    if [ "$with_auth" = "auth" ]; then
        STATUS="$(curl -s -o "$BODY_FILE" -w '%{http_code}' -H "X-API-Key: $API_KEY" "$BASE_URL$path")"
    else
        STATUS="$(curl -s -o "$BODY_FILE" -w '%{http_code}' "$BASE_URL$path")"
    fi
}

# check NAME CONDITION(0/1) [DETAIL]
check() {
    name="$1"; cond="$2"; detail="${3:-}"
    if [ "$cond" -eq 1 ]; then
        printf 'PASS  %s\n' "$name"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        printf 'FAIL  %s  %s\n' "$name" "$detail"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAILURES="$FAILURES\n  - $name  $detail"
    fi
}

# report_feature NAME STATE [DETAIL]
report_feature() {
    name="$1"; state="$2"; detail="${3:-}"
    printf '%-24s %s\n' "$name" "$state"
    [ -n "$detail" ] && printf '  %s\n' "$detail"
    case "$state" in
        PASS) PASS_COUNT=$((PASS_COUNT + 1)) ;;
        FAIL) FAIL_COUNT=$((FAIL_COUNT + 1)); FAILURES="$FAILURES\n  - $name  $detail" ;;
    esac
}

# field_set_matches BODY_JSON "field1 field2 ..." -> echoes 1 or 0
field_set_matches() {
    json="$1"; shift
    expected="$1"
    actual="$(printf '%s' "$json" | jq -r 'keys | sort | join(",")' 2>/dev/null)"
    want="$(printf '%s\n' $expected | sort | tr '\n' ',' | sed 's/,$//')"
    [ "$actual" = "$want" ] && echo 1 || echo 0
}

echo "=== Part 1: full v1.1 suite (must remain a strict superset) ==="
echo "Verifying $BASE_URL against the OpenAPI v1.1 contract"
echo ""

# 1. Health
api_get "/health" noauth
BODY="$(cat "$BODY_FILE")"
check "GET /health -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
SERVICE="$(echo "$BODY" | jq -r '.service // empty')"
check "  service == his-general-directory" $([ "$SERVICE" = "his-general-directory" ] && echo 1 || echo 0) "(got $SERVICE)"
APIVER="$(echo "$BODY" | jq -r '.api_version // empty')"
check "  api_version == 1.0.0" $([ "$APIVER" = "1.0.0" ] && echo 1 || echo 0) "(got $APIVER)"

# 2. Patients, no criteria -> 422 VALIDATION_ERROR
api_get "/patients" auth
BODY="$(cat "$BODY_FILE")"
check "GET /patients (no criteria) -> 422" $([ "$STATUS" = "422" ] && echo 1 || echo 0) "(got $STATUS)"
ERR="$(echo "$BODY" | jq -r '.error // empty')"
check "  error == VALIDATION_ERROR" $([ "$ERR" = "VALIDATION_ERROR" ] && echo 1 || echo 0) "(got $ERR)"

# 3. A lone name field is rejected
FN="$(urlencode "$PATIENT_FIRST_NAME")"
FTN="$(urlencode "$PATIENT_FATHER_NAME")"
LN="$(urlencode "$PATIENT_LAST_NAME")"
api_get "/patients?first_name=$FN" auth
check "GET /patients?first_name=<alone> -> 422" $([ "$STATUS" = "422" ] && echo 1 || echo 0) "(got $STATUS)"

# 3b. first_name + last_name without father_name is still rejected
api_get "/patients?first_name=$FN&last_name=$LN" auth
check "GET /patients?first_name=&last_name= (no father) -> 422" $([ "$STATUS" = "422" ] && echo 1 || echo 0) "(got $STATUS)"

# 4. Full first+father+last trio -> 200
api_get "/patients?first_name=$FN&father_name=$FTN&last_name=$LN&limit=5" auth
BODY="$(cat "$BODY_FILE")"
check "GET /patients?first_name=&father_name=&last_name= -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
ITEMS_COUNT="$(echo "$BODY" | jq -r '.items | length' 2>/dev/null || echo 0)"
check "  at least one result" $([ "$ITEMS_COUNT" -gt 0 ] 2>/dev/null && echo 1 || echo 0) "(0 results - try different name args)"
FIRST_PATIENT="$(echo "$BODY" | jq -c '.items[0] // empty')"
FIRST_PATIENT_ID="$(echo "$FIRST_PATIENT" | jq -r '.patient_id // empty')"
if [ -n "$FIRST_PATIENT_ID" ]; then
    echo "$FIRST_PATIENT_ID" | grep -qv '^P-'
    check "  patient_id has no P- prefix" $([ $? -eq 0 ] && echo 1 || echo 0) "(got $FIRST_PATIENT_ID)"
fi

# 5. Patient exact lookup + 404
if [ -n "$FIRST_PATIENT_ID" ]; then
    api_get "/patients/$FIRST_PATIENT_ID" auth
    check "GET /patients/{id} -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
fi
api_get "/patients/999999999" auth
BODY="$(cat "$BODY_FILE")"
check "GET /patients/{bogus} -> 404" $([ "$STATUS" = "404" ] && echo 1 || echo 0) "(got $STATUS)"
ERR="$(echo "$BODY" | jq -r '.error // empty')"
check "  error == PATIENT_NOT_FOUND" $([ "$ERR" = "PATIENT_NOT_FOUND" ] && echo 1 || echo 0) "(got $ERR)"

# 6. Doctors field set + active_only
api_get "/doctors?limit=5" auth
BODY="$(cat "$BODY_FILE")"
check "GET /doctors -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
DEFAULT_TOTAL="$(echo "$BODY" | jq -r '.total // 0')"
FIRST_DOCTOR="$(echo "$BODY" | jq -c '.items[0] // empty')"
FIRST_DOCTOR_ID="$(echo "$FIRST_DOCTOR" | jq -r '.doctor_id // empty')"
if [ -n "$FIRST_DOCTOR_ID" ]; then
    check "  doctor field set exactly matches contract" "$(field_set_matches "$FIRST_DOCTOR" "doctor_id full_name specialty_id specialty_name department_id department_name is_active")" "(fields: $(echo "$FIRST_DOCTOR" | jq -r 'keys | join(", ")'))"
    echo "$FIRST_DOCTOR_ID" | grep -qv '^D-'
    check "  doctor_id has no D- prefix" $([ $? -eq 0 ] && echo 1 || echo 0) "(got $FIRST_DOCTOR_ID)"
fi
api_get "/doctors?active_only=false&limit=5" auth
BODY="$(cat "$BODY_FILE")"
ACTIVE_FALSE_TOTAL="$(echo "$BODY" | jq -r '.total // 0')"
check "GET /doctors?active_only=false -> total >= default total" $([ "$ACTIVE_FALSE_TOTAL" -ge "$DEFAULT_TOTAL" ] && echo 1 || echo 0) "(active_only=false total=$ACTIVE_FALSE_TOTAL, default total=$DEFAULT_TOTAL)"

if [ -n "$FIRST_DOCTOR_ID" ]; then
    api_get "/doctors/$FIRST_DOCTOR_ID" auth
    check "GET /doctors/{id} -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
fi
api_get "/doctors/999999999" auth
BODY="$(cat "$BODY_FILE")"
check "GET /doctors/{bogus} -> 404" $([ "$STATUS" = "404" ] && echo 1 || echo 0) "(got $STATUS)"
ERR="$(echo "$BODY" | jq -r '.error // empty')"
check "  error == DOCTOR_NOT_FOUND" $([ "$ERR" = "DOCTOR_NOT_FOUND" ] && echo 1 || echo 0) "(got $ERR)"

# 7. Workers: default limit is 10, q is a documented no-op
api_get "/workers" auth
BODY="$(cat "$BODY_FILE")"
check "GET /workers -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
WORKER_LIMIT="$(echo "$BODY" | jq -r '.limit // 0')"
check "  default limit is 10, not 100" $([ "$WORKER_LIMIT" = "10" ] && echo 1 || echo 0) "(got $WORKER_LIMIT)"
WORKER_TOTAL_NO_Q="$(echo "$BODY" | jq -r '.total // 0')"
FIRST_WORKER="$(echo "$BODY" | jq -c '.items[0] // empty')"
FIRST_WORKER_ID="$(echo "$FIRST_WORKER" | jq -r '.employee_id // empty')"
if [ -n "$FIRST_WORKER_ID" ]; then
    echo "$FIRST_WORKER_ID" | grep -qv '^E-'
    check "  employee_id has no E- prefix" $([ $? -eq 0 ] && echo 1 || echo 0) "(got $FIRST_WORKER_ID)"
fi
api_get "/workers?q=ThisShouldNotFilterAnything&limit=10" auth
BODY="$(cat "$BODY_FILE")"
WORKER_TOTAL_WITH_Q="$(echo "$BODY" | jq -r '.total // 0')"
check "  q has no effect on /workers (matches contract + confirmed real behavior)" $([ "$WORKER_TOTAL_WITH_Q" = "$WORKER_TOTAL_NO_Q" ] && echo 1 || echo 0) "(no-q total=$WORKER_TOTAL_NO_Q, with-q total=$WORKER_TOTAL_WITH_Q)"

if [ -n "$FIRST_WORKER_ID" ]; then
    api_get "/workers/$FIRST_WORKER_ID" auth
    BODY="$(cat "$BODY_FILE")"
    check "GET /workers/{id} -> 200" $([ "$STATUS" = "200" ] && echo 1 || echo 0) "(got $STATUS)"
    IS_ACTIVE="$(echo "$BODY" | jq -r '.is_active')"
    check "  is_active is true on exact lookup" $([ "$IS_ACTIVE" = "true" ] && echo 1 || echo 0) "(got $IS_ACTIVE)"
fi
api_get "/workers/999999999" auth
BODY="$(cat "$BODY_FILE")"
check "GET /workers/{bogus} -> 404" $([ "$STATUS" = "404" ] && echo 1 || echo 0) "(got $STATUS)"
ERR="$(echo "$BODY" | jq -r '.error // empty')"
check "  error == WORKER_NOT_FOUND" $([ "$ERR" = "WORKER_NOT_FOUND" ] && echo 1 || echo 0) "(got $ERR)"

# 8. Auth
api_get "/doctors?limit=1" noauth
BODY="$(cat "$BODY_FILE")"
check "GET /doctors with no key -> 401" $([ "$STATUS" = "401" ] && echo 1 || echo 0) "(got $STATUS)"
ERR="$(echo "$BODY" | jq -r '.error // empty')"
check "  error == UNAUTHORIZED" $([ "$ERR" = "UNAUTHORIZED" ] && echo 1 || echo 0) "(got $ERR)"

echo ""
echo "=== Part 2: the 5 proposed v1.2 additions ==="
echo ""

# --- 1. father-names (implemented) ---
api_get "/patients/father-names?first_name=$FN&last_name=$LN" auth
BODY="$(cat "$BODY_FILE")"
if [ "$STATUS" = "404" ]; then
    report_feature "father-names" "NOT-YET-IMPLEMENTED"
elif [ "$STATUS" = "200" ] && [ "$(field_set_matches "$BODY" "success first_name last_name candidates total_candidates")" = "1" ]; then
    TOTAL_CAND="$(echo "$BODY" | jq -r '.total_candidates')"
    report_feature "father-names" "PASS" "candidates=$TOTAL_CAND"
else
    report_feature "father-names" "FAIL" "(status=$STATUS)"
fi

# --- 2. first-names (proposed) ---
api_get "/patients/first-names?last_name=$LN" auth
BODY="$(cat "$BODY_FILE")"
if [ "$STATUS" = "404" ]; then
    report_feature "first-names" "NOT-YET-IMPLEMENTED"
elif [ "$STATUS" = "200" ] && [ "$(field_set_matches "$BODY" "success last_name candidates total_candidates")" = "1" ]; then
    TOTAL_CAND="$(echo "$BODY" | jq -r '.total_candidates')"
    report_feature "first-names" "PASS" "candidates=$TOTAL_CAND"
else
    report_feature "first-names" "FAIL" "(status=$STATUS)"
fi

# --- 3. worker section_name / administration_name (proposed) ---
if [ -n "$FIRST_WORKER" ] && [ "$FIRST_WORKER" != "null" ]; then
    HAS_SECTION_NAME="$(echo "$FIRST_WORKER" | jq 'has("section_name")')"
    if [ "$HAS_SECTION_NAME" = "false" ]; then
        report_feature "worker-section-admin" "NOT-YET-IMPLEMENTED"
    elif [ "$(field_set_matches "$FIRST_WORKER" "employee_id full_name job_id job_title department_id department_name section_id section_name administration_id administration_name is_manager is_active")" = "1" ]; then
        report_feature "worker-section-admin" "PASS"
    else
        report_feature "worker-section-admin" "FAIL" "(fields: $(echo "$FIRST_WORKER" | jq -r 'keys | join(", ")'))"
    fi
else
    report_feature "worker-section-admin" "FAIL" "(no worker in seed data)"
fi

# --- 4. patient encounter_type (proposed) ---
if [ -n "$FIRST_PATIENT" ] && [ "$FIRST_PATIENT" != "null" ]; then
    HAS_ENCOUNTER_TYPE="$(echo "$FIRST_PATIENT" | jq 'has("encounter_type")')"
    if [ "$HAS_ENCOUNTER_TYPE" = "false" ]; then
        report_feature "patient-encounter-type" "NOT-YET-IMPLEMENTED"
    elif [ "$(field_set_matches "$FIRST_PATIENT" "patient_id full_name first_name last_name birth_date age sex encounter_type")" = "1" ]; then
        ENC_TYPE="$(echo "$FIRST_PATIENT" | jq -r '.encounter_type')"
        report_feature "patient-encounter-type" "PASS" "encounter_type=$ENC_TYPE"
    else
        report_feature "patient-encounter-type" "FAIL" "(fields: $(echo "$FIRST_PATIENT" | jq -r 'keys | join(", ")'))"
    fi
else
    report_feature "patient-encounter-type" "FAIL" "(no patient in seed data)"
fi

# --- 5. GET /er/current-visits (proposed) ---
api_get "/er/current-visits" auth
BODY="$(cat "$BODY_FILE")"
if [ "$STATUS" = "404" ]; then
    report_feature "er-current-visits" "NOT-YET-IMPLEMENTED"
elif [ "$STATUS" = "200" ] && [ "$(field_set_matches "$BODY" "success items total")" = "1" ]; then
    ER_TOTAL="$(echo "$BODY" | jq -r '.total')"
    report_feature "er-current-visits" "PASS" "total=$ER_TOTAL"
else
    report_feature "er-current-visits" "FAIL" "(status=$STATUS)"
fi

echo ""
echo "============================================================"
echo "RESULT: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "============================================================"

if [ "$FAIL_COUNT" -gt 0 ]; then
    echo ""
    echo "Failures:"
    printf '%b\n' "$FAILURES"
    exit 1
else
    echo "0 real failures (NOT-YET-IMPLEMENTED lines above are informational, not failures)."
    exit 0
fi
