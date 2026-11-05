"""Guards for the two v1.2 items dropped in the 4 Nov 2026 meeting, so
neither comes back by accident:

- GET /patients/first-names (family-name-only search): a family name can
  match hundreds of first names, so it is not useful.
- Patient.encounter_type: the source system does not record it.
"""


def test_first_names_endpoint_no_longer_exists(client, auth_headers):
    # With the route gone, "first-names" falls through to /patients/{patient_id}
    # and is treated as an unknown patient id.
    response = client.get(
        "/api/directory/v1/patients/first-names",
        params={"last_name": "Ali"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "PATIENT_NOT_FOUND"


def test_patient_has_no_encounter_type(client, auth_headers):
    response = client.get("/api/directory/v1/patients/10025", headers=auth_headers)
    assert response.status_code == 200
    assert "encounter_type" not in response.json()


def test_openapi_does_not_publish_dropped_items(client):
    spec = client.get("/api/directory/v1/openapi.json").json()
    assert not any(path.endswith("/patients/first-names") for path in spec["paths"])
    patient_props = spec["components"]["schemas"]["Patient"]["properties"]
    assert "encounter_type" not in patient_props
