from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class RoomBase(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=10, description="Unique room number")
    room_type: Literal["single", "double", "suite"] = Field(..., description="Room type")
    capacity: int = Field(default=1, ge=1, le=10, description="Room capacity")
    price_per_night: float = Field(..., gt=0, description="Price per night")
    is_available: bool = Field(default=True, description="Room availability")
    description: Optional[str] = Field(default=None, max_length=255, description="Room description")


class RoomCreate(RoomBase):
    """Schema for creating a room."""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating a room."""
    room_number: Optional[str] = Field(default=None, min_length=1, max_length=10)
    room_type: Optional[Literal["single", "double", "suite"]] = None
    capacity: Optional[int] = Field(default=None, ge=1, le=10)
    price_per_night: Optional[float] = Field(default=None, gt=0)
    is_available: Optional[bool] = None
    description: Optional[str] = Field(default=None, max_length=255)


class RoomFilter(BaseModel):
    """Schema for filtering rooms."""
    room_type: Optional[Literal["single", "double", "suite"]] = None
    min_capacity: Optional[int] = Field(default=None, ge=1)
    is_available: Optional[bool] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)


class Room(RoomBase):
    """Schema for room response."""
    id: int

    class Config:
        from_attributes = True
