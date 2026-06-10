from library.app import data as db
from library.app.schemas import BookCreate, BorrowRequest


def add_book(payload: BookCreate) -> dict:
    book = {
        "id": db.next_book_id,
        "title": payload.title,
        "author": payload.author,
        "isbn": payload.isbn,
        "copies": payload.copies,
    }
    db.books_db[db.next_book_id] = book
    db.next_book_id += 1
    return book


def get_all_books(limit: int = 10, offset: int = 0, author: str = None) -> list[dict]:
    books = list(db.books_db.values())
    if author:
        books = [b for b in books if author.lower() in b["author"].lower()]
    return books[offset : offset + limit]


def get_book(book_id: int) -> dict | None:
    return db.books_db.get(book_id)


def borrow_book(payload: BorrowRequest) -> dict | None:
    book = db.books_db.get(payload.book_id)
    if not book or book["copies"] <= 0:
        return None
    book["copies"] -= 1
    loan = {
        "id": db.next_loan_id,
        "book_id": payload.book_id,
        "student_id": payload.student_id,
        "status": "active",
    }
    db.loans_db[db.next_loan_id] = loan
    db.next_loan_id += 1
    return loan


def return_book(loan_id: int) -> dict | None:
    loan = db.loans_db.get(loan_id)
    if not loan or loan["status"] != "active":
        return None
    loan["status"] = "returned"
    book = db.books_db.get(loan["book_id"])
    if book:
        book["copies"] += 1
    return loan


def get_all_loans(student_id: int = None) -> list[dict]:
    loans = list(db.loans_db.values())
    if student_id:
        loans = [loan for loan in loans if loan["student_id"] == student_id]
    return loans


def get_availability(book_id: int) -> dict | None:
    book = db.books_db.get(book_id)
    if not book:
        return None
    active_loans = len(
        [loan for loan in db.loans_db.values() if loan["book_id"] == book_id and loan["status"] == "active"]
    )
    return {
        "book_id": book_id,
        "title": book["title"],
        "total_copies": book["copies"] + active_loans,
        "available_copies": book["copies"],
    }


def get_student_history(student_id: int) -> list[dict]:
    return [loan for loan in db.loans_db.values() if loan["student_id"] == student_id]
