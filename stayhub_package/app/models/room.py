from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(10), unique=True, nullable=False)
    room_type = Column(String(100), nullable=False)  # Свободное текстовое обозначение типа
    capacity = Column(Integer, nullable=False, default=1)
    price_per_night = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
