from fastapi import APIRouter, HTTPException
from typing import Optional
from students.app.schemas import StudentCreate, StudentUpdate, StudentResponse
from students.app import service

router = APIRouter()


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(payload: StudentCreate):
    return service.create_student(payload)


@router.get("/", response_model=list[StudentResponse])
def list_students(name: Optional[str] = None, limit: int = 10, offset: int = 0):
    return service.get_all_students(name=name, limit=limit, offset=offset)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    student = service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, payload: StudentUpdate):
    student = service.update_student(student_id, payload)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int):
    if not service.delete_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted"}


@router.get("/{student_id}/courses")
def get_student_courses(student_id: int):
    student = service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return service.get_student_courses(student_id)


@router.get("/{student_id}/gpa")
def get_student_gpa(student_id: int):
    student = service.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return service.get_student_gpa(student_id)
