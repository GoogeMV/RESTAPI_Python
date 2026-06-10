from fastapi.testclient import TestClient
from students.app.router import router
from fastapi import FastAPI

# creăm app de test
app = FastAPI()
app.include_router(router, prefix="/students")

client = TestClient(app)


# 1. CREATE student
def test_create_student():
    response = client.post("/students/", json={"name": "Ion Popescu", "email": "ion@test.com", "year": 2})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ion Popescu"
    assert data["email"] == "ion@test.com"
    assert data["year"] == 2


# 2. GET all students
def test_get_all_students():
    response = client.get("/students/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# 3. GET student by ID
def test_get_student_by_id():
    # mai întâi creăm unul
    create = client.post("/students/", json={"name": "Maria Ionescu", "email": "maria@test.com", "year": 3})

    student_id = create.json()["id"]

    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["id"] == student_id


# 4. UPDATE student
def test_update_student():
    create = client.post("/students/", json={"name": "Update Test", "email": "update@test.com", "year": 1})

    student_id = create.json()["id"]

    response = client.put(
        f"/students/{student_id}", json={"name": "Updated Name", "email": "updated@test.com", "year": 4}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["year"] == 4


# 5. DELETE + ERROR CASE
def test_delete_and_error():
    create = client.post("/students/", json={"name": "Delete Test", "email": "delete@test.com", "year": 2})

    student_id = create.json()["id"]

    # delete
    response = client.delete(f"/students/{student_id}")
    assert response.status_code == 200

    # verificăm eroare după ștergere
    response = client.get(f"/students/{student_id}")
    assert response.status_code == 404


# 6. DUPLICARE EMAIL
def test_duplicate_email():
    client.post("/students/", json={"name": "Student One", "email": "dup@test.com", "year": 2})

    response = client.post("/students/", json={"name": "Student Two", "email": "dup@test.com", "year": 3})

    assert response.status_code in [400, 409]


# 7.FILTRARE DUPA NUME
def test_filter_by_name():
    client.post("/students/", json={"name": "Ion Popescu", "email": "ion1@test.com", "year": 2})

    client.post("/students/", json={"name": "Maria Ionescu", "email": "maria1@test.com", "year": 3})

    response = client.get("/students/?name=Ion")

    assert response.status_code == 200
    data = response.json()

    assert any("Ion" in s["name"] for s in data)


# 8.PAGINARE
def test_pagination():
    # creează mai mulți studenți
    for i in range(5):
        client.post("/students/", json={"name": f"Student {i}", "email": f"student{i}@test.com", "year": 1})

    response = client.get("/students/?limit=2&offset=0")
    data = response.json()

    assert response.status_code == 200
    assert len(data) <= 2

    response2 = client.get("/students/?limit=2&offset=2")
    data2 = response2.json()

    assert response2.status_code == 200
    assert len(data2) <= 2


# 9.GPA STUDENT CU NOTELE SALE
def test_gpa_with_grades():
    # creează student
    student = client.post("/students/", json={"name": "GPA Student", "email": "gpa@test.com", "year": 3}).json()

    student_id = student["id"]

    # MOCK grades (direct in memory dacă există grades module)
    try:
        from grades.app import data as grades_data

        grades_data.grades_db[1] = {"id": 1, "student_id": student_id, "value": 10}

        grades_data.grades_db[2] = {"id": 2, "student_id": student_id, "value": 8}
    except ImportError:
        pass

    response = client.get(f"/students/{student_id}/gpa")

    assert response.status_code == 200
    data = response.json()
    assert "gpa" in data
    assert data["gpa"] >= 0


# 10.GPA STUDENT FARA NOTELE LA MATERII
def test_gpa_no_grades():
    student = client.post("/students/", json={"name": "No Grades", "email": "nogrades@test.com", "year": 1}).json()

    student_id = student["id"]

    response = client.get(f"/students/{student_id}/gpa")

    assert response.status_code == 200
    assert response.json()["gpa"] == 0
