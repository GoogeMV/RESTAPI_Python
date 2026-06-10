from fastapi import HTTPException
from typing import Optional
from schedule.app import data as db
from schedule.app.schemas import ScheduleCreate, ScheduleUpdate


def _is_duplicate(payload: ScheduleCreate, exclude_id: int | None = None) -> bool:
    for slot_id, slot in db.schedule_db.items():
        if exclude_id is not None and slot_id == exclude_id:
            continue
        if (
            slot["professor_id"] == payload.professor_id
            and slot["room"] == payload.room
            and slot["day"] == payload.day
            and slot["start_time"] == payload.start_time
        ):
            return True
    return False


def create_slot(payload: ScheduleCreate) -> dict:
    if _is_duplicate(payload):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Exista deja un slot pentru profesorul {payload.professor_id} "
                f"in sala {payload.room}, {payload.day} la {payload.start_time}."
            ),
        )
    slot = {
        "id": db.next_id,
        "course_name": payload.course_name,
        "professor_id": payload.professor_id,
        "room": payload.room,
        "day": payload.day,
        "start_time": payload.start_time,
        "end_time": payload.end_time,
    }
    db.schedule_db[db.next_id] = slot
    db.next_id += 1
    return slot


def get_all_slots(
    day: Optional[str] = None,
    professor_id: Optional[int] = None,
    room: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> list[dict]:
    slots = list(db.schedule_db.values())

    # Filtrare
    if day is not None:
        slots = [s for s in slots if s["day"].lower() == day.lower()]
    if professor_id is not None:
        slots = [s for s in slots if s["professor_id"] == professor_id]
    if room is not None:
        slots = [s for s in slots if s["room"].lower() == room.lower()]

    # Paginare
    return slots[offset : offset + limit]


def get_slot(slot_id: int) -> dict | None:
    return db.schedule_db.get(slot_id)


def update_slot(slot_id: int, payload: ScheduleUpdate) -> dict | None:
    if slot_id not in db.schedule_db:
        return None

    slot = db.schedule_db[slot_id]

    merged = {
        "professor_id": payload.professor_id if payload.professor_id is not None else slot["professor_id"],
        "room": payload.room if payload.room is not None else slot["room"],
        "day": payload.day if payload.day is not None else slot["day"],
        "start_time": payload.start_time if payload.start_time is not None else slot["start_time"],
        "end_time": payload.end_time if payload.end_time is not None else slot["end_time"],
    }

    if merged["end_time"] <= merged["start_time"]:
        raise HTTPException(status_code=422, detail="end_time trebuie sa fie dupa start_time")

    check = ScheduleCreate(
        course_name=payload.course_name or slot["course_name"],
        **merged,
    )
    if _is_duplicate(check, exclude_id=slot_id):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Exista deja un slot pentru profesorul {merged['professor_id']} "
                f"in sala {merged['room']}, {merged['day']} la {merged['start_time']}."
            ),
        )

    slot.update({k: v for k, v in merged.items()})
    if payload.course_name is not None:
        slot["course_name"] = payload.course_name

    return slot


def delete_slot(slot_id: int) -> bool:
    if slot_id in db.schedule_db:
        del db.schedule_db[slot_id]
        return True
    return False


def get_slots_by_professor(professor_id: int) -> list[dict]:
    """Returneaza toate sloturile unui profesor, fara limita de paginare."""
    return [slot for slot in db.schedule_db.values() if slot["professor_id"] == professor_id]
