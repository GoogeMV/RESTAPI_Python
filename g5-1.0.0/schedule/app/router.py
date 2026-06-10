from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from schedule.app.schemas import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from schedule.app import service

router = APIRouter()


@router.post("/", response_model=ScheduleResponse, status_code=201)
def create_slot(payload: ScheduleCreate):
    return service.create_slot(payload)


@router.get("/", response_model=list[ScheduleResponse])
def list_slots(
    day: Optional[str] = Query(default=None, description="Filtreaza dupa zi (ex: Luni)"),
    professor_id: Optional[int] = Query(default=None, description="Filtreaza dupa ID profesor"),
    room: Optional[str] = Query(default=None, description="Filtreaza dupa sala (ex: A101)"),
    limit: int = Query(default=10, ge=1, le=100, description="Numarul maxim de rezultate"),
    offset: int = Query(default=0, ge=0, description="De unde incepe lista"),
):
    return service.get_all_slots(
        day=day,
        professor_id=professor_id,
        room=room,
        limit=limit,
        offset=offset,
    )


@router.get("/conflicts")
def get_conflicts():
    slots = service.get_all_slots()
    conflicts = []
    for i in range(len(slots)):
        for j in range(i + 1, len(slots)):
            a = slots[i]
            b = slots[j]
            if a["room"] == b["room"] and a["day"] == b["day"]:
                if a["start_time"] < b["end_time"] and b["start_time"] < a["end_time"]:
                    conflicts.append({"slot_a": a, "slot_b": b})
    return conflicts


@router.get("/professor/{professor_id}", response_model=list[ScheduleResponse])
def get_slots_by_professor(professor_id: int):
    """Returneaza toate sloturile din orar ale unui profesor."""
    return service.get_slots_by_professor(professor_id)


@router.get("/{slot_id}", response_model=ScheduleResponse)
def get_slot(slot_id: int):
    slot = service.get_slot(slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    return slot


@router.put("/{slot_id}", response_model=ScheduleResponse)
def update_slot(slot_id: int, payload: ScheduleUpdate):
    slot = service.update_slot(slot_id, payload)
    if not slot:
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    return slot


@router.delete("/{slot_id}")
def delete_slot(slot_id: int):
    if not service.delete_slot(slot_id):
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    return {"message": "Schedule slot deleted"}
