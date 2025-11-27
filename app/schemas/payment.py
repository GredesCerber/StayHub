from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


class PaymentBase(BaseModel):
    booking_id: int = Field(..., gt=0, description="Booking ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: Literal["cash", "card", "transfer"] = Field(..., description="Payment method")
    status: Literal["pending", "completed", "refunded"] = Field(
        default="pending", description="Payment status"
    )


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    pass


class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""
    booking_id: Optional[int] = Field(default=None, gt=0)
    amount: Optional[float] = Field(default=None, gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    status: Optional[Literal["pending", "completed", "refunded"]] = None


class PaymentFilter(BaseModel):
    """Schema for filtering payments."""
    booking_id: Optional[int] = None
    status: Optional[Literal["pending", "completed", "refunded"]] = None
    payment_method: Optional[Literal["cash", "card", "transfer"]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Payment(PaymentBase):
    """Schema for payment response."""
    id: int
    payment_date: Optional[date] = None

    class Config:
        from_attributes = True
