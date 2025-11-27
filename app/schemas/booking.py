from pydantic import BaseModel
from typing import Optional
from datetime import date


class BookingBase(BaseModel):
    guest_id: int
    room_id: int
    check_in_date: date
    check_out_date: date
    status: str = "pending"


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    guest_id: Optional[int] = None
    room_id: Optional[int] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    total_cost: Optional[float] = None
    status: Optional[str] = None


class Booking(BookingBase):
    id: int
    total_cost: Optional[float] = None

    class Config:
        from_attributes = True
