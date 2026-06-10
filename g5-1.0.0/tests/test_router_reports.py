import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from reports.app import router, service, data

app = FastAPI()
app.include_router(router.router, prefix="/reports")

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    data.reports_db.clear()
    data.next_id = 1
    yield


# ============================================================================
# GET /reports/enrollment-stats
# ============================================================================


def test_enrollment_stats_returns_200():
    with patch.object(service, "get_enrollment_stats", return_value={}):
        r = client.get("/reports/enrollment-stats")
    assert r.status_code == 200


def test_enrollment_stats_empty():
    with patch.object(service, "get_enrollment_stats", return_value={}):
        r = client.get("/reports/enrollment-stats")
    assert r.json() == {}


def test_enrollment_stats_counts_per_course():
    with patch.object(service, "get_enrollment_stats", return_value={"Matematica": 2, "Fizica": 1}):
        r = client.get("/reports/enrollment-stats")
    assert r.json() == {"Matematica": 2, "Fizica": 1}


def test_enrollment_stats_single_entry():
    with patch.object(service, "get_enrollment_stats", return_value={"Chimie": 1}):
        r = client.get("/reports/enrollment-stats")
    assert r.json()["Chimie"] == 1


def test_enrollment_stats_returns_dict():
    with patch.object(service, "get_enrollment_stats", return_value={"Biologie": 3}):
        r = client.get("/reports/enrollment-stats")
    assert isinstance(r.json(), dict)


def test_enrollment_stats_db_unchanged():
    with patch.object(service, "get_enrollment_stats", return_value={"Matematica": 1}):
        client.get("/reports/enrollment-stats")
    assert data.reports_db == {}


# ============================================================================
# GET /reports/grade-distribution
# ============================================================================


def test_grade_distribution_returns_200():
    with patch.object(service, "get_grade_distribution", return_value={}):
        r = client.get("/reports/grade-distribution")
    assert r.status_code == 200


def test_grade_distribution_empty():
    with patch.object(service, "get_grade_distribution", return_value={}):
        r = client.get("/reports/grade-distribution")
    assert r.json() == {}


def test_grade_distribution_average_per_course():
    with patch.object(service, "get_grade_distribution", return_value={"Matematica": 9.0, "Fizica": 6.0}):
        r = client.get("/reports/grade-distribution")
    assert r.json() == {"Matematica": 9.0, "Fizica": 6.0}


def test_grade_distribution_min_avg_passed_to_service():
    with patch.object(service, "get_grade_distribution", return_value={"Matematica": 9.5}) as mock:
        r = client.get("/reports/grade-distribution?min_avg=7.0")
    assert r.status_code == 200
    mock.assert_called_once_with(min_avg=7.0)


def test_grade_distribution_default_min_avg_is_zero():
    with patch.object(service, "get_grade_distribution", return_value={}) as mock:
        client.get("/reports/grade-distribution")
    mock.assert_called_once_with(min_avg=0.0)


def test_grade_distribution_min_avg_negative_returns_422():
    r = client.get("/reports/grade-distribution?min_avg=-1.0")
    assert r.status_code == 422


def test_grade_distribution_filters_via_service():
    with patch.object(service, "get_grade_distribution", return_value={"Matematica": 9.5}):
        r = client.get("/reports/grade-distribution?min_avg=7.0")
    data_json = r.json()
    assert "Matematica" in data_json
    assert "Fizica" not in data_json


def test_grade_distribution_returns_dict():
    with patch.object(service, "get_grade_distribution", return_value={"Info": 8.5}):
        r = client.get("/reports/grade-distribution")
    assert isinstance(r.json(), dict)


def test_grade_distribution_db_unchanged():
    with patch.object(service, "get_grade_distribution", return_value={"Fizica": 7.0}):
        client.get("/reports/grade-distribution")
    assert data.reports_db == {}


# ============================================================================
# GET /reports/student-count
# ============================================================================


def test_student_count_returns_200():
    with patch.object(service, "get_student_count", return_value=0):
        r = client.get("/reports/student-count")
    assert r.status_code == 200


def test_student_count_key_present():
    with patch.object(service, "get_student_count", return_value=5):
        r = client.get("/reports/student-count")
    assert "student_count" in r.json()


def test_student_count_value_matches_service():
    with patch.object(service, "get_student_count", return_value=42):
        r = client.get("/reports/student-count")
    assert r.json()["student_count"] == 42


def test_student_count_is_integer():
    with patch.object(service, "get_student_count", return_value=7):
        r = client.get("/reports/student-count")
    assert isinstance(r.json()["student_count"], int)


def test_student_count_zero():
    with patch.object(service, "get_student_count", return_value=0):
        r = client.get("/reports/student-count")
    assert r.json()["student_count"] == 0


# ============================================================================
# GET /reports/professor-count
# ============================================================================


def test_professor_count_returns_200():
    with patch.object(service, "get_professor_count", return_value=0):
        r = client.get("/reports/professor-count")
    assert r.status_code == 200


