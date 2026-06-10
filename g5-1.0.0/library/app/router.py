from fastapi import APIRouter, HTTPException, Path
from library.app.schemas import BookCreate, BookResponse, BorrowRequest, ReturnRequest, LoanResponse
from library.app import service

router = APIRouter()


@router.post("/books", response_model=BookResponse, status_code=201)
def add_book(payload: BookCreate):
    return service.add_book(payload)


@router.get("/books", response_model=list[BookResponse])
def list_books(limit: int = 10, offset: int = 0, author: str = None):
    return service.get_all_books(limit=limit, offset=offset, author=author)


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    book = service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/borrow", response_model=LoanResponse, status_code=201)
def borrow_book(payload: BorrowRequest):
    loan = service.borrow_book(payload)
    if not loan:
        raise HTTPException(status_code=400, detail="Book not available for borrowing")
    return loan


@router.post("/return")
def return_book(payload: ReturnRequest):
    loan = service.return_book(payload.loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found or already returned")
    return loan


@router.get("/loans", response_model=list[LoanResponse])
def list_loans(student_id: int = None):
    return service.get_all_loans(student_id=student_id)


@router.get("/availability/{book_id}")
def check_availability(book_id: int):
    result = service.get_availability(book_id)
    if not result:
        raise HTTPException(status_code=404, detail="Book not found")
    return result


@router.get("/student/{student_id}/history", response_model=list[LoanResponse])
def get_student_history(student_id: int = Path(gt=0)):
    loans = service.get_student_history(student_id)
    if not loans:
        raise HTTPException(status_code=404, detail="No loan history found for this student")
    return loans
