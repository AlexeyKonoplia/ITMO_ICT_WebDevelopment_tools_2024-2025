from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import List

from db.connection import get_session
from model.models.models import UserGenre
from model.schemas.user_genre import UserGenreRead, UserGenreCreate, UserGenreUpdate

user_genre_router = APIRouter()


@user_genre_router.post("/", response_model=UserGenreRead)
def create_user_genre(data: UserGenreCreate, session: Session = Depends(get_session)):
    user_genre = UserGenre(**data.model_dump())
    session.add(user_genre)
    session.commit()
    session.refresh(user_genre)
    return user_genre


@user_genre_router.get("/", response_model=List[UserGenreRead])
def get_all_user_genres(session: Session = Depends(get_session)):
    return session.exec(select(UserGenre)).all()


@user_genre_router.get("/user/{user_id}", response_model=List[UserGenreRead])
def get_user_genres(user_id: int, session: Session = Depends(get_session)):
    return session.exec(select(UserGenre).where(UserGenre.user_id == user_id)).all()


@user_genre_router.delete("/user/{user_id}/genre/{genre_id}", response_model=dict)
def delete_user_genre(user_id: int, genre_id: int, session: Session = Depends(get_session)):
    relation = session.get(UserGenre, (user_id, genre_id))
    if not relation:
        raise HTTPException(status_code=404, detail="UserGenre not found")
    session.delete(relation)
    session.commit()
    return {"ok": True}

@user_genre_router.patch("/user/{user_id}/genre/{genre_id}", response_model=UserGenreRead)
def update_user_genre(user_id: int, genre_id: int, update: UserGenreUpdate, session: Session = Depends(get_session)):
    relation = session.get(UserGenre, (user_id, genre_id))
    if not relation:
        raise HTTPException(status_code=404, detail="UserGenre not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(relation, key, value)
    session.commit()
    session.refresh(relation)
    return relation