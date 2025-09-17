from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr
from typing_extensions import List

from model.models.models import ExchangeStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


class BookShort(BaseModel):
    id: int
    title: str
    author: str


class ExchangeRequestShort(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: ExchangeStatus


class UserRead(UserBase):
    id: int
    created_at: datetime
    books: List[BookShort] = []
    sent_requests: List[ExchangeRequestShort] = []
    received_requests: List[ExchangeRequestShort] = []


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str
