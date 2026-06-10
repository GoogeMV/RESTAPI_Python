from enrollments.app import data as db
from enrollments.app.schemas import EnrollmentCreate
from fastapi import HTTPException


def create_enrollment(payload: EnrollmentCreate) -> dict:
    # Verificare duplicate
    for e in db.enrollments_db.values():
        if e["student_id"] == payload.student_id and e["course_name"] == payload.course_name:
            raise HTTPException(status_code=400, detail="Student deja inscris la acest curs")
    enrollment = {
        "id": db.next_id,
        "student_id": payload.student_id,
        "course_name": payload.course_name,
        "professor_id": payload.professor_id,
        "status": "enrolled",
    }
    db.enrollments_db[db.next_id] = enrollment
    db.next_id += 1
    return enrollment


def get_all_enrollments(
    limit: int = 10,
    offset: int = 0,
    student_id: int | None = None,
    professor_id: int | None = None,
    course_name: str | None = None,
) -> list[dict]:
    # 1. Luăm toate datele brute
    data = list(db.enrollments_db.values())

    # 2. Aplicăm filtrele (dacă sunt furnizate de utilizator)
    if student_id:
        data = [e for e in data if e["student_id"] == student_id]

    if professor_id:
        data = [e for e in data if e["professor_id"] == professor_id]

    if course_name:
        # Folosim lower() pentru ca căutarea să nu fie influențată de litere mari/mici
        data = [e for e in data if course_name.lower() in e["course_name"].lower()]

    # 3. La final, aplicăm paginarea pe lista filtrată
    return data[offset : offset + limit]


def get_enrollment(enrollment_id: int) -> dict | None:
    return db.enrollments_db.get(enrollment_id)


def delete_enrollment(enrollment_id: int) -> bool:
    if enrollment_id in db.enrollments_db:
        del db.enrollments_db[enrollment_id]
        return True
    return False


def get_waitlist() -> list[dict]:
    return [e for e in db.enrollments_db.values() if e["status"] == "waitlist"]


def get_by_student(student_id: int) -> list[dict]:
    return [e for e in db.enrollments_db.values() if e["student_id"] == student_id]


def update_enrollment_status(enrollment_id: int, status: str) -> dict | None:
    # Verificăm dacă ID-ul înscrierii există în dicționarul nostru din data.py
    if enrollment_id in db.enrollments_db:
        db.enrollments_db[enrollment_id]["status"] = status
        return db.enrollments_db[enrollment_id]
    # Dacă nu a găsit ID-ul, returnăm None pentru ca routerul să știe să dea 404
    return None
