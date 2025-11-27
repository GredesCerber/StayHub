from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, List, Dict, Any
from datetime import date


class BookingBase(BaseModel):
    guest_id: int = Field(..., gt=0, description="Guest ID")
    room_id: int = Field(..., gt=0, description="Room ID")
    check_in_date: date = Field(..., description="Check-in date")
    check_out_date: date = Field(..., description="Check-out date")
    status: Literal["pending", "confirmed", "cancelled", "completed"] = Field(
        default="pending", description="Booking status"
    )
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.check_out_date <= self.check_in_date:
            raise ValueError("Check-out date must be after check-in date")
        return self


class BookingCreate(BookingBase):
    """Schema for creating a booking."""
    pass


class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    guest_id: Optional[int] = Field(default=None, gt=0)
    room_id: Optional[int] = Field(default=None, gt=0)
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    total_cost: Optional[float] = Field(default=None, ge=0)
    status: Optional[Literal["pending", "confirmed", "cancelled", "completed"]] = None


class BookingFilter(BaseModel):
    """Schema for filtering bookings."""
    guest_id: Optional[int] = None
    room_id: Optional[int] = None
    status: Optional[Literal["pending", "confirmed", "cancelled", "completed"]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AvailabilityCheck(BaseModel):
    """Schema for checking room availability."""
    room_id: int = Field(..., gt=0)
    check_in: date
    check_out: date
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("Check-out date must be after check-in date")
        return self


class AvailabilityResponse(BaseModel):
    """Schema for availability check response."""
    room_id: int
    available: bool
    check_in: date
    check_out: date


class CostBreakdown(BaseModel):
    """Schema for booking cost breakdown."""
    room_cost: float
    nights: int
    price_per_night: float
    services: List[Dict[str, Any]]
    services_total: float
    total_cost: float


class Booking(BookingBase):
    """Schema for booking response."""
    id: int
    total_cost: Optional[float] = None

    class Config:
        from_attributes = True


class BookingWithDetails(Booking):
    """Schema for booking with guest and room details."""
    guest_name: Optional[str] = None
    room_number: Optional[str] = None
    room_type: Optional[str] = None
