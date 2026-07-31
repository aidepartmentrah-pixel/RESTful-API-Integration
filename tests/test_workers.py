def test_worker_list(client, auth_headers):
    response = client.get("/api/directory/v1/workers", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["employee_id"] == "E-5541"


def test_exact_worker_lookup(client, auth_headers):
    response = client.get("/api/directory/v1/workers/E-5541", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Hassan Ibrahim"


def test_exact_worker_not_found(client, auth_headers):
    response = client.get("/api/directory/v1/workers/E-0000", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"] == "WORKER_NOT_FOUND"


def test_method_not_allowed(client, auth_headers):
    response = client.post("/api/directory/v1/workers", headers=auth_headers)
    assert response.status_code == 405
