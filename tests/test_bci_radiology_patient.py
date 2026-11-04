"""GET /bci-radiology/patients/{mrn} -- versions/v1.3/requirements/2-bci-radiology-patient/."""
from datetime import date

from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app
from app.models import BciPatient

BASE = "/api/directory/v1/bci-radiology/patients"
FIELDS = {
    "mrn", "first_name_ar", "father_name_ar", "last_name_ar", "mother_name_ar",
    "first_name_en", "father_name_en", "last_name_en", "mother_name_en",
    "birth_date", "sex", "nationality", "id_number", "has_allergy", "phones",
}


def _add(db_session, mrn="9999.000007", **kw):
    defaults = dict(
        first_name_ar="عمار", father_name_ar="كاظم", last_name_ar="الجبوري", mother_name_ar="أمل",
        first_name_en="Ammar", father_name_en="Kazem", last_name_en="Al-Jubouri", mother_name_en="Amal",
        birth_date=date(1972, 1, 25), sex="Male", nationality="Iraqi", id_number="TEST-ID-0007",
        has_allergy=True,
        phones=[{"number": "00-000-009", "owner": "self"}, {"number": "00-000-010", "owner": "brother"}],
    )
    db_session.add(BciPatient(mrn=mrn, **{**defaults, **kw}))
    db_session.commit()


def test_a_known_mrn_returns_the_documented_fields(client, db_session, auth_headers):
    _add(db_session)
    response = client.get(f"{BASE}/9999.000007", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == FIELDS  # a single object, no envelope
    assert body["mrn"] == "9999.000007"
    assert body["nationality"] == "Iraqi" and body["id_number"] == "TEST-ID-0007"
    assert body["has_allergy"] is True
    assert body["birth_date"] == "1972-01-25"
    assert body["phones"] == [{"number": "00-000-009", "owner": "self"},
                              {"number": "00-000-010", "owner": "brother"}]


def test_arabic_comes_back_as_utf8(client, db_session, auth_headers):
    _add(db_session)
    response = client.get(f"{BASE}/9999.000007", headers=auth_headers)
    assert "charset=utf-8" in response.headers["content-type"]
    body = response.json()
    assert (body["first_name_ar"], body["father_name_ar"], body["last_name_ar"], body["mother_name_ar"]) == \
        ("عمار", "كاظم", "الجبوري", "أمل")
    assert "عمار".encode("utf-8") in response.content  # raw bytes are UTF-8, not escaped or Latin-1


def test_missing_values_come_back_as_null_and_phones_may_be_empty(client, db_session, auth_headers):
    _add(db_session, birth_date=None, id_number=None, first_name_en=None, father_name_en=None,
         last_name_en=None, mother_name_en=None, has_allergy=False, phones=[])
    body = client.get(f"{BASE}/9999.000007", headers=auth_headers).json()
    assert body["birth_date"] is None and body["id_number"] is None
    assert body["first_name_en"] is None
    assert body["has_allergy"] is False and body["phones"] == []


def test_two_mrns_of_one_person_are_two_separate_patients(client, db_session, auth_headers):
    _add(db_session, mrn="9999.000003", last_name_ar="الحسيني")
    _add(db_session, mrn="9999.000103", last_name_ar="الحسينى")
    assert client.get(f"{BASE}/9999.000003", headers=auth_headers).json()["last_name_ar"] == "الحسيني"
    assert client.get(f"{BASE}/9999.000103", headers=auth_headers).json()["last_name_ar"] == "الحسينى"


def test_the_mrn_is_matched_exactly_not_by_prefix(client, db_session, auth_headers):
    _add(db_session)
    assert client.get(f"{BASE}/9999.00000", headers=auth_headers).status_code == 404
    assert client.get(f"{BASE}/9999", headers=auth_headers).status_code == 404


def test_an_unknown_mrn_is_404_patient_not_found(client, auth_headers):
    response = client.get(f"{BASE}/9999.999999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json() == {"error": "PATIENT_NOT_FOUND", "message": "The requested patient was not found"}


def test_no_key_and_wrong_key_are_401(client, db_session):
    _add(db_session)
    for headers in ({}, {"X-API-Key": "wrong"}):
        response = client.get(f"{BASE}/9999.000007", headers=headers)
        assert response.status_code == 401
        assert response.json()["error"] == "UNAUTHORIZED"


def test_an_unreadable_source_is_503_not_404(client, auth_headers):
    class BrokenSession:
        def execute(self, *a, **kw):
            raise OperationalError("SELECT", {}, Exception("connection refused"))

    def broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    response = client.get(f"{BASE}/9999.000007", headers=auth_headers)
    assert response.status_code == 503
    assert response.json()["error"] == "SERVICE_UNAVAILABLE"
