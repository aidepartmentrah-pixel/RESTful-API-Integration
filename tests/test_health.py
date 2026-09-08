def test_health_ok(client):
    response = client.get("/api/directory/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "his-general-directory"
    assert body["api_version"] == "1.0.0"
    assert "timestamp" in body


def test_health_requires_no_api_key(client):
    response = client.get("/api/directory/v1/health")
    assert response.status_code != 401
