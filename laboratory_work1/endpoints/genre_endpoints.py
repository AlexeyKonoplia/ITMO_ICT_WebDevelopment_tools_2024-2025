from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from model.models.models import Genre
from model.schemas.genre import GenreRead, GenreCreate, GenreUpdate

genre_router = APIRouter()


@genre_router.post("/", response_model=GenreRead)
def create_genre(genre: GenreCreate, session: Session = Depends(get_session)):
    db_genre = Genre(**genre.model_dump())
    session.add(db_genre)
    session.commit()
    session.refresh(db_genre)
    return db_genre


@genre_router.get("/", response_model=List[GenreRead])
def get_all_genres(session: Session = Depends(get_session)):
    return session.exec(select(Genre)).all()


@genre_router.get("/{genre_id}", response_model=GenreRead)
def get_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@genre_router.delete("/{genre_id}", response_model=dict)
def delete_genre(genre_id: int, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    session.delete(genre)
    session.commit()
    return {"ok": True}

@genre_router.patch("/{genre_id}", response_model=GenreRead)
def update_genre(genre_id: int, update: GenreUpdate, session: Session = Depends(get_session)):
    genre = session.get(Genre, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(genre, key, value)
    session.commit()
    session.refresh(genre)
    return genre