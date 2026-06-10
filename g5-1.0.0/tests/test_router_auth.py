import pytest
from fastapi.testclient import TestClient
from main import app
from auth import data as db


@pytest.fixture
def client():
    """Fixture pentru TestClient care va fi folosit in fiecare test."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_auth_db():
    """Fixture care reseteaza baza de date de autentificare inaintea fiecarui test."""
    db.users_db.clear()
    db.next_id = 1
    yield
    db.users_db.clear()
    db.next_id = 1


# ========================
# TESTE PENTRU REGISTER
# ========================


def test_register_success(client):
    """Test: Inregistrare cu parametrii valizi."""
    response = client.post(
        "/auth/register",
        params={"username": "ion", "password": "pass123", "role": "student"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "ion"
    assert data["role"] == "student"
    assert "id" in data
    assert data["id"] == 1


def test_register_default_role(client):
    """Test: Inregistrare fara specificarea rolului (ar trebui sa foloseasca default)."""
    response = client.post("/auth/register", params={"username": "maria", "password": "pass456"})

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "maria"
    assert data["role"] == "user"


def test_register_duplicate_user(client):
    """Test: Tentativa de re-inregistrare cu acelasi utilizator."""
    # Prima inregistrare
    response1 = client.post(
        "/auth/register",
        params={"username": "alex", "password": "pass789", "role": "professor"},
    )
    assert response1.status_code == 201

    # A doua inregistrare cu acelasi username
    response2 = client.post(
        "/auth/register",
        params={"username": "alex", "password": "altaparola", "role": "student"},
    )
    assert response2.status_code == 409
    data = response2.json()
    assert data["detail"] == "Utilizatorul exista deja"


# ========================
# TESTE PENTRU LOGIN
# ========================


def test_login_success(client):
    """Test: Autentificare reusita cu credentiale corecte."""
    # Inregistrare inaintea
    client.post(
        "/auth/register",
        params={"username": "user1", "password": "parola123", "role": "student"},
    )

    # Login
    response = client.post("/auth/login", params={"username": "user1", "password": "parola123"})

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["role"] == "student"
    assert "Login reusit" in data.get("message", "")


def test_login_wrong_password(client):
    """Test: Logare esuata cu parola incorecta."""
    # Inregistrare
    client.post(
        "/auth/register",
        params={"username": "user2", "password": "parola123", "role": "professor"},
    )

    # Login cu parola gresita
    response = client.post("/auth/login", params={"username": "user2", "password": "parolagresita"})

    assert response.status_code == 200
    data = response.json()
    assert "Credentiale invalide" in data.get("message", "")
    assert "user_id" not in data


def test_login_nonexistent_user(client):
    """Test: Logare esuata cu utilizator neexistent."""
    response = client.post(
        "/auth/login",
        params={"username": "utilizatornexistent", "password": "oriceparola"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "Credentiale invalide" in data.get("message", "")


# ========================
# TESTE PENTRU ME
# ========================


def test_get_me_success(client):
    """Test: Consultare profil pentru utilizator existent."""
    # Inregistrare
    resp_register = client.post(
        "/auth/register",
        params={"username": "george", "password": "pass999", "role": "student"},
    )
    user_id = resp_register.json()["id"]

    # Get me
    response = client.get(f"/auth/me?user_id={user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "george"
    assert data["role"] == "student"


def test_get_me_nonexistent_user(client):
    """Test: Comportament la cererea pentru utilizator inexistent."""
    response = client.get("/auth/me?user_id=999")

    assert response.status_code == 200
    data = response.json()
    assert "Utilizator negasit" in data.get("message", "")


def test_get_me_invalid_user_id(client):
    """Test: Cerere cu user_id negativ sau invalid."""
    response = client.get("/auth/me?user_id=-1")

    assert response.status_code == 200
    data = response.json()
    assert "Utilizator negasit" in data.get("message", "")


# ========================
# TESTE PENTRU ROLES
# ========================


def test_update_role_success(client):
    """Test: Schimbare rol pentru utilizator prezent in sistem."""
    # Inregistrare
    resp_register = client.post(
        "/auth/register",
        params={"username": "cornel", "password": "pass111", "role": "student"},
    )
    user_id = resp_register.json()["id"]

    # Update role
    response = client.put("/auth/roles", params={"user_id": user_id, "new_role": "professor"})

    assert response.status_code == 200
    data = response.json()
    assert "Rol actualizat" in data.get("message", "")
    assert data["role"] == "professor"
    assert data["user_id"] == user_id


def test_update_role_nonexistent_user(client):
    """Test: Tentativa modificare rol pentru utilizator absent."""
    response = client.put("/auth/roles", params={"user_id": 555, "new_role": "admin"})

    assert response.status_code == 200
    data = response.json()
    assert "Utilizator negasit" in data.get("message", "")


def test_update_role_multiple_roles(client):
    """Test: Actualizare rol de mai multe ori pentru acelasi utilizator."""
    # Inregistrare
    resp = client.post(
        "/auth/register",
        params={"username": "dan", "password": "pass222", "role": "student"},
    )
    user_id = resp.json()["id"]

    # Prima actualizare
    response1 = client.put("/auth/roles", params={"user_id": user_id, "new_role": "professor"})
    assert response1.json()["role"] == "professor"

    # A doua actualizare
    response2 = client.put("/auth/roles", params={"user_id": user_id, "new_role": "admin"})
    assert response2.json()["role"] == "admin"


# ========================
# TESTE PENTRU VERIFY
# ========================


def test_verify_valid_user(client):
    """Test: Verificare pozitiva pentru utilizator valid."""
    # Inregistrare
    resp_register = client.post(
        "/auth/register",
        params={"username": "tudor", "password": "pass333", "role": "student"},
    )
    user_id = resp_register.json()["id"]

    # Verify
    response = client.get(f"/auth/verify?user_id={user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["user_id"] == user_id
    assert data["role"] == "student"


def test_verify_nonexistent_user(client):
    """Test: Verificare pentru identificator inexistent."""
    response = client.get("/auth/verify?user_id=888")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


# ========================
# TESTE PENTRU LISTARE UTILIZATORI
# ========================


def test_list_users_default_pagination(client):
    """Test: Lista paginata implicita fara filtre."""
    client.post(
        "/auth/register",
        params={"username": "ion", "password": "pass123", "role": "student"},
    )
    client.post(
        "/auth/register",
        params={"username": "maria", "password": "pass456", "role": "admin"},
    )

    response = client.get("/auth/users")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert [item["username"] for item in data["items"]] == ["ion", "maria"]
    assert all("password" not in item for item in data["items"])


def test_list_users_filter_by_name(client):
    """Test: Filtrare partiala dupa username."""
    client.post(
        "/auth/register",
        params={"username": "Ionel", "password": "pass123", "role": "student"},
    )
    client.post(
        "/auth/register",
        params={"username": "maria", "password": "pass456", "role": "admin"},
    )

    response = client.get("/auth/users", params={"name": "ion"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["username"] == "Ionel"


def test_list_users_filter_by_role_and_offset(client):
    """Test: Filtrare dupa rol si paginare cu offset."""
    client.post(
        "/auth/register",
        params={"username": "ana1", "password": "pass123", "role": "student"},
    )
    client.post(
        "/auth/register",
        params={"username": "ana2", "password": "pass123", "role": "student"},
    )
    client.post(
        "/auth/register",
        params={"username": "ana3", "password": "pass123", "role": "professor"},
    )

    response = client.get("/auth/users", params={"role": "student", "limit": 1, "offset": 1})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 1
    assert data["offset"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["username"] == "ana2"


def test_list_users_empty_result(client):
    """Test: Lista vida cand filtrele nu returneaza utilizatori."""
    client.post(
        "/auth/register",
        params={"username": "ion", "password": "pass123", "role": "student"},
    )

    response = client.get("/auth/users", params={"name": "xyz"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_users_invalid_limit(client):
    """Test: Validare pentru limit invalid."""
    response = client.get("/auth/users", params={"limit": 0})

    assert response.status_code == 422


def test_verify_after_role_update(client):
    """Test: Verificare dupa actualizarea rolului."""
    # Inregistrare
    resp_register = client.post(
        "/auth/register",
        params={"username": "rares", "password": "pass444", "role": "student"},
    )
    user_id = resp_register.json()["id"]

    # Update role
    client.put("/auth/roles", params={"user_id": user_id, "new_role": "admin"})

    # Verify - ar trebui sa arate rolul nou
    response = client.get(f"/auth/verify?user_id={user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["role"] == "admin"
