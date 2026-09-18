from app.models import Worker


def test_worker_list_includes_section_and_administration_names(client, db_session, auth_headers):
    db_session.add(
        Worker(
            employee_id="70201",
            full_name="Section Test Worker",
            section_id="3",
            section_name="Emergency Response",
            administration_id="1",
            administration_name="Medical Affairs",
            is_active=True,
        )
    )
    db_session.commit()

    response = client.get("/api/directory/v1/workers/70201", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["section_name"] == "Emergency Response"
    assert body["administration_name"] == "Medical Affairs"


def test_worker_section_and_administration_names_default_to_null(client, auth_headers):
    # employee_id 5541 is seeded in conftest.py without section/administration
    # fields set at all -- confirms the new columns are nullable and don't
    # break an existing record that predates this addition.
    response = client.get("/api/directory/v1/workers/5541", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["section_name"] is None
    assert body["administration_name"] is None


def test_worker_list_field_set_includes_new_names(client, auth_headers):
    response = client.get("/api/directory/v1/workers", headers=auth_headers)
    assert response.status_code == 200
    worker = response.json()["items"][0]
    assert "section_name" in worker
    assert "administration_name" in worker
