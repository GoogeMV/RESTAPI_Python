import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from materials.app import data as db
from materials.app.router import router


@pytest.fixture(autouse=True)
def reset_materials_db():
    db.materials_db.clear()
    db.next_id = 1


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router, prefix="/materials")
    return TestClient(app)


def create_sample_material(client):
    response = client.post(
        "/materials/",
        json={
            "course_name": "Programare Python",
            "title": "Introducere in FastAPI",
            "content": "Material despre construirea unui REST API cu FastAPI.",
            "file_url": "https://example.com/fastapi.pdf",
        },
    )

    return response


def test_create_material(client):
    response = create_sample_material(client)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["course_name"] == "Programare Python"
    assert data["title"] == "Introducere in FastAPI"
    assert data["content"] == "Material despre construirea unui REST API cu FastAPI."
    assert data["file_url"] == "https://example.com/fastapi.pdf"


def test_get_material_by_id(client):
    create_sample_material(client)

    response = client.get("/materials/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["course_name"] == "Programare Python"
    assert data["title"] == "Introducere in FastAPI"


def test_list_materials_with_pagination(client):
    create_sample_material(client)

    client.post(
        "/materials/",
        json={
            "course_name": "Algoritmi",
            "title": "Algoritmi de sortare",
            "content": "Material despre bubble sort, merge sort si quick sort.",
            "file_url": None,
        },
    )

    response = client.get("/materials/?limit=1&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == 1


def test_update_material(client):
    create_sample_material(client)

    response = client.put(
        "/materials/1",
        json={
            "title": "FastAPI actualizat",
            "content": "Continut actualizat pentru materialul despre FastAPI.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "FastAPI actualizat"
    assert data["content"] == "Continut actualizat pentru materialul despre FastAPI."
    assert data["course_name"] == "Programare Python"


def test_delete_material(client):
    create_sample_material(client)

    delete_response = client.delete("/materials/1")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Material deleted successfully"}

    get_response = client.get("/materials/1")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Material not found"}


def test_get_missing_material_returns_404(client):
    response = client.get("/materials/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}


def test_create_duplicate_material_returns_409(client):
    create_sample_material(client)

    response = client.post(
        "/materials/",
        json={
            "course_name": "programare python",
            "title": "introducere in fastapi",
            "content": "Alt continut pentru acelasi material.",
            "file_url": None,
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Material already exists for this course"}


def test_create_invalid_material_returns_422(client):
    response = client.post(
        "/materials/",
        json={
            "course_name": "A",
            "title": "AB",
            "content": "1234",
            "file_url": "invalid-url",
        },
    )

    assert response.status_code == 422


def test_search_materials(client):
    create_sample_material(client)

    response = client.get("/materials/search?q=fastapi&limit=10&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Introducere in FastAPI"


def test_search_materials_not_found_returns_404(client):
    create_sample_material(client)

    response = client.get("/materials/search?q=java")

    assert response.status_code == 404
    assert response.json() == {"detail": "No materials found for this search query"}


def test_filter_materials_by_course(client):
    create_sample_material(client)

    response = client.get("/materials/course/programare%20python?limit=10&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["course_name"] == "Programare Python"
