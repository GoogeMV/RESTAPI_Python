from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    name: str = Field(min_length=3, description="Student name must have at least 3 characters")
    email: EmailStr
    year: int = Field(ge=1, le=6, description="Year must be between 1 and 6")


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3)
    email: EmailStr | None = None
    year: int | None = Field(default=None, ge=1, le=6)


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    year: int
