from fastapi import APIRouter, HTTPException
from enrollments.app.schemas import EnrollmentCreate, EnrollmentResponse, EnrollmentStatusUpdate
from enrollments.app import service


router = APIRouter()


@router.post("/", response_model=EnrollmentResponse, status_code=201)
def create_enrollment(payload: EnrollmentCreate):
    return service.create_enrollment(payload)


@router.get("/", response_model=list[EnrollmentResponse])
def list_enrollments(
    limit: int = 10,
    offset: int = 0,
    student_id: int | None = None,
    professor_id: int | None = None,
    course_name: str | None = None,
):
    return service.get_all_enrollments(
        limit=limit, offset=offset, student_id=student_id, professor_id=professor_id, course_name=course_name
    )


@router.get("/waitlist", response_model=list[EnrollmentResponse])
def get_waitlist():
    return service.get_waitlist()


@router.get("/student/{student_id}", response_model=list[EnrollmentResponse])
def get_student_enrollments(student_id: int):
    return service.get_by_student(student_id)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_enrollment(enrollment_id: int):
    enrollment = service.get_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enrollment


@router.delete("/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    if not service.delete_enrollment(enrollment_id):
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"message": "Enrollment deleted"}


@router.put("/{enrollment_id}/status", response_model=EnrollmentResponse)
def update_enrollment_status(enrollment_id: int, payload: EnrollmentStatusUpdate):
    updated_enrollment = service.update_enrollment_status(enrollment_id, payload.status)
    if not updated_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return updated_enrollment
