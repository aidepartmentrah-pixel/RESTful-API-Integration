def test_worker_list(client, auth_headers):
    response = client.get("/api/directory/v1/workers", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["employee_id"] == "5541"


def test_worker_list_excludes_inactive(client, auth_headers):
    response = client.get("/api/directory/v1/workers", headers=auth_headers)
    employee_ids = [item["employee_id"] for item in response.json()["items"]]
    assert "5542" not in employee_ids


def test_worker_list_ignores_q(client, auth_headers):
    # OpenAPI v1.1 dropped `q` from /workers entirely -- confirmed the real
    # server silently ignores it, so the mock no longer offers it either.
    response = client.get(
        "/api/directory/v1/workers", params={"q": "DoesNotMatchAnything"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_worker_list_default_limit_is_ten(client, auth_headers):
    response = client.get("/api/directory/v1/workers", headers=auth_headers)
    assert response.json()["limit"] == 10


def test_exact_worker_lookup(client, auth_headers):
    response = client.get("/api/directory/v1/workers/5541", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Hassan Ibrahim"


def test_inactive_worker_lookup_reports_active_true(client, auth_headers):
    # OpenAPI v1.1 quirk: HR's single-employee lookup exposes no active
    # flag, so this route always reports is_active true.
    response = client.get("/api/directory/v1/workers/5542", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_exact_worker_not_found(client, auth_headers):
    response = client.get("/api/directory/v1/workers/999999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"] == "WORKER_NOT_FOUND"


def test_method_not_allowed(client, auth_headers):
    response = client.post("/api/directory/v1/workers", headers=auth_headers)
    assert response.status_code == 405
