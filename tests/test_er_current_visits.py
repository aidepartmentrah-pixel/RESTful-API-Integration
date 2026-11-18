"""ER current visits, as 3iSoft delivered it (v1.2): a separate ER API at
/his-er/api/er/v1/current-visits with its own key (meraj:8080 in production)."""
from datetime import datetime, timedelta, timezone

from app.models import ErVisit

ER_URL = "/his-er/api/er/v1/current-visits"
TZ = timezone(timedelta(hours=3))
MALE, FEMALE = "ذكر", "انثى"


def _visit(er_visit_id, minutes=0, **kw):
    base = dict(first_name="أحمد", father_name="خليل", last_name="منصور",
                arrival_time=datetime(2026, 9, 18, 12, 0, 0, tzinfo=TZ) + timedelta(minutes=minutes))
    base.update(kw)
    return ErVisit(er_visit_id=er_visit_id, **base)


def test_empty_is_200(client, er_headers):
    response = client.get(ER_URL, headers=er_headers)
    assert response.status_code == 200
    assert response.json() == {"success": True, "items": [], "total": 0}


def test_ordered_by_arrival_then_visit_id(client, db_session, er_headers):
    db_session.add_all([
        _visit("90003", 120), _visit("90010", 0), _visit("9002", 0), _visit("90002", 60),
    ])
    db_session.commit()
    body = client.get(ER_URL, headers=er_headers).json()
    assert body["total"] == 4
    # equal times by visit id (numeric order: 9002 before 90010)
    assert [i["er_visit_id"] for i in body["items"]] == ["9002", "90010", "90002", "90003"]


def test_full_snapshot_ignores_paging_params(client, db_session, er_headers):
    db_session.add_all([_visit(f"9010{i}", i) for i in range(5)])
    db_session.commit()
    response = client.get(ER_URL, params={"limit": 1, "offset": 0}, headers=er_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 5
    assert len(response.json()["items"]) == 5


def test_fields_always_present_and_null_when_empty(client, db_session, er_headers):
    db_session.add_all([
        _visit("90201", gender=MALE, age=48, chief_complaint="ألم في الصدر"),
        _visit("90202", 1, father_name=None, gender=None, age=None, chief_complaint=None),
    ])
    db_session.commit()
    items = client.get(ER_URL, headers=er_headers).json()["items"]
    fields = {"er_visit_id", "first_name", "father_name", "last_name", "arrival_time", "gender", "age", "chief_complaint"}
    assert all(set(i.keys()) == fields for i in items)
    assert items[0]["gender"] == MALE and items[0]["age"] == 48 and items[0]["chief_complaint"] == "ألم في الصدر"
    assert items[1]["father_name"] is None and items[1]["gender"] is None
    assert items[1]["age"] is None and items[1]["chief_complaint"] is None


def test_arrival_time_has_beirut_offset(client, db_session, er_headers):
    # September: Beirut summer time, +03:00. (SQLite keeps the wall-clock digits.)
    db_session.add(_visit("90301", arrival_time=datetime(2026, 9, 18, 14, 32, 0, tzinfo=TZ)))
    db_session.commit()
    item = client.get(ER_URL, headers=er_headers).json()["items"][0]
    assert item["arrival_time"] == "2026-09-18T14:32:00+03:00"


def test_arrival_time_winter_offset_is_plus_two(client, db_session, er_headers):
    db_session.add(_visit("90302", arrival_time=datetime(2026, 11, 10, 7, 15, 0)))
    db_session.commit()
    item = client.get(ER_URL, headers=er_headers).json()["items"][0]
    assert item["arrival_time"] == "2026-11-10T07:15:00+02:00"


def test_requires_er_key(client):
    response = client.get(ER_URL)
    assert response.status_code == 401
    assert response.json() == {"error": "UNAUTHORIZED", "message": "Missing or invalid API key"}


def test_directory_key_is_rejected(client, auth_headers):
    response = client.get(ER_URL, headers=auth_headers)
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_method_not_allowed(client, er_headers):
    response = client.post(ER_URL, headers=er_headers)
    assert response.status_code == 405
    assert response.json()["error"] == "METHOD_NOT_ALLOWED"


def test_old_directory_er_path_is_gone(client, auth_headers):
    # The v1.2 proposal put it under the Directory API; 3iSoft did not.
    for prefix in ("/his-general/api/directory/v1", "/api/directory/v1"):
        assert client.get(f"{prefix}/er/current-visits", headers=auth_headers).status_code == 404
