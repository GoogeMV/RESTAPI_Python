from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, model_validator
from datetime import date


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------


class StudentBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StudentCreate(StudentBase):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    year: int = Field(ge=1, le=6)

    @field_validator("name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class StudentUpdate(StudentBase):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    year: int | None = Field(default=None, ge=1, le=6)

    @field_validator("name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class StudentResponse(StudentBase):
    id: int
    name: str
    email: EmailStr
    year: int


# ---------------------------------------------------------------------------
# Professor
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------


class CourseBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CourseCreate(CourseBase):
    name: str = Field(min_length=3, max_length=150)
    credits: int = Field(ge=1, le=30)
    professor_id: int = Field(gt=0)

    @field_validator("name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class CourseUpdate(CourseBase):
    name: str | None = Field(default=None, min_length=3, max_length=150)
    credits: int | None = Field(default=None, ge=1, le=30)
    professor_id: int | None = Field(default=None, gt=0)

    @field_validator("name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class CourseResponse(CourseBase):
    id: int
    name: str
    credits: int
    professor_id: int


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------


class EnrollmentBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EnrollmentCreate(EnrollmentBase):
    student_id: int = Field(gt=0)
    course_name: str = Field(min_length=3, max_length=150)

    @field_validator("course_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class EnrollmentResponse(EnrollmentBase):
    id: int
    student_id: int
    course_name: str


# ---------------------------------------------------------------------------
# Grade
# ---------------------------------------------------------------------------


class GradeBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GradeCreate(GradeBase):
    student_id: int = Field(gt=0)
    course_name: str = Field(min_length=3, max_length=150)
    value: float = Field(ge=1.0, le=10.0)

    @field_validator("value", mode="before")
    @classmethod
    def validate_grade(cls, v):
        if isinstance(v, (int, float)):
            rounded = round(float(v) * 2) / 2
            if abs(rounded - float(v)) > 0.01:
                raise ValueError("Nota trebuie să fie întreagă sau cu .5 (ex: 7, 7.5, 8).")
            return rounded
        return v

    @field_validator("course_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class GradeUpdate(GradeBase):
    value: float | None = Field(default=None, ge=1.0, le=10.0)

    @field_validator("value", mode="before")
    @classmethod
    def validate_grade(cls, v):
        if v is not None and isinstance(v, (int, float)):
            rounded = round(float(v) * 2) / 2
            if abs(rounded - float(v)) > 0.01:
                raise ValueError("Nota trebuie să fie întreagă sau cu .5 (ex: 7, 7.5, 8).")
            return rounded
        return v


class GradeResponse(GradeBase):
    id: int
    student_id: int
    course_name: str
    value: float


# ---------------------------------------------------------------------------
# Book
# ---------------------------------------------------------------------------


class BookBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BookCreate(BookBase):
    title: str = Field(min_length=3, max_length=200)
    author: str = Field(min_length=2, max_length=150)
    available_copies: int = Field(ge=0)

    @field_validator("title", "author", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class BookUpdate(BookBase):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    author: str | None = Field(default=None, min_length=2, max_length=150)
    available_copies: int | None = Field(default=None, ge=0)

    @field_validator("title", "author", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class BookResponse(BookBase):
    id: int
    title: str
    author: str
    available_copies: int


# ---------------------------------------------------------------------------
# Loan
# ---------------------------------------------------------------------------


class LoanBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoanCreate(LoanBase):
    student_id: int = Field(gt=0)
    book_id: int = Field(gt=0)
    loan_date: date
    due_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.due_date <= self.loan_date:
            raise ValueError("Data scadenței trebuie să fie după data împrumutului.")
        return self


class LoanResponse(LoanBase):
    id: int
    student_id: int
    book_id: int
    loan_date: date
    due_date: date
    status: str