def test_professor_count_key_present():
    with patch.object(service, "get_professor_count", return_value=3):
        r = client.get("/reports/professor-count")
    assert "professor_count" in r.json()


def test_professor_count_value_matches_service():
    with patch.object(service, "get_professor_count", return_value=10):
        r = client.get("/reports/professor-count")
    assert r.json()["professor_count"] == 10


def test_professor_count_is_integer():
    with patch.object(service, "get_professor_count", return_value=4):
        r = client.get("/reports/professor-count")
    assert isinstance(r.json()["professor_count"], int)


def test_professor_count_zero():
    with patch.object(service, "get_professor_count", return_value=0):
        r = client.get("/reports/professor-count")
    assert r.json()["professor_count"] == 0


# ============================================================================
# GET /reports/library-stats
# ============================================================================


def test_library_stats_returns_200():
    with patch.object(service, "get_library_stats", return_value={"total_books": 0, "active_loans": 0}):
        r = client.get("/reports/library-stats")
    assert r.status_code == 200


def test_library_stats_has_total_books_key():
    with patch.object(service, "get_library_stats", return_value={"total_books": 5, "active_loans": 2}):
        r = client.get("/reports/library-stats")
    assert "total_books" in r.json()


def test_library_stats_has_active_loans_key():
    with patch.object(service, "get_library_stats", return_value={"total_books": 5, "active_loans": 2}):
        r = client.get("/reports/library-stats")
    assert "active_loans" in r.json()


def test_library_stats_values_match_service():
    payload = {"total_books": 100, "active_loans": 13}
    with patch.object(service, "get_library_stats", return_value=payload):
        r = client.get("/reports/library-stats")
    assert r.json() == payload


def test_library_stats_fallback_zeros():
    with patch.object(service, "get_library_stats", return_value={"total_books": 0, "active_loans": 0}):
        r = client.get("/reports/library-stats")
    assert r.json()["total_books"] == 0
    assert r.json()["active_loans"] == 0


# ============================================================================
# GET /reports/export
# ============================================================================


def _all_patches(
    enrollment_stats=None,
    grade_distribution=None,
    student_count=0,
    professor_count=0,
    library_stats=None,
):
    return (
        patch.object(service, "get_enrollment_stats", return_value=enrollment_stats or {}),
        patch.object(service, "get_grade_distribution", return_value=grade_distribution or {}),
        patch.object(service, "get_student_count", return_value=student_count),
        patch.object(service, "get_professor_count", return_value=professor_count),
        patch.object(service, "get_library_stats", return_value=library_stats or {"total_books": 0, "active_loans": 0}),
    )


def test_export_returns_200():
    with _all_patches()[0], _all_patches()[1], _all_patches()[2], _all_patches()[3], _all_patches()[4]:
        r = client.get("/reports/export")
    assert r.status_code == 200


def test_export_has_all_keys():
    p = _all_patches()
    with p[0], p[1], p[2], p[3], p[4]:
        r = client.get("/reports/export")
    data_json = r.json()
    for key in ("enrollment_stats", "grade_distribution", "student_count", "professor_count", "library_stats"):
        assert key in data_json


def test_export_values_match_services():
    p = _all_patches(
        enrollment_stats={"Matematica": 2},
        grade_distribution={"Matematica": 9.0},
        student_count=15,
        professor_count=4,
        library_stats={"total_books": 50, "active_loans": 3},
    )
    with p[0], p[1], p[2], p[3], p[4]:
        r = client.get("/reports/export")
    d = r.json()
    assert d["enrollment_stats"] == {"Matematica": 2}
    assert d["grade_distribution"] == {"Matematica": 9.0}
    assert d["student_count"] == 15
    assert d["professor_count"] == 4
    assert d["library_stats"] == {"total_books": 50, "active_loans": 3}


def test_export_student_and_professor_count_are_integers():
    p = _all_patches(student_count=8, professor_count=3)
    with p[0], p[1], p[2], p[3], p[4]:
        r = client.get("/reports/export")
    d = r.json()
    assert isinstance(d["student_count"], int)
    assert isinstance(d["professor_count"], int)


def test_export_grade_distribution_called_with_no_args():
    with (
        patch.object(service, "get_enrollment_stats", return_value={}),
        patch.object(service, "get_grade_distribution", return_value={"Fizica": 4.0}) as mock_gd,
        patch.object(service, "get_student_count", return_value=0),
        patch.object(service, "get_professor_count", return_value=0),
        patch.object(service, "get_library_stats", return_value={"total_books": 0, "active_loans": 0}),
    ):
        client.get("/reports/export")
    mock_gd.assert_called_once_with()


def test_export_db_unchanged():
    p = _all_patches()
    with p[0], p[1], p[2], p[3], p[4]:
        client.get("/reports/export")
    assert data.reports_db == {}
    assert data.next_id == 1
