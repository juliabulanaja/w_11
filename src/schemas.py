from datetime import datetime, date

from pydantic import BaseModel, Field


class ContactModel(BaseModel):
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    email: str
    phone: str
    birthday: date


class ContactResponse(BaseModel):
    id: int
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    email: str
    phone: str
    birthday: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactUpdate(BaseModel):
    firstname: str = Field(max_length=50)
    lastname: str = Field(max_length=50)
    email: str
    phone: str
    birthday: date
