from fastapi import HTTPException
from professors.app import data as db
from professors.app.schemas import ProfessorCreate, ProfessorUpdate


# exclude_id is used on PUT requests, when the professor doesn't change his email address
def _email_exists(email: str, exclude_id: int | None = None) -> bool:
    return any(professor["email"] == email and professor["id"] != exclude_id for professor in db.professors_db.values())


def _matches_filter(value: str, query: str | None) -> bool:
    if query is None:
        return True
    return query.lower() in value.lower()


def create_professor(payload: ProfessorCreate) -> dict:
    if _email_exists(payload.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    prof = {"id": db.next_id, "name": payload.name, "email": payload.email, "department": payload.department}
    db.professors_db[db.next_id] = prof
    db.next_id += 1
    return prof


def get_all_professors(
    limit: int = 10,
    offset: int = 0,
    name: str | None = None,
    department: str | None = None,
    email: str | None = None,
) -> list[dict]:
    filtered = [
        prof
        for prof in db.professors_db.values()
        if _matches_filter(prof["name"], name)
        and _matches_filter(prof["department"], department)
        and _matches_filter(prof["email"], email)
    ]
    return filtered[offset : offset + limit]


def get_professor(professor_id: int) -> dict | None:
    return db.professors_db.get(professor_id)


def update_professor(professor_id: int, payload: ProfessorUpdate) -> dict | None:
    if professor_id not in db.professors_db:
        return None

    prof = db.professors_db[professor_id]

    if payload.email is not None and _email_exists(payload.email, exclude_id=professor_id):
        raise HTTPException(status_code=409, detail="Email already exists")

    if payload.name is not None:
        prof["name"] = payload.name

    if payload.email is not None:
        prof["email"] = payload.email

    if payload.department is not None:
        prof["department"] = payload.department

    return prof


def delete_professor(professor_id: int) -> bool:
    if professor_id in db.professors_db:
        del db.professors_db[professor_id]
        return True
    return False


def get_professor_courses(professor_id: int, limit: int = 10, offset: int = 0) -> list[dict] | None:
    try:
        from enrollments.app import data as enr_data
    except ImportError:
        return None

    courses = [e for e in enr_data.enrollments_db.values() if e["professor_id"] == professor_id]
    return courses[offset : offset + limit]


def get_professor_students(professor_id: int, limit: int = 10, offset: int = 0) -> list[dict] | None:
    try:
        from enrollments.app import data as enr_data
        from students.app import data as stu_data
    except ImportError:
        return None

    professor_enrollments = [e for e in enr_data.enrollments_db.values() if e["professor_id"] == professor_id]

    student_ids = {e["student_id"] for e in professor_enrollments}

    students = [stu_data.students_db[sid] for sid in sorted(student_ids) if sid in stu_data.students_db]

    return students[offset : offset + limit]
