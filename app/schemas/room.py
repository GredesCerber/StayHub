from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    room_number: str
    room_type: str
    capacity: int = 1
    price_per_night: float
    is_available: bool = True
    description: Optional[str] = None


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price_per_night: Optional[float] = None
    is_available: Optional[bool] = None
    description: Optional[str] = None


class Room(RoomBase):
    id: int

    class Config:
        from_attributes = True
