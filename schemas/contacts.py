"""
Contact Schema Definitions
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, PastDate


class ContactSchema(BaseModel):
    first_name: str = Field(min=1, max_length=50)
    last_name: str | None = Field(max_length=50, default="")
    birthday: PastDate | None = Field(default="1900-01-01")
    # birthday: Optional[PastDate]
    notes: str | None = Field(max_length=150, default="")
    email: EmailStr | None = Field(max_length=100, default="user@example.com")
    phone: str | None = Field(max_length=30, default="")

    class Config:
        # orm_mode = True
        from_attributes = True


class ContactResponseSchema(BaseModel):
    id: int = 1
    first_name: str
    last_name: str = None
    birthday: date = None
    notes: str = None
    email: EmailStr = None
    phone: str = None

    class Config:
        from_attributes = True


class ContactUpdateSchema(BaseModel):
    id: int = 1
    first_name: str = Field(min=1, max_length=50)
    last_name: str | None = Field(max_length=50, default=None)
    birthday: Optional[PastDate] = None
    notes: str | None = Field(max_length=150, default=None)
    email: EmailStr | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=30)

    class Config:
        from_attributes = True
