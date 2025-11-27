from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class RoomType(Base):
    """Справочник типов номеров."""

    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    default_capacity = Column(Integer, nullable=True)
    default_price = Column(Float, nullable=True)
