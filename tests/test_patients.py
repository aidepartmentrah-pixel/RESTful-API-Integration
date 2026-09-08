def test_patient_search_requires_criterion(client, auth_headers):
    response = client.get("/api/directory/v1/patients", headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_patient_search_by_full_name_trio(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients",
        params={"first_name": "Ahmad", "father_name": "Mohammed", "last_name": "Ali"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total"] == 1
    assert body["items"][0]["patient_id"] == "10025"


def test_patient_search_no_results(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients",
        params={"first_name": "NoSuch", "father_name": "Patient", "last_name": "Here"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_patient_search_single_name_field_rejected(client, auth_headers):
    # OpenAPI v1.1: a lone name field is rejected, not silently matched.
    response = client.get(
        "/api/directory/v1/patients", params={"first_name": "Ahmad"}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_patient_search_first_and_last_without_father_rejected(client, auth_headers):
    # OpenAPI v1.1: first+last without father_name is still rejected -- all
    # three are required together.
    response = client.get(
        "/api/directory/v1/patients",
        params={"first_name": "Ahmad", "last_name": "Ali"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_exact_patient_found(client, auth_headers):
    response = client.get("/api/directory/v1/patients/10025", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "10025"
    assert body["full_name"] == "Ahmad Mohammed Ali"
    assert "visit_id" not in body
    assert "arrival_time" not in body
    assert "father_name" not in body


def test_exact_patient_not_found(client, auth_headers):
    response = client.get("/api/directory/v1/patients/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"] == "PATIENT_NOT_FOUND"


def test_pagination_bounds_rejected(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients",
        params={"first_name": "A", "father_name": "B", "last_name": "C", "limit": 501},
        headers=auth_headers,
    )
    assert response.status_code == 422
