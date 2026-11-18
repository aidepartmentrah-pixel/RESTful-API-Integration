HOSPITAL DIRECTORY API v1.2 - OFFLINE TEST
==========================================

Tests the v1.2 API exactly as 3iSoft delivered it (their document
"HIS API - v1.2 Additions", 18 Nov 2026), from a Windows PC on the
hospital network. No internet and no installation needed.


HOW TO RUN
----------
1. Copy this whole folder to the offline PC.
2. Open settings.txt in Notepad and fill in:
     BaseUrl / ApiKey       the Directory API address and its key
     ErBaseUrl / ErApiKey   the ER API address and its key (SEPARATE key)
     PatientFirstName / PatientFatherName / PatientLastName
                            a patient who really exists on the server
   Save the file. The test refuses to start while a key is not filled in.
3. Double-click RUN-TEST.bat.
4. Bring back the file saved in the "results" folder (one per run).


WHAT IT CHECKS (about 80 checks)
--------------------------------
Part 1   v1.1 still works: patient search rules, patient / doctor /
         worker lookups, 404s, and 401 without a key.

Part 2A  GET /patients/father-names
         fields, sorting (most records first, ties alphabetical),
         total_candidates vs limit, the two exact error messages,
         no-match answer, Arabic not garbled, 401 without a key.

Part 2B  GET /hr-workers and /hr-workers/{id}
         the 12 fields, default paging, offset, 404, the 422 limits,
         filters by administration / section / department: each one
         includes the units below it, ignores extra spaces and spelling
         differences (alef forms, ta marbuta, alef maqsura), AND-combines,
         unknown name = empty list, empty filter ignored. The unit names
         are taken from the server's own data - nothing to type.

Part 2C  GET /current-visits on the ER API (own address, own key;
         the real ER API is on meraj, not malin)
         the 8 fields always present, total = number of items,
         ISO 8601 time with offset, age, sorting (earliest first, equal
         times by visit id), unique visit ids, Arabic not garbled,
         UTF-8 content type, 401 without a key, and the Directory key
         is refused (keys are separate).


READING THE RESULT
------------------
"RESULT: N passed, M failed, K info" at the end.
  PASS / FAIL   counted; any FAIL is listed again at the end.
  INFO          worth knowing, never a failure (for example the
                api_version, how many patients are in the ER now,
                a gender value that is a raw code).

Things to expect:
  - "the patient in settings.txt is found" fails if that patient does
    not exist: use a real patient's exact names.
  - If the ER list is empty when you run it, the ER field checks are
    skipped (INFO). Run again when patients are in the ER.
  - The black window may show Arabic as boxes. The file in "results"
    shows it correctly.


FILES
-----
RUN-TEST.bat                    double-click to run (uses settings.txt)
settings.txt                    the real servers: the only file to edit
settings.local-mock.txt         our v1.2-dev mock on port 6001
run.ps1                         reads a settings file, saves the results file
verify_v1.2_delivered.ps1       the test itself
results\                        one log file per run (not kept in git)

This folder lives in the RESTful-API-Integration repo under
versions/v1.2/offline_test_kit/. Copy the whole folder to the offline PC.
To test the mock instead:  powershell -File run.ps1 -SettingsFile settings.local-mock.txt
