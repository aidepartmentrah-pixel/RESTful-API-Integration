"""v1.2 as delivered: the real Directory path works next to the mock's old one,
and /workers is unchanged from v1.1 (unit names went to /hr-workers)."""

WORKER_V11_FIELDS = {"employee_id", "full_name", "job_id", "job_title", "department_id", "department_name",
                     "section_id", "administration_id", "is_manager", "is_active"}


def test_real_and_legacy_directory_paths_both_work(client, auth_headers):
    for prefix in ("/his-general/api/directory/v1", "/api/directory/v1"):
        assert client.get(f"{prefix}/health").status_code == 200
        assert client.get(f"{prefix}/patients/10025", headers=auth_headers).status_code == 200
        assert client.get(f"{prefix}/hr-workers", headers=auth_headers).status_code == 200


def test_openapi_lists_only_the_real_paths(client):
    paths = client.get("/his-general/api/directory/v1/openapi.json").json()["paths"]
    assert "/his-general/api/directory/v1/hr-workers" in paths
    assert "/his-er/api/er/v1/current-visits" in paths
    assert not any(p.startswith("/api/directory/v1") for p in paths)


def test_workers_has_the_v1_1_fields_only(client, auth_headers):
    body = client.get("/his-general/api/directory/v1/workers/5541", headers=auth_headers).json()
    assert set(body.keys()) == WORKER_V11_FIELDS
