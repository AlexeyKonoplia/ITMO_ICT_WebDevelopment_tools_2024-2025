from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from model.models.models import ExchangeStatus
from model.schemas.book import BookRead
from model.schemas.user import UserRead


class ExchangeRequestCreate(BaseModel):
    sender_id: int
    receiver_id: int
    sender_book_id: int
    receiver_book_id: int
    message: Optional[str] = None


class ExchangeRequestRead(BaseModel):
    id: int
    sender: UserRead
    receiver: UserRead
    sender_book: BookRead
    receiver_book: BookRead
    status: ExchangeStatus
    message: Optional[str] = None
    created_at: datetime
