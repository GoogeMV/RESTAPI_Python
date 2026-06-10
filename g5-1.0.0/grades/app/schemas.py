from pydantic import BaseModel, Field


class GradeCreate(BaseModel):
    student_id: int = Field(..., gt=0)
    course_name: str = Field(..., min_length=3, max_length=100)
    value: float = Field(..., ge=1.0, le=10.0)


class GradeUpdate(BaseModel):
    student_id: int | None = Field(None, gt=0)
    course_name: str | None = Field(None, min_length=3, max_length=100)
    value: float | None = Field(None, ge=1.0, le=10.0)


class GradeResponse(BaseModel):
    id: int
    student_id: int
    course_name: str
    value: float


class StudentGPA(BaseModel):
    student_id: int
    gpa: float


class CourseStatsResponse(BaseModel):
    course_name: str
    average_grade: float
    max_grade: float
    min_grade: float
    total_grades: int
