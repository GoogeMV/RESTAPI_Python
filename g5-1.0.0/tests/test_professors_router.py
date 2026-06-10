"""
Teste pentru modulul professors.
Acopera CRUD complet si cazuri de eroare de baza.
Aceste teste reflecta comportamentul actual al codului, inainte de
adaugarea validarilor Pydantic. Unele teste vor trebui actualizate
cand se vor introduce restrictiile (ex: email duplicat va deveni 409).
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from professors.app import data as db


client = TestClient(app)


# autouse = True inseamna ca pentru fiecare test rulat se executa codul de mai jos
@pytest.fixture(autouse=True)
def reset_db():
    """Curata baza de date in memorie inainte de fiecare test."""
    db.professors_db.clear()
    db.next_id = 1

    try:
        from students.app import data as stu_data

        stu_data.students_db.clear()
        stu_data.next_id = 1
    except ImportError:
        pass

    try:
        from enrollments.app import data as enr_data

        enr_data.enrollments_db.clear()
        enr_data.next_id = 1
    except ImportError:
        pass

    yield


def _payload(name="Ion Popescu", email="ion@univ.ro", department="Informatica"):
    """Helper pentru a construi rapid un payload de profesor."""
    return {"name": name, "email": email, "department": department}


# ============================================================================
# CREATE
# ============================================================================


def test_create_professor_returns_201_and_data():
    """POST /professors/ creeaza un profesor si returneaza 201 si datele."""
    response = client.post("/professors/", json=_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ion Popescu"
    assert data["email"] == "ion@univ.ro"
    assert data["department"] == "Informatica"
    assert data["id"] == 1


def test_create_professor_assigns_incremental_ids():
    """Profesorii primesc ID-uri incrementale incepand cu 1."""
    r1 = client.post("/professors/", json=_payload(email="a@x.ro"))
    r2 = client.post("/professors/", json=_payload(email="b@x.ro"))

    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


# ============================================================================
# READ
# ============================================================================


def test_list_professors_returns_empty_list_initially():
    """GET /professors/ pe baza goala returneaza lista goala."""
    response = client.get("/professors/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_professor_by_id_returns_correct_data():
    """GET /professors/{id} returneaza profesorul corect."""
    created = client.post("/professors/", json=_payload()).json()

    response = client.get(f"/professors/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_nonexistent_professor_returns_404():
    """GET /professors/{id} cu un ID inexistent returneaza 404."""
    response = client.get("/professors/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ============================================================================
# UPDATE
# ============================================================================


def test_update_professor_modifies_only_sent_fields():
    """PUT /professors/{id} modifica doar campurile trimise."""
    created = client.post("/professors/", json=_payload()).json()

    response = client.put(f"/professors/{created['id']}", json={"department": "Matematica"})

    assert response.status_code == 200
    data = response.json()
    assert data["department"] == "Matematica"
    assert data["name"] == "Ion Popescu"  # nemodificat
    assert data["email"] == "ion@univ.ro"  # nemodificat


def test_update_nonexistent_professor_returns_404():
    response = client.put("/professors/999", json={"name": "X"})

    assert response.status_code == 422


# ============================================================================
# DELETE
# ============================================================================


def test_delete_professor_removes_it():
    """DELETE /professors/{id} sterge profesorul."""
    created = client.post("/professors/", json=_payload()).json()
    prof_id = created["id"]

    delete_response = client.delete(f"/professors/{prof_id}")
    assert delete_response.status_code == 200

    # Confirmam ca a fost sters
    get_response = client.get(f"/professors/{prof_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_professor_returns_404():
    """DELETE pe profesor inexistent returneaza 404."""
    response = client.delete("/professors/999")

    assert response.status_code == 404


# ============================================================================
# VALIDATION - SCHEMAS
# ============================================================================


def test_create_professor_with_invalid_email_returns_422():
    response = client.post("/professors/", json=_payload(email="n-am mail :("))
    assert response.status_code == 422


def test_create_professor_with_short_name_returns_422():
    response = client.post("/professors/", json=_payload(name="X"))
    assert response.status_code == 422


def test_create_professor_with_short_department_returns_422():
    response = client.post("/professors/", json=_payload(department="I"))
    assert response.status_code == 422


def test_create_professor_with_too_long_name_returns_422():
    response = client.post("/professors/", json=_payload(name="A" * 255))
    assert response.status_code == 422


def test_create_professor_with_extra_field_returns_422():
    payload = _payload()
    payload["id"] = "99"  # unknown field
    response = client.post("/professors/", json=payload)
    assert response.status_code == 422


def test_create_professor_strips_whitespace_from_name():
    response = client.post("/professors/", json=_payload(name="  Ion Popescu  "))
    assert response.status_code == 201
    assert response.json()["name"] == "Ion Popescu"


def test_create_professor_strips_whitespace_from_department():
    response = client.post("/professors/", json=_payload(department="  Informatica  "))
    assert response.status_code == 201
    assert response.json()["department"] == "Informatica"


def test_create_professor_with_only_whitespace_name_returns_422():
    response = client.post("/professors/", json=_payload(name="   "))
    assert response.status_code == 422


def test_update_professor_with_invalid_email_returns_422():
    created = client.post("/professors/", json=_payload()).json()
    response = client.put(f"/professors/{created['id']}", json={"email": "ai pierdut dreptul la email OwO"})
    assert response.status_code == 422


def test_update_professor_with_short_name_returns_422():
    created = client.post("/professors/", json=_payload()).json()
    response = client.put(f"/professors/{created['id']}", json={"name": "X"})
    assert response.status_code == 422


def test_update_professor_with_extra_field_returns_422():
    created = client.post("/professors/", json=_payload()).json()
    response = client.put(f"/professors/{created['id']}", json={"unknown_field": "value"})
    assert response.status_code == 422


# ============================================================================
# VALIDATION - EMAIL UNIQUENESS
# ============================================================================


def test_create_professor_with_duplicate_email_returns_409():
    client.post("/professors/", json=_payload())
    response = client.post("/professors/", json=_payload(name="Profesor Unu"))
    assert response.status_code == 409
    assert "email" in response.json()["detail"].lower()


def test_update_professor_with_duplicate_email_returns_409():
    client.post("/professors/", json=_payload(email="a@univ.ro"))
    second = client.post("/professors/", json=_payload(email="b@univ.ro", name="Profesor Doi")).json()

    response = client.put(f"/professors/{second['id']}", json={"email": "a@univ.ro"})
    assert response.status_code == 409


def test_update_professor_with_own_email_succeeds():
    created = client.post("/professors/", json=_payload()).json()
    response = client.put(f"/professors/{created['id']}", json={"email": created["email"], "name": "Nume Nou"})
    assert response.status_code == 200
    assert response.json()["name"] == "Nume Nou"


def test_create_professor_after_delete_allows_email_reuse():
    first = client.post("/professors/", json=_payload()).json()
    client.delete(f"/professors/{first['id']}")

    response = client.post("/professors/", json=_payload())
    assert response.status_code == 201


# ============================================================================
# PAGINATION
# ============================================================================


def _create_n_professors(n: int):
    for i in range(n):
        client.post(
            "/professors/",
            json={
                "name": f"Profesor {i}",
                "email": f"prof{i}@univ.ro",
                "department": "Informatica",
            },
        )


def test_list_default_limit_is_10():
    _create_n_professors(15)
    r = client.get("/professors/")
    assert r.status_code == 200
    assert len(r.json()) == 10


def test_list_respects_custom_limit():
    _create_n_professors(15)
    r = client.get("/professors/?limit=5")
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_list_respects_offset():
    _create_n_professors(15)
    r = client.get("/professors/?limit=5&offset=10")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    assert data[0]["name"] == "Profesor 10"


def test_list_offset_beyond_total_returns_empty():
    _create_n_professors(5)
    r = client.get("/professors/?offset=100")
    assert r.status_code == 200
    assert r.json() == []


def test_list_invalid_limit_zero_returns_422():
    r = client.get("/professors/?limit=0")
    assert r.status_code == 422


def test_list_invalid_limit_negative_returns_422():
    r = client.get("/professors/?limit=-5")
    assert r.status_code == 422


def test_list_invalid_limit_too_large_returns_422():
    r = client.get("/professors/?limit=101")
    assert r.status_code == 422


def test_list_invalid_offset_negative_returns_422():
    r = client.get("/professors/?offset=-1")
    assert r.status_code == 422


# ============================================================================
# FILTERING
# ============================================================================


def test_filter_by_name_substring():
    client.post("/professors/", json={"name": "Ion Popescu", "email": "ion@univ.ro", "department": "Informatica"})
    client.post("/professors/", json={"name": "Maria Ionescu", "email": "maria@univ.ro", "department": "Matematica"})
    client.post("/professors/", json={"name": "Vasile Georgescu", "email": "vasile@univ.ro", "department": "Fizica"})

    r = client.get("/professors/?name=ion")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    names = {p["name"] for p in data}
    assert names == {"Ion Popescu", "Maria Ionescu"}


def test_filter_by_name_case_insensitive():
    client.post("/professors/", json={"name": "Ion Popescu", "email": "ion@univ.ro", "department": "Informatica"})
    r = client.get("/professors/?name=ION")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_filter_by_department():
    client.post("/professors/", json={"name": "Ion Popescu", "email": "ion@univ.ro", "department": "Informatica"})
    client.post("/professors/", json={"name": "Maria Ionescu", "email": "maria@univ.ro", "department": "Matematica"})

    r = client.get("/professors/?department=Informatica")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["name"] == "Ion Popescu"


def test_filter_by_email():
    client.post("/professors/", json={"name": "Ion Popescu", "email": "ion@univ.ro", "department": "Informatica"})
    client.post("/professors/", json={"name": "Maria Ionescu", "email": "maria@cti.ro", "department": "Matematica"})

    r = client.get("/professors/?email=univ.ro")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["email"] == "ion@univ.ro"


def test_filter_no_match_returns_empty():
    client.post("/professors/", json={"name": "Ion Popescu", "email": "ion@univ.ro", "department": "Informatica"})
    r = client.get("/professors/?name=inexistent")
    assert r.status_code == 200
    assert r.json() == []


def test_filters_are_combined_with_and():
    client.post("/professors/", json={"name": "Ion Popescu", "email": "ion@univ.ro", "department": "Informatica"})
    client.post("/professors/", json={"name": "Ion Vasilescu", "email": "ionv@univ.ro", "department": "Matematica"})
    r = client.get("/professors/?name=ion&department=Informatica")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["name"] == "Ion Popescu"


# ============================================================================
# FILTERING + PAGINATION
# ============================================================================


def test_filter_then_paginate():
    for i in range(12):
        client.post(
            "/professors/",
            json={
                "name": f"Profesor Info {i}",
                "email": f"info{i}@univ.ro",
                "department": "Informatica",
            },
        )
    for i in range(3):
        client.post(
            "/professors/",
            json={
                "name": f"Profesor Mate {i}",
                "email": f"mate{i}@univ.ro",
                "department": "Matematica",
            },
        )
    r = client.get("/professors/?department=Informatica&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    assert all(p["department"] == "Informatica" for p in data)


# ============================================================================
# GET /professors/{id}/students
# ============================================================================


def _setup_professor_with_students(num_students: int = 3, num_extra_enrollments: int = 0):
    from students.app import data as stu_data
    from enrollments.app import data as enr_data

    prof_resp = client.post(
        "/professors/",
        json={
            "name": "Prof Test",
            "email": "test@univ.ro",
            "department": "Informatica",
        },
    )
    professor_id = prof_resp.json()["id"]

    student_ids = []
    for i in range(num_students):
        sid = stu_data.next_id
        stu_data.students_db[sid] = {
            "id": sid,
            "name": f"Student {i}",
            "email": f"stud{i}@univ.ro",
            "year": 2,
        }
        stu_data.next_id += 1
        student_ids.append(sid)

        eid = enr_data.next_id
        enr_data.enrollments_db[eid] = {
            "id": eid,
            "student_id": sid,
            "professor_id": professor_id,
            "course_name": f"Curs {i}",
        }
        enr_data.next_id += 1

    for i in range(num_extra_enrollments):
        eid = enr_data.next_id
        enr_data.enrollments_db[eid] = {
            "id": eid,
            "student_id": student_ids[i % num_students],
            "professor_id": professor_id,
            "course_name": f"Curs extra {i}",
        }
        enr_data.next_id += 1

    return professor_id, student_ids


def test_get_professor_students_returns_list_of_students():
    professor_id, student_ids = _setup_professor_with_students(num_students=3)
    r = client.get(f"/professors/{professor_id}/students")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 3
    assert all("name" in s and "email" in s for s in data)
    assert {s["id"] for s in data} == set(student_ids)


def test_get_professor_students_deduplicates():
    professor_id, _ = _setup_professor_with_students(num_students=3, num_extra_enrollments=2)
    r = client.get(f"/professors/{professor_id}/students")
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_get_professor_students_empty_when_no_enrollments():
    prof_resp = client.post(
        "/professors/",
        json={
            "name": "Prof Singur",
            "email": "singur@univ.ro",
            "department": "Fizica",
        },
    )
    professor_id = prof_resp.json()["id"]
    r = client.get(f"/professors/{professor_id}/students")
    assert r.status_code == 200
    assert r.json() == []


def test_get_professor_students_404_when_professor_not_found():
    r = client.get("/professors/99999/students")
    assert r.status_code == 404


def test_get_professor_students_respects_pagination():
    professor_id, _ = _setup_professor_with_students(num_students=15)
    r = client.get(f"/professors/{professor_id}/students?limit=5&offset=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5


def test_get_professor_students_invalid_limit_returns_422():
    prof_resp = client.post(
        "/professors/",
        json={
            "name": "Prof Test 2",
            "email": "test2@univ.ro",
            "department": "Mate",
        },
    )
    professor_id = prof_resp.json()["id"]
    r = client.get(f"/professors/{professor_id}/students?limit=0")
    assert r.status_code == 422
