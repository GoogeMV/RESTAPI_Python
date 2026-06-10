from grades.app import data as db
from grades.app.schemas import GradeCreate, GradeUpdate


def create_grade(payload: GradeCreate) -> dict:
    grade = {
        "id": db.next_id,
        "student_id": payload.student_id,
        "course_name": payload.course_name,
        "value": payload.value,
    }
    db.grades_db[db.next_id] = grade
    db.next_id += 1
    return grade


def get_all_grades(limit: int, offset: int, min_value: float | None) -> list[dict]:
    all_grades = list(db.grades_db.values())

    if min_value is not None:
        all_grades = [g for g in all_grades if g["value"] >= min_value]
    return all_grades[offset : offset + limit]


def get_grade(grade_id: int) -> dict | None:
    return db.grades_db.get(grade_id)


def update_grade(grade_id: int, payload: GradeUpdate) -> dict | None:
    if grade_id not in db.grades_db:
        return None
    grade = db.grades_db[grade_id]
    if payload.student_id is not None:
        grade["student_id"] = payload.student_id
    if payload.course_name is not None:
        grade["course_name"] = payload.course_name
    if payload.value is not None:
        grade["value"] = payload.value
    return grade


def delete_grade(grade_id: int) -> bool:
    if grade_id in db.grades_db:
        del db.grades_db[grade_id]
        return True
    return False


def get_transcript(student_id: int) -> list[dict]:
    return [g for g in db.grades_db.values() if g["student_id"] == student_id]


def get_gpa(student_id: int) -> float | None:
    grades = get_transcript(student_id)
    if not grades:
        return None
    return sum(g["value"] for g in grades) / len(grades)


def get_top_students(n: int) -> list[dict]:
    student_totals = {}
    for grade in db.grades_db.values():
        sid = grade["student_id"]
        if sid not in student_totals:
            student_totals[sid] = []
        student_totals[sid].append(grade["value"])

    student_averages = []
    for sid, values in student_totals.items():
        avg = sum(values) / len(values)
        student_averages.append({"student_id": sid, "gpa": round(avg, 2)})

    top_n = sorted(student_averages, key=lambda x: x["gpa"], reverse=True)[:n]

    return top_n


def get_course_stats(course_name: str) -> dict | None:
    course_grades = [
        g["value"] for g in db.grades_db.values() if g["course_name"].strip().lower() == course_name.strip().lower()
    ]
    if not course_grades:
        return None
    return {
        "course_name": course_name,
        "average_grade": round(sum(course_grades) / len(course_grades), 2),
        "max_grade": max(course_grades),
        "min_grade": min(course_grades),
        "total_grades": len(course_grades),
    }
