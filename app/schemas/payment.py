from pydantic import BaseModel
from typing import Optional
from datetime import date


class PaymentBase(BaseModel):
    booking_id: int
    amount: float
    payment_method: str
    status: str = "pending"


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    booking_id: Optional[int] = None
    amount: Optional[float] = None
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None


class Payment(PaymentBase):
    id: int
    payment_date: Optional[date] = None

    class Config:
        from_attributes = True
