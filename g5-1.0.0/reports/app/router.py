from fastapi import APIRouter, Query
from reports.app import service

router = APIRouter()


@router.get("/enrollment-stats")
def enrollment_stats():
    return service.get_enrollment_stats()


@router.get("/grade-distribution")
def grade_distribution(min_avg: float = Query(default=0.0, ge=0.0)):
    return service.get_grade_distribution(min_avg=min_avg)


@router.get("/student-count")
def student_count():
    return {"student_count": service.get_student_count()}


@router.get("/professor-count")
def professor_count():
    return {"professor_count": service.get_professor_count()}


@router.get("/library-stats")
def library_stats():
    return service.get_library_stats()


@router.get("/export")
def export_all():
    return {
        "enrollment_stats": service.get_enrollment_stats(),
        "grade_distribution": service.get_grade_distribution(),
        "student_count": service.get_student_count(),
        "professor_count": service.get_professor_count(),
        "library_stats": service.get_library_stats(),
    }
