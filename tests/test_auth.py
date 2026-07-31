def test_missing_api_key_returns_401(client):
    response = client.get("/api/directory/v1/doctors")
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_invalid_api_key_returns_401(client):
    response = client.get(
        "/api/directory/v1/doctors", headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401


def test_valid_api_key_succeeds(client, auth_headers):
    response = client.get("/api/directory/v1/doctors", headers=auth_headers)
    assert response.status_code == 200
