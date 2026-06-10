from collections import defaultdict


def get_enrollment_stats() -> dict:
    try:
        from enrollments.app import data as enr_data

        counts = defaultdict(int)
        for e in enr_data.enrollments_db.values():
            counts[e["course_name"]] += 1
        return dict(counts)
    except ImportError:
        return {}


def get_grade_distribution(min_avg: float = 0.0) -> dict:
    try:
        from grades.app import data as gr_data

        course_grades = defaultdict(list)
        for g in gr_data.grades_db.values():
            course_grades[g["course_name"]].append(g["value"])
        result = {course: round(sum(vals) / len(vals), 2) for course, vals in course_grades.items()}
        return {course: avg for course, avg in result.items() if avg >= min_avg}
    except ImportError:
        return {}


def get_student_count() -> int:
    try:
        from students.app import data as st_data

        return len(st_data.students_db)
    except ImportError:
        return 0


def get_professor_count() -> int:
    try:
        from professors.app import data as pr_data

        return len(pr_data.professors_db)
    except ImportError:
        return 0


def get_library_stats() -> dict:
    try:
        from library.app import data as lib_data

        total_books = len(lib_data.books_db)
        active_loans = len([loan for loan in lib_data.loans_db.values() if loan["status"] == "active"])
        return {"total_books": total_books, "active_loans": active_loans}
    except ImportError:
        return {"total_books": 0, "active_loans": 0}
