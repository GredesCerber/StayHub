from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class GuestBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, description="Guest first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Guest last name")
    email: str = Field(..., max_length=100, description="Email address")
    phone: Optional[str] = Field(default=None, max_length=20, description="Phone number")
    address: Optional[str] = Field(default=None, max_length=255, description="Address")
    id_document: Optional[str] = Field(default=None, max_length=50, description="ID document number")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class GuestCreate(GuestBase):
    """Schema for creating a guest."""
    pass


class GuestUpdate(BaseModel):
    """Schema for updating a guest."""
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=255)
    id_document: Optional[str] = Field(default=None, max_length=50)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v is not None:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Invalid email format')
        return v


class GuestFilter(BaseModel):
    """Schema for filtering guests."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Guest(GuestBase):
    """Schema for guest response."""
    id: int

    class Config:
        from_attributes = True
