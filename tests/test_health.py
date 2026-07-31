def test_health_ok(client):
    response = client.get("/api/directory/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_requires_no_api_key(client):
    response = client.get("/api/directory/v1/health")
    assert response.status_code != 401
