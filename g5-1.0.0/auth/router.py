from fastapi import APIRouter, Depends, HTTPException, Query, status
from auth import data as db
from auth.schemas import LoginRequest, UserCreate, UserListResponse

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
def list_users(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    name: str | None = None,
    role: str | None = None,
):
    users = sorted(db.users_db.values(), key=lambda user: user["id"])

    if name is not None:
        needle = name.casefold()
        users = [user for user in users if needle in user["username"].casefold()]

    if role is not None:
        users = [user for user in users if user["role"] == role]

    total = len(users)
    page = users[offset : offset + limit]

    return {
        "items": [{"id": user["id"], "username": user["username"], "role": user["role"]} for user in page],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/register", status_code=201)
def register(payload: UserCreate = Depends()):
    username = payload.username
    password = payload.password
    role = payload.role

    for user in db.users_db.values():
        if user["username"] == username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Utilizatorul exista deja",
            )

    user = {"id": db.next_id, "username": username, "password": password, "role": role}
    db.users_db[db.next_id] = user
    db.next_id += 1
    return {"id": user["id"], "username": username, "role": role}


@router.post("/login")
def login(payload: LoginRequest = Depends()):
    username = payload.username
    password = payload.password
    for user in db.users_db.values():
        if user["username"] == username and user["password"] == password:
            return {
                "message": "Login reusit",
                "user_id": user["id"],
                "role": user["role"],
            }
    return {"message": "Credentiale invalide"}


@router.get("/me")
def get_me(user_id: int):
    if user_id in db.users_db:
        u = db.users_db[user_id]
        return {"id": u["id"], "username": u["username"], "role": u["role"]}
    return {"message": "Utilizator negasit"}


@router.put("/roles")
def update_role(user_id: int, new_role: str):
    if user_id in db.users_db:
        db.users_db[user_id]["role"] = new_role
        return {"message": "Rol actualizat", "user_id": user_id, "role": new_role}
    return {"message": "Utilizator negasit"}


@router.get("/verify")
def verify(user_id: int):
    if user_id in db.users_db:
        return {"valid": True, "user_id": user_id, "role": db.users_db[user_id]["role"]}
    return {"valid": False}
