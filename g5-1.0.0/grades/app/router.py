from fastapi import APIRouter, HTTPException, Query, Path
from grades.app.schemas import CourseStatsResponse, GradeCreate, GradeUpdate, GradeResponse, StudentGPA
from grades.app import service

router = APIRouter()


@router.post("/", response_model=GradeResponse, status_code=201)
def create_grade(payload: GradeCreate):
    return service.create_grade(payload)


@router.get("/", response_model=list[GradeResponse])
def list_grades(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_value: float | None = Query(None, ge=1.0, le=10.0),
):
    return service.get_all_grades(limit, offset, min_value)


@router.get("/transcript/{student_id}", response_model=list[GradeResponse])
def get_transcript(student_id: int):
    return service.get_transcript(student_id)


@router.get("/gpa/{student_id}")
def get_gpa(student_id: int):
    gpa = service.get_gpa(student_id)
    if gpa is None:
        return {"student_id": student_id, "gpa": 0.0, "message": "No grades found"}
    return {"student_id": student_id, "gpa": round(gpa, 2)}


@router.get("/{grade_id}", response_model=GradeResponse)
def get_grade(grade_id: int):
    grade = service.get_grade(grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.get("/top/{n}", response_model=list[StudentGPA])
def get_top_students(n: int = Path(..., gt=0)):
    return service.get_top_students(n)


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(grade_id: int, payload: GradeUpdate):
    grade = service.update_grade(grade_id, payload)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.delete("/{grade_id}")
def delete_grade(grade_id: int):
    if not service.delete_grade(grade_id):
        raise HTTPException(status_code=404, detail="Grade not found")
    return {"message": "Grade deleted"}


@router.get("/stats/{course_name}", response_model=CourseStatsResponse)
def get_course_stats(course_name: str):
    stats = service.get_course_stats(course_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Course not found")
    return stats
