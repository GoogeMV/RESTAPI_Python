from pydantic import BaseModel, Field
from typing import Literal


class EnrollmentCreate(BaseModel):
    # Student ID trebuie să fie un număr pozitiv si să fie mai mare ca 0
    student_id: int = Field(..., gt=0)
    # Numele cursului trebuie să aibă minim 2 caractere
    course_name: str = Field(..., min_length=2)
    # Professor ID trebuie să fie un număr pozitiv si să fie mai mare ca 0"
    professor_id: int = Field(..., gt=0)


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_name: str
    professor_id: int
    status: str


class EnrollmentStatusUpdate(BaseModel):
    status: Literal["enrolled", "waitlist"] = Field(..., description="Statusul poate fi doar 'enrolled' sau 'waitlist'")
