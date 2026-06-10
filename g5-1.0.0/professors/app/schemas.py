from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class ProfessorBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfessorCreate(ProfessorBase):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    department: str = Field(min_length=2, max_length=100)

    @field_validator("name", "department", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class ProfessorUpdate(ProfessorBase):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    department: str | None = Field(default=None, min_length=2, max_length=100)

    @field_validator("name", "department", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class ProfessorResponse(ProfessorBase):
    id: int
    name: str
    email: EmailStr
    department: str
