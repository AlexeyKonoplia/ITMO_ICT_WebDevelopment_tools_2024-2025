from typing import Optional

from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None
    genre_id: Optional[int] = None
    year: Optional[int] = None
    available: bool = True


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    genre_id: Optional[int] = None
    year: Optional[int] = None
    available: Optional[bool] = None


class GenreSimple(BaseModel):
    id: int
    name: str


class BookRead(BookBase):
    id: int
    owner_id: int
    genre: Optional[GenreSimple] = None
