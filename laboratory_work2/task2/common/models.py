from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    bio: Optional[str] = None
    created_at: datetime = datetime.now()

    books: List["Book"] = Relationship(back_populates="owner")
    sent_requests: List["ExchangeRequest"] = Relationship(back_populates="sender", sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.sender_id"})
    received_requests: List["ExchangeRequest"] = Relationship(back_populates="receiver", sa_relationship_kwargs={"foreign_keys": "ExchangeRequest.receiver_id"})
    user_genres: List["UserGenre"] = Relationship(back_populates="user")


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    title: str
    author: str
    description: Optional[str] = None
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id")
    year: Optional[int] = None
    available: bool = True

    owner: Optional[User] = Relationship(back_populates="books")
    genre: Optional["Genre"] = Relationship(back_populates="books")


class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    books: List[Book] = Relationship(back_populates="genre")
    users: List["UserGenre"] = Relationship(back_populates="genre")


class UserGenre(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    genre_id: int = Field(foreign_key="genre.id", primary_key=True)
    preference_level: Optional[int] = None

    user: Optional[User] = Relationship(back_populates="user_genres")
    genre: Optional[Genre] = Relationship(back_populates="users")


class ExchangeStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class ExchangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    sender_book_id: int = Field(foreign_key="book.id")
    receiver_book_id: int = Field(foreign_key="book.id")
    status: ExchangeStatus = ExchangeStatus.pending
    message: Optional[str] = None
    created_at: datetime = datetime.now()

    sender: Optional[User] = Relationship(back_populates="sent_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_id]"})
    receiver: Optional[User] = Relationship(back_populates="received_requests", sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_id]"})
    sender_book: Optional[Book] = Relationship(sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.sender_book_id]"})
    receiver_book: Optional[Book] = Relationship(sa_relationship_kwargs={"foreign_keys": "[ExchangeRequest.receiver_book_id]"})
