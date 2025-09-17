from typing import Optional

from pydantic import BaseModel


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):
    name: Optional[str] = None


class GenreRead(GenreBase):
    id: int

    class Config:
        from_attributes = True
