"""GET /bci-radiology/visits/today -- versions/v1.3/requirements/1-bci-radiology-visits-today/."""
from datetime import date

import pytest
from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app
from app.models import BciPatient, BciVisit, Patient
from app.services import bci_service

URL = "/api/directory/v1/bci-radiology/visits/today"
ITEM_FIELDS = {
    "visit_id", "mrn",
    "first_name_ar", "father_name_ar", "last_name_ar", "mother_name_ar",
    "first_name_en", "father_name_en", "last_name_en", "mother_name_en",
    "birth_date", "sex", "visit_time", "visit_kind", "doctor_name", "status",
}


@pytest.fixture()
def winter_day(monkeypatch):
    monkeypatch.setattr(bci_service, "beirut_today", lambda: date(2026, 11, 4))


def _patient(mrn, **kw):
    return BciPatient(mrn=mrn, phones=[], has_allergy=False, **kw)


def _visit(visit_id, mrn, clock, **kw):
    return BciVisit(visit_id=visit_id, mrn=mrn, visit_clock=clock,
                    visit_kind=kw.pop("visit_kind", "scheduled"),
                    doctor_name=kw.pop("doctor_name", "Dr. Test-A"),
                    status=kw.pop("status", "registered"))


def test_an_empty_day_is_200_with_no_items(client, auth_headers):
    response = client.get(URL, headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"success": True, "items": [], "total": 0}


def test_visits_come_back_ordered_by_time_then_visit_id(client, db_session, auth_headers, winter_day):
    db_session.add_all([_patient("9999.000001"), _patient("9999.000002")])
    db_session.flush()
    db_session.add_all([
        _visit("V9999-0003", "9999.000002", "10:00"),
        _visit("V9999-0002", "9999.000001", "08:15"),
        _visit("V9999-0001", "9999.000001", "08:15"),
    ])
    db_session.commit()
    body = client.get(URL, headers=auth_headers).json()
    assert [i["visit_id"] for i in body["items"]] == ["V9999-0001", "V9999-0002", "V9999-0003"]
    assert body["total"] == 3


def test_a_patient_with_two_visits_appears_twice(client, db_session, auth_headers, winter_day):
    db_session.add(_patient("9999.000001"))
    db_session.flush()
    db_session.add_all([_visit("V9999-0001", "9999.000001", "08:15"),
                        _visit("V9999-0002", "9999.000001", "13:00", visit_kind="walk_in")])
    db_session.commit()
    items = client.get(URL, headers=auth_headers).json()["items"]
    assert [i["mrn"] for i in items] == ["9999.000001", "9999.000001"]
    assert [i["visit_kind"] for i in items] == ["scheduled", "walk_in"]


def test_visit_time_is_today_in_beirut_with_the_winter_offset(client, db_session, auth_headers, winter_day):
    db_session.add(_patient("9999.000001"))
    db_session.flush()
    db_session.add(_visit("V9999-0001", "9999.000001", "08:30"))
    db_session.commit()
    item = client.get(URL, headers=auth_headers).json()["items"][0]
    assert item["visit_time"] == "2026-11-04T08:30:00+02:00"


def test_visit_time_uses_the_summer_offset_in_summer(client, db_session, auth_headers, monkeypatch):
    monkeypatch.setattr(bci_service, "beirut_today", lambda: date(2026, 7, 15))
    db_session.add(_patient("9999.000001"))
    db_session.flush()
    db_session.add(_visit("V9999-0001", "9999.000001", "08:30"))
    db_session.commit()
    item = client.get(URL, headers=auth_headers).json()["items"][0]
    assert item["visit_time"] == "2026-07-15T08:30:00+03:00"


def test_item_carries_exactly_the_documented_fields_with_arabic_intact(client, db_session, auth_headers, winter_day):
    db_session.add(_patient(
        "9999.000001", first_name_ar="عمار", father_name_ar="كاظم", last_name_ar="الجبوري",
        mother_name_ar="أمل", first_name_en="Ammar", sex="Male", birth_date=date(1972, 1, 25)))
    db_session.flush()
    db_session.add(_visit("V9999-0001", "9999.000001", "08:00", status="frozen"))
    db_session.commit()
    response = client.get(URL, headers=auth_headers)
    assert "charset=utf-8" in response.headers["content-type"]
    item = response.json()["items"][0]
    assert set(item) == ITEM_FIELDS
    assert (item["first_name_ar"], item["last_name_ar"], item["mother_name_ar"]) == ("عمار", "الجبوري", "أمل")
    assert item["father_name_en"] is None  # English not stored
    assert (item["birth_date"], item["sex"], item["status"]) == ("1972-01-25", "Male", "frozen")


def test_limit_and_offset_have_no_effect(client, db_session, auth_headers, winter_day):
    db_session.add(_patient("9999.000001"))
    db_session.flush()
    db_session.add_all([_visit(f"V9999-000{i}", "9999.000001", f"0{i}:00") for i in range(1, 5)])
    db_session.commit()
    assert client.get(URL, params={"limit": 1, "offset": 2}, headers=auth_headers).json()["total"] == 4


def test_no_key_and_wrong_key_are_401(client):
    for headers in ({}, {"X-API-Key": "wrong"}):
        response = client.get(URL, headers=headers)
        assert response.status_code == 401
        assert response.json()["error"] == "UNAUTHORIZED"


def test_an_unreadable_source_is_503_never_an_empty_list(client, auth_headers):
    class BrokenSession:
        def execute(self, *a, **kw):
            raise OperationalError("SELECT", {}, Exception("connection refused"))

    def broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    response = client.get(URL, headers=auth_headers)
    assert response.status_code == 503
    assert response.json() == {"error": "SERVICE_UNAVAILABLE", "message": "The source of visits is unavailable"}


def test_the_directory_patients_table_is_not_touched(client, db_session, auth_headers, winter_day):
    db_session.add(_patient("9999.000001"))
    db_session.commit()
    assert db_session.query(Patient).filter(Patient.patient_id.like("9999.%")).count() == 0
