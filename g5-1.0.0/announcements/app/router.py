from fastapi import APIRouter, HTTPException, Query
from announcements.app.schemas import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from announcements.app import service

router = APIRouter()


@router.post("/", response_model=AnnouncementResponse, status_code=201)
def create_announcement(payload: AnnouncementCreate):
    return service.create_announcement(payload)


@router.get("/", response_model=list[AnnouncementResponse])
def list_announcements(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    target_audience: str | None = None,
    author: str | None = None,
    search: str | None = None,
):
    return service.get_all_announcements(
        limit=limit,
        offset=offset,
        target_audience=target_audience,
        author=author,
        search=search,
    )


@router.get("/stats/summary")
def get_summary():
    return service.get_summary()


@router.get("/audience/{audience}", response_model=list[AnnouncementResponse])
def get_by_audience(audience: str):
    return service.get_by_audience(audience)


@router.delete("/audience/{audience}")
def delete_by_audience(audience: str):
    deleted_count = service.delete_by_audience(audience)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No announcements found for this audience")
    return {"message": "Announcements deleted", "deleted_count": deleted_count}


@router.get("/authors/{author}", response_model=list[AnnouncementResponse])
def get_by_author(author: str):
    return service.get_by_author(author)


@router.get("/search/{keyword}", response_model=list[AnnouncementResponse])
def search_announcements(keyword: str):
    return service.search_announcements(keyword)


@router.post("/{ann_id}/archive", response_model=AnnouncementResponse)
def archive_announcement(ann_id: int):
    ann = service.archive_announcement(ann_id)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann


@router.get("/{ann_id}", response_model=AnnouncementResponse)
def get_announcement(ann_id: int):
    ann = service.get_announcement(ann_id)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann


@router.put("/{ann_id}", response_model=AnnouncementResponse)
def update_announcement(ann_id: int, payload: AnnouncementUpdate):
    ann = service.update_announcement(ann_id, payload)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return ann


@router.delete("/{ann_id}")
def delete_announcement(ann_id: int):
    if not service.delete_announcement(ann_id):
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted"}
