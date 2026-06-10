from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=2)
    author: str = Field(min_length=2)
    isbn: str = Field(min_length=10, max_length=13)
    copies: int = Field(ge=1)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    copies: int


class BorrowRequest(BaseModel):
    book_id: int = Field(gt=0)
    student_id: int = Field(gt=0)


class ReturnRequest(BaseModel):
    loan_id: int


class LoanResponse(BaseModel):
    id: int
    book_id: int
    student_id: int
    status: str
