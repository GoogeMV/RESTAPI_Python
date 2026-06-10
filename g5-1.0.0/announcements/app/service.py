from announcements.app import data as db
from announcements.app.schemas import AnnouncementCreate, AnnouncementUpdate


def create_announcement(payload: AnnouncementCreate) -> db.AnnouncementDict:
    ann: db.AnnouncementDict = {
        "id": db.next_id,
        "title": payload.title,
        "content": payload.content,
        "author": payload.author,
        "target_audience": payload.target_audience,
        "status": "active",
    }
    db.announcements_db[db.next_id] = ann
    db.next_id += 1
    return ann


def get_all_announcements(
    limit: int = 10,
    offset: int = 0,
    target_audience: str | None = None,
    author: str | None = None,
    search: str | None = None,
) -> list[db.AnnouncementDict]:
    data = list(db.announcements_db.values())

    if target_audience:
        audience_filter = target_audience.lower()
        data = [ann for ann in data if ann["target_audience"].lower() == audience_filter]

    if author:
        author_filter = author.lower()
        data = [ann for ann in data if author_filter in ann["author"].lower()]

    if search:
        search_filter = search.lower()
        data = [ann for ann in data if search_filter in ann["title"].lower() or search_filter in ann["content"].lower()]

    return data[offset : offset + limit]


def get_announcement(ann_id: int) -> db.AnnouncementDict | None:
    return db.announcements_db.get(ann_id)


def update_announcement(
    ann_id: int,
    payload: AnnouncementUpdate,
) -> db.AnnouncementDict | None:
    if ann_id not in db.announcements_db:
        return None
    ann = db.announcements_db[ann_id]
    if payload.title is not None:
        ann["title"] = payload.title
    if payload.content is not None:
        ann["content"] = payload.content
    if payload.author is not None:
        ann["author"] = payload.author
    if payload.target_audience is not None:
        ann["target_audience"] = payload.target_audience
    return ann


def delete_announcement(ann_id: int) -> bool:
    if ann_id in db.announcements_db:
        del db.announcements_db[ann_id]
        return True
    return False


def delete_by_audience(audience: str) -> int:
    audience_filter = audience.lower()
    matching_ids = [
        ann_id for ann_id, ann in db.announcements_db.items() if ann["target_audience"].lower() == audience_filter
    ]
    for ann_id in matching_ids:
        del db.announcements_db[ann_id]
    return len(matching_ids)


def get_summary() -> dict[str, int]:
    announcements = list(db.announcements_db.values())
    audiences = {ann["target_audience"].lower() for ann in announcements}
    authors = {ann["author"].lower() for ann in announcements}

    return {
        "total": len(announcements),
        "audiences": len(audiences),
        "authors": len(authors),
        "archived": sum(1 for ann in announcements if ann["status"] == "archived"),
        "active": sum(1 for ann in announcements if ann["status"] == "active"),
    }


def archive_announcement(ann_id: int) -> db.AnnouncementDict | None:
    if ann_id not in db.announcements_db:
        return None
    ann = db.announcements_db[ann_id]
    ann["status"] = "archived"
    return ann


def get_by_audience(audience: str) -> list[db.AnnouncementDict]:
    audience_filter = audience.lower()
    return [ann for ann in db.announcements_db.values() if ann["target_audience"].lower() == audience_filter]


def get_by_author(author: str) -> list[db.AnnouncementDict]:
    author_filter = author.lower()
    return [ann for ann in db.announcements_db.values() if author_filter in ann["author"].lower()]


def search_announcements(keyword: str) -> list[db.AnnouncementDict]:
    keyword_filter = keyword.lower()
    return [
        ann
        for ann in db.announcements_db.values()
        if keyword_filter in ann["title"].lower() or keyword_filter in ann["content"].lower()
    ]
