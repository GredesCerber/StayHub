from pydantic import BaseModel
from typing import Optional


class BookingServiceBase(BaseModel):
    booking_id: int
    service_id: int
    quantity: int = 1


class BookingServiceCreate(BookingServiceBase):
    pass


class BookingServiceUpdate(BaseModel):
    booking_id: Optional[int] = None
    service_id: Optional[int] = None
    quantity: Optional[int] = None
    subtotal: Optional[float] = None


class BookingService(BookingServiceBase):
    id: int
    subtotal: Optional[float] = None

    class Config:
        from_attributes = True
