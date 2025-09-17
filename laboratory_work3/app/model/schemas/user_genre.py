from typing import Optional

from pydantic import BaseModel

from model.schemas.book import GenreSimple


class UserGenreCreate(BaseModel):
    user_id: int
    genre_id: int
    preference_level: Optional[int] = None


class UserGenreUpdate(BaseModel):
    preference_level: Optional[int] = None


class UserGenreRead(BaseModel):
    user_id: int
    genre: GenreSimple
    preference_level: Optional[int] = None

    class Config:
        from_attributes = True
