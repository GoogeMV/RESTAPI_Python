import pytest
from fastapi.testclient import TestClient
from main import app
from grades.app import data as db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Acest fixture curăță baza de date din memorie înainte de fiecare test
    și adaugă date de test proaspete.
    """
    db.grades_db.clear()
    db.next_id = 1
    yield
    db.grades_db.clear()


def clean_database():
    """
    Acest fixture rulează automat înainte de FIECARE test.
    Golește baza de date din memorie pentru ca testele să fie complet independente.
    """
    db.grades_db.clear()
    db.next_id = 1
    yield
    db.grades_db.clear()


# 1. Teste pentru creare notă (POST /)
def test_create_grade_success():
    payload = {"student_id": 1, "course_name": "Matematica", "value": 9.5}
    response = client.post("/grades/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["student_id"] == 1
    assert data["course_name"] == "Matematica"
    assert data["value"] == 9.5


def test_create_grade_invalid_value_high():
    payload = {"student_id": 1, "course_name": "Matematica", "value": 12.5}
    response = client.post("/grades/", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_create_grade_invalid_course_name_short():
    # Numele cursului este prea scurt (trebuie să fie >= 3 caractere)
    payload = {"student_id": 1, "course_name": "Xi", "value": 8.0}
    response = client.post("/grades/", json=payload)
    assert response.status_code == 422


# 2. Teste pentru listare, paginare ȘI filtrare (GET /)


def test_list_grades_pagination_and_filter():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Mate", "value": 4.5}
    db.grades_db[2] = {"id": 2, "student_id": 2, "course_name": "Fizica", "value": 8.0}
    db.grades_db[3] = {"id": 3, "student_id": 3, "course_name": "Chimie", "value": 9.5}

    res_limit = client.get("/grades/?limit=2")
    assert res_limit.status_code == 200
    assert len(res_limit.json()) == 2

    res_filter = client.get("/grades/?min_value=8.0")
    assert res_filter.status_code == 200
    data_filter = res_filter.json()
    assert len(data_filter) == 2
    assert all(g["value"] >= 8.0 for g in data_filter)


# 3. Teste pentru detaliu notă (GET /{grade_id})
def test_get_grade_success():
    db.grades_db[1] = {"id": 1, "student_id": 5, "course_name": "Mate", "value": 7.0}
    response = client.get("/grades/1")
    assert response.status_code == 200
    assert response.json()["course_name"] == "Mate"


def test_get_grade_not_found():
    response = client.get("/grades/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Grade not found"


# 4. Teste pentru transcript și GPA (SITUAȚIE ȘCOLARĂ)
def test_get_transcript_success():
    db.grades_db[1] = {"id": 1, "student_id": 10, "course_name": "Mate", "value": 9.0}
    db.grades_db[2] = {"id": 2, "student_id": 11, "course_name": "Mate", "value": 8.0}  # Alt student

    response = client.get("/grades/transcript/10")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["student_id"] == 10


def test_get_gpa_calculated():
    db.grades_db[1] = {"id": 1, "student_id": 10, "course_name": "Mate", "value": 10.0}
    db.grades_db[2] = {"id": 2, "student_id": 10, "course_name": "Fizica", "value": 8.0}

    response = client.get("/grades/gpa/10")
    assert response.status_code == 200
    assert response.json()["gpa"] == 9.0  # (10 + 8) / 2


def test_get_gpa_no_grades():
    response = client.get("/grades/gpa/999")
    assert response.status_code == 200
    assert response.json()["gpa"] == 0.0
    assert response.json()["message"] == "No grades found"


# 5. Teste pentru top studenți (GET /top/{n})
def test_get_top_students():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Mate", "value": 9.0}
    db.grades_db[2] = {"id": 2, "student_id": 2, "course_name": "Mate", "value": 10.0}

    response = client.get("/grades/top/2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["student_id"] == 2
    assert data[0]["gpa"] == 10.0


# 6. Teste pentru actualizare notă (PUT /{grade_id})
def test_update_grade_success():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Mate", "value": 6.0}

    payload = {"value": 9.0}
    response = client.put("/grades/1", json=payload)

    assert response.status_code == 200
    assert response.json()["value"] == 9.0
    assert db.grades_db[1]["value"] == 9.0


def test_update_grade_not_found():
    payload = {"value": 9.0}
    response = client.put("/grades/999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Grade not found"


# 7. Teste pentru ștergere notă (DELETE /{grade_id})
def test_delete_grade_success():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Mate", "value": 6.0}

    response = client.delete("/grades/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Grade deleted"
    assert 1 not in db.grades_db


def test_delete_grade_not_found():
    response = client.delete("/grades/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Grade not found"


# 8. Teste pentru statisici curs (GET /stats/{course_name})
def test_get_course_stats_success_1():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Python", "value": 10.0}
    db.grades_db[2] = {"id": 2, "student_id": 2, "course_name": "Python", "value": 6.0}

    response = client.get("/grades/stats/Python")
    assert response.status_code == 200
    data = response.json()
    assert data["average_grade"] == 8.0
    assert data["max_grade"] == 10.0
    assert data["min_grade"] == 6.0
    assert data["total_grades"] == 2


def test_get_course_stats_not_found_1():
    response = client.get("/grades/stats/Inexistenta")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"


# 9. test pentru succes (200 OK)
def test_get_course_stats_success_2():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Programare Python", "value": 10.0}
    db.grades_db[2] = {"id": 2, "student_id": 2, "course_name": "Programare Python", "value": 8.0}
    db.grades_db[3] = {"id": 3, "student_id": 3, "course_name": "Mate", "value": 5.0}  # Alt curs, nu trebuie inclus

    response = client.get("/grades/stats/Programare Python")

    assert response.status_code == 200
    data = response.json()
    assert data["course_name"] == "Programare Python"
    assert data["average_grade"] == 9.0  # (10 + 8) / 2
    assert data["max_grade"] == 10.0
    assert data["min_grade"] == 8.0
    assert data["total_grades"] == 2


# 10. test pentru case-insensitivity și strip (200 OK)
def test_get_course_stats_case_insensitive():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Programare Python", "value": 9.0}

    response = client.get("/grades/stats/%20%20programare%20python%20%20")

    assert response.status_code == 200
    assert response.json()["total_grades"] == 1


# 11. test pentru cazul de eroare (404 Not Found)
def test_get_course_stats_not_found_2():
    db.grades_db[1] = {"id": 1, "student_id": 1, "course_name": "Istorie", "value": 7.0}

    response = client.get("/grades/stats/Chimie")

    assert response.status_code == 404
    assert "Course not found" in response.json()["detail"]
