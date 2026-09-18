from app.models import Patient


def test_father_name_candidates_groups_and_counts(client, db_session, auth_headers):
    db_session.add_all([
        Patient(patient_id="70001", first_name_ar="Zaid", father_name_ar="Common", last_name_ar="Shared", sex="Male"),
        Patient(patient_id="70002", first_name_ar="Zaid", father_name_ar="Common", last_name_ar="Shared", sex="Male"),
        Patient(patient_id="70003", first_name_ar="Zaid", father_name_ar="Rare", last_name_ar="Shared", sex="Male"),
    ])
    db_session.commit()

    response = client.get(
        "/api/directory/v1/patients/father-names",
        params={"first_name": "Zaid", "last_name": "Shared"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_candidates"] == 2
    by_name = {c["father_name"]: c["patient_count"] for c in body["candidates"]}
    assert by_name["Common"] == 2
    assert by_name["Rare"] == 1
    # ordered by patient_count descending, most common first
    assert body["candidates"][0]["father_name"] == "Common"


def test_father_name_candidates_requires_both_names(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients/father-names",
        params={"first_name": "Zaid"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_father_name_candidates_no_match_is_empty_200(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients/father-names",
        params={"first_name": "NoSuch", "last_name": "PersonAtAll"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_candidates"] == 0
    assert body["candidates"] == []


def test_father_name_candidates_excludes_patients_without_father_name(client, db_session, auth_headers):
    db_session.add(
        Patient(patient_id="70004", first_name_ar="Compound", father_name_ar=None, last_name_ar="NoFather", sex="Male")
    )
    db_session.commit()

    response = client.get(
        "/api/directory/v1/patients/father-names",
        params={"first_name": "Compound", "last_name": "NoFather"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["total_candidates"] == 0


def test_father_names_route_does_not_shadow_patient_id_lookup(client, auth_headers):
    # Regression check: /patients/father-names is registered before
    # /patients/{patient_id} -- confirms the literal route wins and an
    # actual numeric patient_id lookup still works normally.
    response = client.get("/api/directory/v1/patients/10025", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["patient_id"] == "10025"
