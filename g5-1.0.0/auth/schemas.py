from typing import Literal

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    role: Literal["user", "student", "professor", "admin"] = "user"


class UserResponse(BaseModel):
    id: int
    username: str
    role: str


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class LoginResponse(BaseModel):
    message: str
    user_id: int | None = None
    role: str | None = None
