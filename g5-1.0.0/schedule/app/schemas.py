from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import re

VALID_DAYS = {"Luni", "Marti", "Miercuri", "Joi", "Vineri"}
TIME_PATTERN = re.compile(r"^\d{2}:\d{2}$")


def validate_time_format(value: str) -> str:
    """Verifica formatul HH:MM si ca ora/minutul sunt valide."""
    if not TIME_PATTERN.match(value):
        raise ValueError("Timpul trebuie sa fie in formatul HH:MM (ex: 08:00)")
    hour, minute = int(value[:2]), int(value[3:])
    if not (0 <= hour <= 23):
        raise ValueError("Ora trebuie sa fie intre 00 si 23")
    if not (0 <= minute <= 59):
        raise ValueError("Minutele trebuie sa fie intre 00 si 59")
    return value


class ScheduleCreate(BaseModel):
    course_name: str
    professor_id: int
    room: str
    day: str
    start_time: str
    end_time: str

    @field_validator("course_name")
    @classmethod
    def course_name_min_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Numele cursului trebuie sa aiba minim 3 caractere")
        return v

    @field_validator("professor_id")
    @classmethod
    def professor_id_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("professor_id trebuie sa fie un numar pozitiv")
        return v

    @field_validator("room")
    @classmethod
    def room_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Sala nu poate fi goala")
        return v

    @field_validator("day")
    @classmethod
    def day_must_be_valid(cls, v: str) -> str:
        v = v.strip().capitalize()
        if v not in VALID_DAYS:
            raise ValueError(f"Ziua trebuie sa fie una dintre: {', '.join(sorted(VALID_DAYS))}")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def time_format(cls, v: str) -> str:
        return validate_time_format(v)

    @model_validator(mode="after")
    def end_time_after_start_time(self) -> "ScheduleCreate":
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError("end_time trebuie sa fie dupa start_time")
        return self


class ScheduleUpdate(BaseModel):
    course_name: Optional[str] = None
    professor_id: Optional[int] = None
    room: Optional[str] = None
    day: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    @field_validator("course_name")
    @classmethod
    def course_name_min_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 3:
                raise ValueError("Numele cursului trebuie sa aiba minim 3 caractere")
        return v

    @field_validator("professor_id")
    @classmethod
    def professor_id_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("professor_id trebuie sa fie un numar pozitiv")
        return v

    @field_validator("room")
    @classmethod
    def room_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Sala nu poate fi goala")
        return v

    @field_validator("day")
    @classmethod
    def day_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().capitalize()
            if v not in VALID_DAYS:
                raise ValueError(f"Ziua trebuie sa fie una dintre: {', '.join(sorted(VALID_DAYS))}")
        return v

    @field_validator("start_time", "end_time")
    @classmethod
    def time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_time_format(v)
        return v


class ScheduleResponse(BaseModel):
    id: int
    course_name: str
    professor_id: int
    room: str
    day: str
    start_time: str
    end_time: str
