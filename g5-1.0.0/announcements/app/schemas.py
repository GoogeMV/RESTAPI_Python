from pydantic import BaseModel, Field


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=10, max_length=1000)
    author: str = Field(..., min_length=2, max_length=100)
    target_audience: str = Field(..., min_length=3, max_length=50)


class AnnouncementUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    content: str | None = Field(None, min_length=10, max_length=1000)
    author: str | None = Field(None, min_length=2, max_length=100)
    target_audience: str | None = Field(None, min_length=3, max_length=50)


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    target_audience: str
    status: str
