from app.models import Patient


def test_first_name_candidates_groups_and_counts(client, db_session, auth_headers):
    db_session.add_all([
        Patient(patient_id="70101", first_name_ar="Common", father_name_ar="Any", last_name_ar="Shared", sex="Male"),
        Patient(patient_id="70102", first_name_ar="Common", father_name_ar="Any", last_name_ar="Shared", sex="Male"),
        Patient(patient_id="70103", first_name_ar="Rare", father_name_ar="Any", last_name_ar="Shared", sex="Male"),
    ])
    db_session.commit()

    response = client.get(
        "/api/directory/v1/patients/first-names",
        params={"last_name": "Shared"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_candidates"] == 2
    by_name = {c["first_name"]: c["patient_count"] for c in body["candidates"]}
    assert by_name["Common"] == 2
    assert by_name["Rare"] == 1
    # ordered by patient_count descending, most common first
    assert body["candidates"][0]["first_name"] == "Common"


def test_first_name_candidates_requires_last_name(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients/first-names",
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_first_name_candidates_no_match_is_empty_200(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients/first-names",
        params={"last_name": "NoSuchFamilyAtAll"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_candidates"] == 0
    assert body["candidates"] == []


def test_first_name_candidates_excludes_patients_without_first_name(client, db_session, auth_headers):
    db_session.add(
        Patient(patient_id="70104", first_name_ar=None, father_name_ar="Any", last_name_ar="NoFirst", sex="Male")
    )
    db_session.commit()

    response = client.get(
        "/api/directory/v1/patients/first-names",
        params={"last_name": "NoFirst"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["total_candidates"] == 0


def test_first_names_route_does_not_shadow_patient_id_lookup(client, auth_headers):
    # Regression check: /patients/first-names is registered before
    # /patients/{patient_id} -- confirms the literal route wins and an
    # actual numeric patient_id lookup still works normally.
    response = client.get("/api/directory/v1/patients/10025", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["patient_id"] == "10025"
