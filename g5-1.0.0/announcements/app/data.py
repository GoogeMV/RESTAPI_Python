from typing import TypedDict


class AnnouncementDict(TypedDict):
    id: int
    title: str
    content: str
    author: str
    target_audience: str
    status: str


announcements_db: dict[int, AnnouncementDict] = {}
next_id: int = 1
