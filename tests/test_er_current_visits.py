from datetime import datetime, timedelta, timezone

from app.models import ErVisit

TZ = timezone(timedelta(hours=3))


def test_er_current_visits_empty_is_200(client, auth_headers):
    response = client.get("/api/directory/v1/er/current-visits", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["items"] == []
    assert body["total"] == 0


def test_er_current_visits_returns_items_ordered_by_arrival_ascending(client, db_session, auth_headers):
    now = datetime(2026, 9, 18, 12, 0, 0, tzinfo=TZ)
    db_session.add_all([
        ErVisit(
            er_visit_id="90003",
            first_name="Third",
            father_name="Arrival",
            last_name="Visit",
            arrival_time=now + timedelta(hours=2),
        ),
        ErVisit(
            er_visit_id="90001",
            first_name="First",
            father_name="Arrival",
            last_name="Visit",
            arrival_time=now,
        ),
        ErVisit(
            er_visit_id="90002",
            first_name="Second",
            father_name="Arrival",
            last_name="Visit",
            arrival_time=now + timedelta(hours=1),
        ),
    ])
    db_session.commit()

    response = client.get("/api/directory/v1/er/current-visits", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert [item["er_visit_id"] for item in body["items"]] == ["90001", "90002", "90003"]


def test_er_current_visits_has_no_pagination_params(client, db_session, auth_headers):
    # Deliberate deviation from every other list endpoint -- see
    # requirement.md section 4. limit/offset must have no effect at all.
    now = datetime(2026, 9, 18, 12, 0, 0, tzinfo=TZ)
    db_session.add_all([
        ErVisit(
            er_visit_id=f"9010{i}",
            first_name="Name",
            father_name="Father",
            last_name="Last",
            arrival_time=now + timedelta(minutes=i),
        )
        for i in range(5)
    ])
    db_session.commit()

    response = client.get(
        "/api/directory/v1/er/current-visits",
        params={"limit": 1, "offset": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["total"] == 5


def test_er_current_visits_field_set(client, db_session, auth_headers):
    db_session.add(
        ErVisit(
            er_visit_id="90201",
            first_name="Field",
            father_name="Set",
            last_name="Check",
            arrival_time=datetime(2026, 9, 18, 12, 0, 0, tzinfo=TZ),
            gender="Male",
            age=40,
            chief_complaint="Fever",
        )
    )
    db_session.commit()

    response = client.get("/api/directory/v1/er/current-visits", headers=auth_headers)
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert set(item.keys()) == {
        "er_visit_id", "first_name", "father_name", "last_name",
        "arrival_time", "gender", "age", "chief_complaint",
    }
    assert item["gender"] == "Male"
    assert item["age"] == 40
    assert item["chief_complaint"] == "Fever"


def test_er_current_visits_arrival_time_serializes_with_utc3_offset(client, db_session, auth_headers):
    # Regression check for the naive-vs-aware datetime split between SQLite
    # (this test) and Postgres (the real deployment): the serializer must
    # not silently reinterpret the stored wall-clock time.
    db_session.add(
        ErVisit(
            er_visit_id="90301",
            first_name="Offset",
            father_name="Check",
            last_name="Visit",
            arrival_time=datetime(2026, 9, 18, 14, 32, 0, tzinfo=TZ),
        )
    )
    db_session.commit()

    response = client.get("/api/directory/v1/er/current-visits", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["items"][0]["arrival_time"] == "2026-09-18T14:32:00+03:00"


def test_er_current_visits_requires_auth(client):
    response = client.get("/api/directory/v1/er/current-visits")
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"
