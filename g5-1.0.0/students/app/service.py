from students.app import data as db
from students.app.schemas import StudentCreate, StudentUpdate
from fastapi import HTTPException


# 🔷 CREATE + duplicate check
def create_student(payload: StudentCreate) -> dict:
    # ❗ duplicate email check (cerință)
    for s in db.students_db.values():
        if s["email"] == payload.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    student = {"id": db.next_id, "name": payload.name, "email": payload.email, "year": payload.year}

    db.students_db[db.next_id] = student
    db.next_id += 1
    return student


# 🔷 GET ALL + FILTER + PAGINATION (CERINȚĂ IMPORTANTĂ)
def get_all_students(name: str | None = None, limit: int = 10, offset: int = 0) -> list[dict]:
    students = list(db.students_db.values())

    # filtrare după nume
    if name:
        students = [s for s in students if name.lower() in s["name"].lower()]

    # paginare
    return students[offset : offset + limit]


# 🔷 GET ONE
def get_student(student_id: int) -> dict | None:
    return db.students_db.get(student_id)


# 🔷 UPDATE + duplicate check
def update_student(student_id: int, payload: StudentUpdate) -> dict | None:
    if student_id not in db.students_db:
        return None

    student = db.students_db[student_id]

    # ❗ check duplicate email
    if payload.email is not None:
        for sid, s in db.students_db.items():
            if s["email"] == payload.email and sid != student_id:
                raise HTTPException(status_code=400, detail="Email already exists")

    if payload.name is not None:
        student["name"] = payload.name

    if payload.email is not None:
        student["email"] = payload.email

    if payload.year is not None:
        student["year"] = payload.year

    return student


# 🔷 DELETE
def delete_student(student_id: int) -> bool:
    if student_id in db.students_db:
        del db.students_db[student_id]
        return True
    return False


# 🔷 EXTRA ENDPOINT (CERINȚĂ: modul dependency - enrollments)
def get_student_courses(student_id: int):
    from enrollments.app import data as enr_data

    return [e for e in enr_data.enrollments_db.values() if e["student_id"] == student_id]


# 🔷 EXTRA ENDPOINT (CERINȚĂ BONUS: GPA din alt modul)
def get_student_gpa(student_id: int):
    from grades.app import data as grades_data

    grades = [g for g in grades_data.grades_db.values() if g["student_id"] == student_id]

    if not grades:
        return {"student_id": student_id, "gpa": 0}

    avg = sum(g["value"] for g in grades) / len(grades)

    return {"student_id": student_id, "gpa": round(avg, 2)}
