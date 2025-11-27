from pydantic import BaseModel, Field
from typing import Optional


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Service name")
    description: Optional[str] = Field(default=None, max_length=255, description="Service description")
    price: float = Field(..., ge=0, description="Service price")
    is_active: bool = Field(default=True, description="Service active status")


class ServiceCreate(ServiceBase):
    """Schema for creating a service."""
    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ServiceFilter(BaseModel):
    """Schema for filtering services."""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)


class Service(ServiceBase):
    """Schema for service response."""
    id: int

    class Config:
        from_attributes = True
