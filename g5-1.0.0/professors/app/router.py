from fastapi import APIRouter, HTTPException, Query
from professors.app.schemas import ProfessorCreate, ProfessorUpdate, ProfessorResponse
from professors.app import service

router = APIRouter()


@router.post("/", response_model=ProfessorResponse, status_code=201)
def create_professor(payload: ProfessorCreate):
    return service.create_professor(payload)


@router.get("/", response_model=list[ProfessorResponse])
def list_professors(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    name: str | None = Query(default=None),
    department: str | None = Query(default=None),
    email: str | None = Query(default=None),
):
    return service.get_all_professors(limit=limit, offset=offset, name=name, department=department, email=email)


@router.get("/{professor_id}", response_model=ProfessorResponse)
def get_professor(professor_id: int):
    prof = service.get_professor(professor_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Professor not found")
    return prof


@router.put("/{professor_id}", response_model=ProfessorResponse)
def update_professor(professor_id: int, payload: ProfessorUpdate):
    prof = service.update_professor(professor_id, payload)
    if not prof:
        raise HTTPException(status_code=404, detail="Professor not found")
    return prof


@router.delete("/{professor_id}")
def delete_professor(professor_id: int):
    if not service.delete_professor(professor_id):
        raise HTTPException(status_code=404, detail="Professor not found")
    return {"message": "Professor deleted"}


@router.get("/{professor_id}/courses")
def get_professor_courses(
    professor_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    prof = service.get_professor(professor_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Professor not found")

    courses = service.get_professor_courses(professor_id, limit=limit, offset=offset)
    if courses is None:
        return {"message": "Enrollments modulenot available", "courses": []}
    return courses


@router.get("/{professor_id}/students")
def get_professor_students(
    professor_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    prof = service.get_professor(professor_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Professor not found")

    students = service.get_professor_students(professor_id, limit=limit, offset=offset)
    if students is None:
        raise HTTPException(
            status_code=503,
            detail="Required modules (enrollments, students) not available",
        )
    return students
