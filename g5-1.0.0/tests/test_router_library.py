import pytest
from fastapi.testclient import TestClient
from main import app
import library.app.data as db


@pytest.fixture(autouse=True)
def reset_db():
    # Clear the in-memory database before each test
    db.books_db.clear()
    db.loans_db.clear()
    db.next_book_id = 1
    db.next_loan_id = 1


@pytest.fixture
def client():
    return TestClient(app)


def test_add_book(client):
    response = client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 3}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Clean Code"
    assert data["author"] == "Robert Martin"
    assert data["id"] == 1


def test_get_books(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 3}
    )
    response = client.get("/library/books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Clean Code"


def test_borrow_book(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 3}
    )
    response = client.post("/library/borrow", json={"book_id": 1, "student_id": 42})
    assert response.status_code == 201
    data = response.json()
    assert data["book_id"] == 1
    assert data["student_id"] == 42
    assert data["status"] == "active"


def test_borrow_unavailable(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 1}
    )
    client.post("/library/borrow", json={"book_id": 1, "student_id": 42})
    response = client.post("/library/borrow", json={"book_id": 1, "student_id": 99})
    assert response.status_code == 400


def test_return_book(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 1}
    )
    client.post("/library/borrow", json={"book_id": 1, "student_id": 42})
    response = client.post("/library/return", json={"loan_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "returned"


def test_return_already_returned(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 1}
    )
    client.post("/library/borrow", json={"book_id": 1, "student_id": 42})
    client.post("/library/return", json={"loan_id": 1})
    response = client.post("/library/return", json={"loan_id": 1})
    assert response.status_code == 404


def test_get_availability(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 3}
    )
    client.post("/library/borrow", json={"book_id": 1, "student_id": 42})
    response = client.get("/library/availability/1")
    assert response.status_code == 200
    data = response.json()
    assert data["total_copies"] == 3
    assert data["available_copies"] == 2


def test_student_history(client):
    client.post(
        "/library/books", json={"title": "Clean Code", "author": "Robert Martin", "isbn": "9780132350884", "copies": 3}
    )
    client.post("/library/borrow", json={"book_id": 1, "student_id": 10})
    client.post("/library/borrow", json={"book_id": 1, "student_id": 10})
    response = client.get("/library/student/10/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(loan["student_id"] == 10 for loan in data)


def test_student_history_not_found(client):
    response = client.get("/library/student/999/history")
    assert response.status_code == 404


def test_student_history_invalid_id(client):
    response = client.get("/library/student/0/history")
    assert response.status_code == 422
