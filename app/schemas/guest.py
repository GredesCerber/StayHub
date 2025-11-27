from pydantic import BaseModel, EmailStr
from typing import Optional


class GuestBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    id_document: Optional[str] = None


class GuestCreate(GuestBase):
    pass


class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    id_document: Optional[str] = None


class Guest(GuestBase):
    id: int

    class Config:
        from_attributes = True
