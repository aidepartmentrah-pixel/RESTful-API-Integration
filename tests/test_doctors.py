def test_doctor_list_defaults_to_active_only(client, auth_headers):
    response = client.get("/api/directory/v1/doctors", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    doctor_ids = [item["doctor_id"] for item in body["items"]]
    assert "1025" in doctor_ids
    assert "9999" not in doctor_ids


def test_doctor_list_can_include_inactive(client, auth_headers):
    response = client.get(
        "/api/directory/v1/doctors", params={"active_only": "false"}, headers=auth_headers
    )
    assert response.status_code == 200
    doctor_ids = [item["doctor_id"] for item in response.json()["items"]]
    assert "9999" in doctor_ids


def test_doctor_search_matches_father_name(client, auth_headers):
    # OpenAPI v1.1: q OR-matches full name/first/father/last/assistant
    # number/id-as-text.
    response = client.get(
        "/api/directory/v1/doctors", params={"q": "Mohammed"}, headers=auth_headers
    )
    assert response.status_code == 200
    doctor_ids = [item["doctor_id"] for item in response.json()["items"]]
    assert "1025" in doctor_ids


def test_exact_doctor_lookup(client, auth_headers):
    response = client.get("/api/directory/v1/doctors/1025", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Dr. Ahmad Mohammed"


def test_exact_doctor_not_found(client, auth_headers):
    response = client.get("/api/directory/v1/doctors/999999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"] == "DOCTOR_NOT_FOUND"
