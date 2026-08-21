def test_patient_search_requires_criterion(client, auth_headers):
    response = client.get("/api/directory/v1/patients", headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_patient_search_by_q(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients", params={"q": "Ahmad Ali"}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["total"] == 1
    assert body["items"][0]["patient_id"] == "P-10025"


def test_patient_search_no_results(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients", params={"q": "NoSuch Patient"}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


def test_patient_search_single_word_rejected(client, auth_headers):
    # Confirmed real-API behavior: a partial (single-word) name search is
    # rejected, not silently matched. See patient_service.search_patients.
    response = client.get(
        "/api/directory/v1/patients", params={"q": "Ahmad"}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_exact_patient_found(client, auth_headers):
    response = client.get("/api/directory/v1/patients/P-10025", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == "P-10025"
    assert body["full_name"] == "Ahmad Ali"
    assert "visit_id" not in body
    assert "arrival_time" not in body


def test_exact_patient_not_found(client, auth_headers):
    response = client.get("/api/directory/v1/patients/P-99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"] == "PATIENT_NOT_FOUND"


def test_pagination_bounds_rejected(client, auth_headers):
    response = client.get(
        "/api/directory/v1/patients",
        params={"q": "a", "limit": 501},
        headers=auth_headers,
    )
    assert response.status_code == 422
