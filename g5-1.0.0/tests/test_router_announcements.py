import pytest
from fastapi.testclient import TestClient
from main import app
from announcements.app import data as db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    db.announcements_db.clear()
    db.next_id = 1
    yield


def _payload(title="Anunt important", content="Continut anunt", author="Admin", target_audience="students"):
    return {"title": title, "content": content, "author": author, "target_audience": target_audience}


def test_list_announcements_returns_empty_list_initially():
    response = client.get("/announcements/")

    assert response.status_code == 200
    assert response.json() == []


def test_create_announcement_returns_201_and_data():
    response = client.post("/announcements/", json=_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Anunt important"
    assert data["content"] == "Continut anunt"
    assert data["author"] == "Admin"
    assert data["target_audience"] == "students"
    assert data["status"] == "active"


def test_create_announcement_assigns_incremental_ids():
    r1 = client.post("/announcements/", json=_payload(title="Anunt A"))
    r2 = client.post("/announcements/", json=_payload(title="Anunt B"))

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["id"] == 1
    assert r2.json()["id"] == 2


def test_get_announcement_by_id_returns_correct_data():
    created = client.post("/announcements/", json=_payload()).json()

    response = client.get(f"/announcements/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_nonexistent_announcement_returns_404():
    response = client.get("/announcements/999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_announcements_by_audience_returns_only_matching_items():
    client.post("/announcements/", json=_payload(title="Studenti", target_audience="students"))
    client.post("/announcements/", json=_payload(title="Profesori", target_audience="professors"))

    response = client.get("/announcements/audience/students")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Studenti"
    assert data[0]["target_audience"] == "students"


def test_update_announcement_modifies_only_sent_fields():
    created = client.post("/announcements/", json=_payload()).json()

    response = client.put(f"/announcements/{created['id']}", json={"title": "Titlu modificat"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Titlu modificat"
    assert data["content"] == "Continut anunt"
    assert data["author"] == "Admin"
    assert data["target_audience"] == "students"


def test_update_nonexistent_announcement_returns_404():
    response = client.put("/announcements/999", json={"title": "Titlu valid"})

    assert response.status_code == 404


def test_delete_announcement_removes_it():
    created = client.post("/announcements/", json=_payload()).json()
    ann_id = created["id"]

    delete_response = client.delete(f"/announcements/{ann_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Announcement deleted"

    get_response = client.get(f"/announcements/{ann_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_announcement_returns_404():
    response = client.delete("/announcements/999")

    assert response.status_code == 404


def test_archive_announcement_updates_status():
    created = client.post("/announcements/", json=_payload()).json()

    response = client.post(f"/announcements/{created['id']}/archive")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["status"] == "archived"


def test_archive_nonexistent_announcement_returns_404():
    response = client.post("/announcements/999/archive")

    assert response.status_code == 404
    assert response.json()["detail"] == "Announcement not found"


def test_summary_counts_announcements_audiences_authors_and_statuses():
    client.post(
        "/announcements/",
        json=_payload(title="Studenti", author="Admin", target_audience="Students"),
    )
    archived = client.post(
        "/announcements/",
        json=_payload(title="Profesori", author="admin", target_audience="professors"),
    ).json()
    client.post(
        "/announcements/",
        json=_payload(title="General", author="Secretariat", target_audience="students"),
    )
    client.post(f"/announcements/{archived['id']}/archive")

    response = client.get("/announcements/stats/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total": 3,
        "audiences": 2,
        "authors": 2,
        "archived": 1,
        "active": 2,
    }


def test_get_announcements_by_author_supports_exact_case_insensitive_and_partial_matches():
    client.post("/announcements/", json=_payload(title="Admin", author="Admin Principal"))
    client.post("/announcements/", json=_payload(title="Secretariat", author="Secretariat"))

    exact_response = client.get("/announcements/authors/Secretariat")
    case_response = client.get("/announcements/authors/admin principal")
    partial_response = client.get("/announcements/authors/secret")

    assert exact_response.status_code == 200
    assert case_response.status_code == 200
    assert partial_response.status_code == 200
    assert [ann["author"] for ann in exact_response.json()] == ["Secretariat"]
    assert [ann["author"] for ann in case_response.json()] == ["Admin Principal"]
    assert [ann["author"] for ann in partial_response.json()] == ["Secretariat"]


def test_get_announcements_by_unknown_author_returns_empty_list():
    client.post("/announcements/", json=_payload(author="Admin"))

    response = client.get("/announcements/authors/Nobody")

    assert response.status_code == 200
    assert response.json() == []


def test_search_announcements_by_title_content_and_case_insensitive_keyword():
    client.post(
        "/announcements/",
        json=_payload(
            title="Examen programare",
            content="Detalii obisnuite pentru studenti",
        ),
    )
    client.post(
        "/announcements/",
        json=_payload(
            title="Anunt general",
            content="Restanta la matematica",
        ),
    )

    title_response = client.get("/announcements/search/programare")
    content_response = client.get("/announcements/search/matematica")
    case_response = client.get("/announcements/search/EXAMEN")

    assert title_response.status_code == 200
    assert content_response.status_code == 200
    assert case_response.status_code == 200
    assert [ann["title"] for ann in title_response.json()] == ["Examen programare"]
    assert [ann["title"] for ann in content_response.json()] == ["Anunt general"]
    assert [ann["title"] for ann in case_response.json()] == ["Examen programare"]


def test_search_announcements_unknown_keyword_returns_empty_list():
    client.post("/announcements/", json=_payload(title="Anunt general"))

    response = client.get("/announcements/search/inexistent")

    assert response.status_code == 200
    assert response.json() == []


def test_delete_announcements_by_audience_removes_only_matching_items():
    client.post("/announcements/", json=_payload(title="Studenti A", target_audience="students"))
    client.post("/announcements/", json=_payload(title="Studenti B", target_audience="Students"))
    client.post("/announcements/", json=_payload(title="Profesori", target_audience="professors"))

    response = client.delete("/announcements/audience/STUDENTS")

    assert response.status_code == 200
    assert response.json() == {"message": "Announcements deleted", "deleted_count": 2}

    remaining = client.get("/announcements/").json()
    assert len(remaining) == 1
    assert remaining[0]["target_audience"] == "professors"


def test_delete_announcements_by_missing_audience_returns_404():
    client.post("/announcements/", json=_payload(target_audience="students"))

    response = client.delete("/announcements/audience/professors")

    assert response.status_code == 404
    assert response.json()["detail"] == "No announcements found for this audience"


def test_create_announcement_with_short_title_returns_422():
    response = client.post("/announcements/", json=_payload(title="A"))

    assert response.status_code == 422


def test_create_announcement_with_short_content_returns_422():
    response = client.post("/announcements/", json=_payload(content="Mic"))

    assert response.status_code == 422


def test_create_announcement_with_short_author_returns_422():
    response = client.post("/announcements/", json=_payload(author="A"))

    assert response.status_code == 422


def test_create_announcement_with_short_target_audience_returns_422():
    response = client.post("/announcements/", json=_payload(target_audience="x"))

    assert response.status_code == 422


def test_update_announcement_with_short_title_returns_422():
    created = client.post("/announcements/", json=_payload()).json()

    response = client.put(f"/announcements/{created['id']}", json={"title": "A"})

    assert response.status_code == 422


def test_update_announcement_with_short_content_returns_422():
    created = client.post("/announcements/", json=_payload()).json()

    response = client.put(f"/announcements/{created['id']}", json={"content": "Mic"})

    assert response.status_code == 422


def test_list_announcements_supports_pagination():
    client.post("/announcements/", json=_payload(title="Anunt A"))
    client.post("/announcements/", json=_payload(title="Anunt B"))
    client.post("/announcements/", json=_payload(title="Anunt C"))

    response = client.get("/announcements/?limit=2&offset=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Anunt B"
    assert data[1]["title"] == "Anunt C"


def test_list_announcements_rejects_invalid_pagination():
    response = client.get("/announcements/?limit=0&offset=-1")

    assert response.status_code == 422


def test_list_announcements_filters_by_target_audience():
    client.post("/announcements/", json=_payload(title="Studenti", target_audience="students"))
    client.post("/announcements/", json=_payload(title="Profesori", target_audience="professors"))

    response = client.get("/announcements/?target_audience=students")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Studenti"


def test_list_announcements_filters_by_author():
    client.post("/announcements/", json=_payload(title="Admin title", author="Admin"))
    client.post("/announcements/", json=_payload(title="Secretariat title", author="Secretariat"))

    response = client.get("/announcements/?author=secret")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author"] == "Secretariat"


def test_list_announcements_searches_title_and_content():
    client.post(
        "/announcements/",
        json=_payload(
            title="Examen programare",
            content="Detalii normale despre curs",
        ),
    )
    client.post(
        "/announcements/",
        json=_payload(
            title="Anunt general",
            content="Restanta la matematica",
        ),
    )

    response = client.get("/announcements/?search=matematica")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Anunt general"
