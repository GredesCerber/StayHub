from pydantic import BaseModel
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class Service(ServiceBase):
    id: int

    class Config:
        from_attributes = True
