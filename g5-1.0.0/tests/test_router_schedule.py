"""
Teste pentru modulul schedule.
Acopera CRUD complet, validari, detectare conflicte, filtrare/paginare
si endpoint-ul GET /schedule/professor/{professor_id}.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from schedule.app import data as db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Curata baza de date in memorie inainte de fiecare test."""
    db.schedule_db.clear()
    db.next_id = 1
    yield


def _payload(
    course_name="Algoritmi",
    professor_id=1,
    room="A101",
    day="Luni",
    start_time="08:00",
    end_time="10:00",
):
    """Helper pentru a construi rapid un payload de slot."""
    return {
        "course_name": course_name,
        "professor_id": professor_id,
        "room": room,
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
    }


# ============================================================================
# CREATE
# ============================================================================


def test_create_slot_returns_201_and_data():
    """POST /schedule/ creeaza un slot si returneaza 201 si datele corecte."""
    response = client.post("/schedule/", json=_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["course_name"] == "Algoritmi"
    assert data["professor_id"] == 1
    assert data["room"] == "A101"
    assert data["day"] == "Luni"
    assert data["start_time"] == "08:00"
    assert data["end_time"] == "10:00"
    assert data["id"] == 1


def test_create_slot_assigns_incremental_ids():
    """Sloturile primesc ID-uri incrementale incepand cu 1."""
    r1 = client.post("/schedule/", json=_payload(start_time="08:00", end_time="10:00"))
    r2 = client.post("/schedule/", json=_payload(start_time="10:00", end_time="12:00"))

    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


# ============================================================================
# READ
# ============================================================================


def test_list_slots_returns_empty_list_initially():
    """GET /schedule/ pe baza goala returneaza lista goala."""
    response = client.get("/schedule/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_slot_by_id_returns_correct_data():
    """GET /schedule/{id} returneaza slotul corect."""
    created = client.post("/schedule/", json=_payload()).json()

    response = client.get(f"/schedule/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_nonexistent_slot_returns_404():
    """GET /schedule/{id} cu un ID inexistent returneaza 404."""
    response = client.get("/schedule/999")

    assert response.status_code == 404


# ============================================================================
# UPDATE
# ============================================================================


def test_update_slot_modifies_only_sent_fields():
    """PUT /schedule/{id} modifica doar campurile trimise."""
    created = client.post("/schedule/", json=_payload()).json()

    response = client.put(f"/schedule/{created['id']}", json={"room": "B202"})

    assert response.status_code == 200
    data = response.json()
    assert data["room"] == "B202"
    assert data["course_name"] == "Algoritmi"  # nemodificat
    assert data["day"] == "Luni"  # nemodificat


def test_update_nonexistent_slot_returns_404():
    """PUT /schedule/{id} cu ID inexistent returneaza 404."""
    response = client.put("/schedule/999", json={"room": "B202"})

    assert response.status_code == 404


# ============================================================================
# DELETE
# ============================================================================


def test_delete_slot_removes_it():
    """DELETE /schedule/{id} sterge slotul."""
    created = client.post("/schedule/", json=_payload()).json()
    slot_id = created["id"]

    delete_response = client.delete(f"/schedule/{slot_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/schedule/{slot_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_slot_returns_404():
    """DELETE pe slot inexistent returneaza 404."""
    response = client.delete("/schedule/999")

    assert response.status_code == 404


# ============================================================================
# VALIDATION
# ============================================================================


def test_create_slot_with_short_course_name_returns_422():
    """course_name cu mai putin de 3 caractere este respins."""
    response = client.post("/schedule/", json=_payload(course_name="AB"))

    assert response.status_code == 422


def test_create_slot_with_invalid_day_returns_422():
    """Ziua invalida (ex: Sambata) este respinsa."""
    response = client.post("/schedule/", json=_payload(day="Sambata"))

    assert response.status_code == 422


def test_create_slot_with_invalid_time_format_returns_422():
    """Format de timp invalid (ex: 8:00) este respins."""
    response = client.post("/schedule/", json=_payload(start_time="8:00"))

    assert response.status_code == 422


def test_create_slot_with_end_before_start_returns_422():
    """end_time inainte de start_time este respins."""
    response = client.post("/schedule/", json=_payload(start_time="10:00", end_time="08:00"))

    assert response.status_code == 422


def test_create_slot_with_equal_times_returns_422():
    """start_time egal cu end_time este respins."""
    response = client.post("/schedule/", json=_payload(start_time="10:00", end_time="10:00"))

    assert response.status_code == 422


def test_create_slot_with_negative_professor_id_returns_422():
    """professor_id negativ este respins."""
    response = client.post("/schedule/", json=_payload(professor_id=-1))

    assert response.status_code == 422


def test_create_slot_with_empty_room_returns_422():
    """Sala goala este respinsa."""
    response = client.post("/schedule/", json=_payload(room=""))

    assert response.status_code == 422


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================


def test_create_duplicate_slot_returns_409():
    """Acelasi professor_id + room + day + start_time returneaza 409."""
    client.post("/schedule/", json=_payload())
    response = client.post("/schedule/", json=_payload(course_name="Alt Curs"))

    assert response.status_code == 409


def test_create_slot_same_professor_different_room_is_allowed():
    """Acelasi profesor in alta sala la aceeasi ora este permis."""
    client.post("/schedule/", json=_payload(room="A101"))
    response = client.post("/schedule/", json=_payload(room="B202"))

    assert response.status_code == 201


def test_create_slot_same_room_different_time_is_allowed():
    """Aceeasi sala la ore diferite este permisa."""
    client.post("/schedule/", json=_payload(start_time="08:00", end_time="10:00"))
    response = client.post("/schedule/", json=_payload(start_time="10:00", end_time="12:00"))

    assert response.status_code == 201


# ============================================================================
# CONFLICTS
# ============================================================================


def test_conflicts_returns_empty_when_no_overlap():
    """GET /schedule/conflicts returneaza lista goala fara suprapuneri."""
    client.post("/schedule/", json=_payload(start_time="08:00", end_time="10:00"))
    client.post("/schedule/", json=_payload(start_time="10:00", end_time="12:00"))

    response = client.get("/schedule/conflicts")

    assert response.status_code == 200
    assert response.json() == []


def test_conflicts_detects_overlapping_slots():
    """GET /schedule/conflicts detecteaza doua sloturi care se suprapun in aceeasi sala."""
    client.post("/schedule/", json=_payload(professor_id=1, start_time="08:00", end_time="10:00"))
    client.post(
        "/schedule/",
        json=_payload(professor_id=2, start_time="09:00", end_time="11:00"),
    )

    response = client.get("/schedule/conflicts")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_conflicts_ignores_different_rooms():
    """Suprapunere de timp in sali diferite nu este conflict."""
    client.post("/schedule/", json=_payload(room="A101", professor_id=1))
    client.post("/schedule/", json=_payload(room="B202", professor_id=2))

    response = client.get("/schedule/conflicts")

    assert response.status_code == 200
    assert response.json() == []


# ============================================================================
# GET /schedule/professor/{professor_id}
# ============================================================================


def test_get_slots_by_professor_returns_correct_slots():
    """GET /schedule/professor/{id} returneaza toate sloturile profesorului."""
    client.post("/schedule/", json=_payload(professor_id=5, start_time="08:00", end_time="10:00"))
    client.post("/schedule/", json=_payload(professor_id=5, day="Marti", start_time="10:00", end_time="12:00"))
    client.post("/schedule/", json=_payload(professor_id=9, start_time="08:00", end_time="10:00", room="B202"))

    response = client.get("/schedule/professor/5")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(slot["professor_id"] == 5 for slot in data)


def test_get_slots_by_professor_returns_empty_list_when_no_slots():
    """GET /schedule/professor/{id} returneaza [] daca profesorul nu are sloturi."""
    response = client.get("/schedule/professor/99")

    assert response.status_code == 200
    assert response.json() == []


def test_get_slots_by_professor_returns_all_without_pagination_limit():
    """GET /schedule/professor/{id} returneaza toate sloturile, nu doar primele 10."""
    for i in range(15):
        client.post(
            "/schedule/",
            json=_payload(
                professor_id=7,
                day="Luni"
                if i % 5 == 0
                else "Marti"
                if i % 5 == 1
                else "Miercuri"
                if i % 5 == 2
                else "Joi"
                if i % 5 == 3
                else "Vineri",
                room=f"S{i + 1:03}",
                start_time="08:00",
                end_time="10:00",
            ),
        )

    response = client.get("/schedule/professor/7")

    assert response.status_code == 200
    assert len(response.json()) == 15


# ============================================================================
# FILTERING
# ============================================================================


def test_filter_by_day():
    """GET /schedule/?day=Luni returneaza doar sloturile de luni."""
    client.post("/schedule/", json=_payload(day="Luni"))
    client.post("/schedule/", json=_payload(day="Marti", room="B202"))

    response = client.get("/schedule/?day=Luni")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["day"] == "Luni"


def test_filter_by_room():
    """GET /schedule/?room=A101 returneaza doar sloturile din sala A101."""
    client.post("/schedule/", json=_payload(room="A101"))
    client.post("/schedule/", json=_payload(room="B202", start_time="10:00", end_time="12:00"))

    response = client.get("/schedule/?room=A101")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["room"] == "A101"


def test_filter_by_professor_id():
    """GET /schedule/?professor_id=3 returneaza doar sloturile profesorului 3."""
    client.post("/schedule/", json=_payload(professor_id=3))
    client.post("/schedule/", json=_payload(professor_id=7, room="B202"))

    response = client.get("/schedule/?professor_id=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["professor_id"] == 3


# ============================================================================
# PAGINATION
# ============================================================================


def _create_n_slots(n: int):
    days = ["Luni", "Marti", "Miercuri", "Joi", "Vineri"]
    for i in range(n):
        client.post(
            "/schedule/",
            json=_payload(
                course_name=f"Curs {i}",
                professor_id=i + 1,
                room=f"S{i + 1:03}",
                day=days[i % 5],
                start_time="08:00",
                end_time="10:00",
            ),
        )


def test_list_default_limit_is_10():
    """Fara parametri, GET /schedule/ returneaza maxim 10 rezultate."""
    _create_n_slots(15)
    response = client.get("/schedule/")

    assert response.status_code == 200
    assert len(response.json()) == 10


def test_list_respects_custom_limit():
    """?limit=5 returneaza cel mult 5 rezultate."""
    _create_n_slots(15)
    response = client.get("/schedule/?limit=5")

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_list_respects_offset():
    """?limit=5&offset=10 returneaza urmatoarele 5 dupa primele 10."""
    _create_n_slots(15)
    all_slots = client.get("/schedule/?limit=100").json()
    response = client.get("/schedule/?limit=5&offset=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["id"] == all_slots[10]["id"]


def test_list_offset_beyond_total_returns_empty():
    """Offset mai mare decat totalul returneaza lista goala."""
    _create_n_slots(5)
    response = client.get("/schedule/?offset=100")

    assert response.status_code == 200
    assert response.json() == []


def test_list_invalid_limit_zero_returns_422():
    """limit=0 este invalid si returneaza 422."""
    response = client.get("/schedule/?limit=0")

    assert response.status_code == 422


def test_list_invalid_limit_too_large_returns_422():
    """limit>100 este invalid si returneaza 422."""
    response = client.get("/schedule/?limit=101")

    assert response.status_code == 422


def test_list_invalid_offset_negative_returns_422():
    """offset negativ este invalid si returneaza 422."""
    response = client.get("/schedule/?offset=-1")

    assert response.status_code == 422
