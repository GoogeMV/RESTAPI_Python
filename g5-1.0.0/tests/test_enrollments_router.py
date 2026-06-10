import pytest
from fastapi.testclient import TestClient
from main import app  # Importăm aplicația principală FastAPI

client = TestClient(app)


# Ne asigurăm că baza de date locală (memoria) are câteva date de test înainte de rulare
@pytest.fixture(autouse=True)
def setup_database():
    from enrollments.app import data as db

    # Resetăm baza de date fictivă pentru a avea un mediu curat la fiecare test
    db.enrollments_db = {
        1: {"id": 1, "student_id": 10, "course_name": "Matematica", "professor_id": 100, "status": "enrolled"},
        2: {"id": 2, "student_id": 11, "course_name": "Fizica", "professor_id": 101, "status": "enrolled"},
    }
    db.next_id = 3


# --- TEST 1: Creare înscriere validă (Succes) ---
def test_create_enrollment_success():
    payload = {"student_id": 12, "course_name": "Informatica", "professor_id": 102}
    response = client.post("/enrollments/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == 12
    assert data["course_name"] == "Informatica"
    assert data["status"] == "enrolled"  # Verificăm statusul implicit


# --- TEST 2: Eroare de validare Pydantic (student_id negativ) ---
def test_create_enrollment_invalid_student_id():
    payload = {
        "student_id": -5,  # ID invalid, în schemas avem gt=0
        "course_name": "Chimie",
        "professor_id": 103,
    }
    response = client.post("/enrollments/", json=payload)
    assert response.status_code == 422  # Unprocessable Entity


# --- TEST 3: Eroare de business (Student duplicat la același curs) ---
def test_create_enrollment_duplicate():
    payload = {
        "student_id": 10,  # Studentul 10 există deja la Matematica în setup
        "course_name": "Matematica",
        "professor_id": 100,
    }
    response = client.post("/enrollments/", json=payload)
    assert response.status_code == 400  # Bad Request
    assert response.json()["detail"] == "Student deja inscris la acest curs"


# --- TEST 4: Verificare Paginare (Limit și Offset) ---
def test_get_enrollments_pagination():
    # Trimitem limit=1, deci ar trebui să ne returneze doar o singură înscriere din cele 2 existente
    response = client.get("/enrollments/?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


# --- TEST 5: Modificare Status Endpoint (PUT) ---
def test_update_enrollment_status_success():
    payload = {"status": "waitlist"}
    # Modificăm statusul înscrierii cu ID-ul 1 (creată în setup)
    response = client.put("/enrollments/1/status", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "waitlist"
