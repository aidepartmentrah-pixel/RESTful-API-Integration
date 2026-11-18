"""GET /hr-workers, as 3iSoft delivered it (v1.2, "HIS API - v1.2 Additions")."""
import pytest

from app.models import HrUnit, Worker

URL = "/his-general/api/directory/v1/hr-workers"
FIELDS = {"employee_id", "full_name", "job_id", "job_title", "administration_id", "administration_name",
          "section_id", "section_name", "department_id", "department_name", "is_manager", "is_active"}

TREE = [
    ("A1", "الإدارة الطبية", "administration", None, True),
    ("S1", "دائرة التمريض", "section", "A1", True),
    ("D1", "قسم الطوارئ", "department", "S1", True),
    ("D2", "قسم العناية الفائقة", "department", "S1", True),
    ("A2", "الإدارة المالية", "administration", None, True),
    ("S2", "دائرة المحاسبة", "section", "A2", True),
    ("D3", "قسم الأرشيف", "department", "S2", True),
    ("S3", "دائرة الموارد", "section", "A1", True),
    ("D4", "قسم الأرشيف", "department", "S3", False),   # same name as D3, and inactive
]


@pytest.fixture()
def hr(client, db_session):
    for unit_id, name, level, parent, active in TREE:
        db_session.add(HrUnit(unit_id=unit_id, name=name, level=level, parent_unit_id=parent, is_active=active))
    for emp, unit in [("6080.1", "D1"), ("6080.2", "D1"), ("6080.3", "D2"), ("6080.4", "S1"),
                      ("6080.5", "D3"), ("6080.6", "D4"), ("6080.7", "A2")]:
        db_session.add(Worker(employee_id=emp, full_name=f"موظف {emp}", job_id="6080.977", job_title="ممرض",
                              hr_unit_id=unit, is_active=True))
    db_session.commit()
    return client


def ids(response):
    return sorted(w["employee_id"] for w in response.json()["items"])


def test_list_envelope_default_paging_and_fields(hr, auth_headers):
    r = hr.get(URL, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"success", "items", "total", "limit", "offset"}
    assert body["limit"] == 10 and body["offset"] == 0
    assert body["total"] == 9  # 7 placed + the 2 conftest workers without a unit
    assert all(set(w.keys()) == FIELDS for w in body["items"])


def test_placement_walks_up_the_tree(hr, auth_headers):
    w = hr.get(f"{URL}/6080.1", headers=auth_headers).json()
    assert (w["administration_id"], w["section_id"], w["department_id"]) == ("A1", "S1", "D1")
    assert (w["administration_name"], w["section_name"], w["department_name"]) == ("الإدارة الطبية", "دائرة التمريض", "قسم الطوارئ")
    in_section = hr.get(f"{URL}/6080.4", headers=auth_headers).json()
    assert in_section["section_id"] == "S1" and in_section["department_id"] is None and in_section["administration_id"] == "A1"
    in_admin = hr.get(f"{URL}/6080.7", headers=auth_headers).json()
    assert in_admin["administration_id"] == "A2" and in_admin["section_id"] is None
    no_unit = hr.get(f"{URL}/5541", headers=auth_headers).json()
    assert no_unit["administration_name"] is None and set(no_unit.keys()) == FIELDS


def test_single_worker_has_no_envelope(hr, auth_headers):
    body = hr.get(f"{URL}/6080.1", headers=auth_headers).json()
    assert set(body.keys()) == FIELDS


def test_unknown_worker_is_404(hr, auth_headers):
    r = hr.get(f"{URL}/999999999", headers=auth_headers)
    assert r.status_code == 404 and r.json()["error"] == "WORKER_NOT_FOUND"


def test_administration_filter_includes_units_below(hr, auth_headers):
    r = hr.get(URL, params={"administration": "الإدارة الطبية", "limit": 50}, headers=auth_headers)
    assert ids(r) == ["6080.1", "6080.2", "6080.3", "6080.4", "6080.6"]
    assert r.json()["total"] == 5


def test_section_and_department_filters(hr, auth_headers):
    assert ids(hr.get(URL, params={"section": "دائرة التمريض"}, headers=auth_headers)) == ["6080.1", "6080.2", "6080.3", "6080.4"]
    assert ids(hr.get(URL, params={"department": "قسم الطوارئ"}, headers=auth_headers)) == ["6080.1", "6080.2"]


def test_spelling_is_unified_and_spaces_trimmed(hr, auth_headers):
    # 3iSoft's example: "الادارة الطبيه" matches "الإدارة الطبية".
    r = hr.get(URL, params={"administration": "  الادارة الطبيه  ", "limit": 50}, headers=auth_headers)
    assert r.json()["total"] == 5


def test_same_name_units_both_match_including_inactive(hr, auth_headers):
    assert ids(hr.get(URL, params={"department": "قسم الارشيف"}, headers=auth_headers)) == ["6080.5", "6080.6"]


def test_filters_combine_with_and(hr, auth_headers):
    r = hr.get(URL, params={"administration": "الإدارة المالية", "department": "قسم الأرشيف"}, headers=auth_headers)
    assert ids(r) == ["6080.5"]


def test_unknown_name_or_wrong_level_is_empty_not_error(hr, auth_headers):
    for params in ({"section": "لا يوجد"}, {"section": "الإدارة الطبية"}):
        r = hr.get(URL, params=params, headers=auth_headers)
        assert r.status_code == 200 and r.json()["total"] == 0 and r.json()["items"] == []


def test_empty_filter_is_ignored(hr, auth_headers):
    assert hr.get(URL, params={"section": ""}, headers=auth_headers).json()["total"] == 9


def test_filter_before_paging(hr, auth_headers):
    r = hr.get(URL, params={"administration": "الإدارة الطبية", "limit": 2, "offset": 2}, headers=auth_headers)
    assert r.json()["total"] == 5 and len(r.json()["items"]) == 2


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 501}, {"offset": -1}])
def test_paging_validation(hr, auth_headers, params):
    r = hr.get(URL, params=params, headers=auth_headers)
    assert r.status_code == 422 and r.json()["error"] == "VALIDATION_ERROR"


def test_requires_directory_key(hr, er_headers):
    assert hr.get(URL).status_code == 401
    assert hr.get(URL, headers=er_headers).status_code == 401
