from pydantic import BaseModel, Field
from typing import Optional


class RoomTypeBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Уникальный код типа номера")
    name: str = Field(..., min_length=1, max_length=100, description="Название типа номера")
    description: Optional[str] = Field(default=None, max_length=255, description="Описание типа номера")
    default_capacity: Optional[int] = Field(default=None, ge=1, le=10, description="Рекомендуемая вместимость")
    default_price: Optional[float] = Field(default=None, gt=0, description="Рекомендуемая стоимость за ночь")


class RoomTypeCreate(RoomTypeBase):
    pass


class RoomTypeUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    default_capacity: Optional[int] = Field(default=None, ge=1, le=10)
    default_price: Optional[float] = Field(default=None, gt=0)


class RoomType(RoomTypeBase):
    id: int

    class Config:
        from_attributes = True
