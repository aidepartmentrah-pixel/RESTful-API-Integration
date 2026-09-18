from app.models import Patient


def test_patient_lookup_includes_encounter_type(client, db_session, auth_headers):
    db_session.add(
        Patient(
            patient_id="70301",
            first_name_ar="Encounter",
            father_name_ar="Type",
            last_name_ar="Test",
            sex="Male",
            encounter_type="inpatient",
        )
    )
    db_session.commit()

    response = client.get("/api/directory/v1/patients/70301", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["encounter_type"] == "inpatient"


def test_patient_search_includes_encounter_type(client, db_session, auth_headers):
    db_session.add(
        Patient(
            patient_id="70302",
            first_name_ar="Outpt",
            father_name_ar="Search",
            last_name_ar="Case",
            sex="Female",
            encounter_type="outpatient",
        )
    )
    db_session.commit()

    response = client.get(
        "/api/directory/v1/patients",
        params={"first_name": "Outpt", "father_name": "Search", "last_name": "Case"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["encounter_type"] == "outpatient"


def test_patient_encounter_type_defaults_to_null(client, auth_headers):
    # patient_id 10025 is seeded in conftest.py without encounter_type set --
    # confirms the new column is nullable and doesn't break an existing
    # record that predates this addition.
    response = client.get("/api/directory/v1/patients/10025", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["encounter_type"] is None
