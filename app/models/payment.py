from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, default=date.today)
    payment_method = Column(String(50), nullable=False)  # cash, card, transfer
    status = Column(String(20), default="pending")  # pending, completed, refunded

    booking = relationship("Booking", backref="payments")
