import os
from typing import List

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.connection import get_session
from endpoints.user_endpoints import auth_handler
from model.models.models import User, Book
from model.schemas.book import BookRead, BookCreate, BookUpdate
from model.schemas.parse import ParseRequest

book_router = APIRouter()


@book_router.post("/parse")
async def parse(parse_request: ParseRequest):
    parser_url = os.getenv("PARSER_URL", "http://0.0.0.0:8001/parse")
    try:
        async with aiohttp.ClientSession() as client:
            response = await client.post(
                parser_url, json=parse_request.model_dump(), timeout=15
            )
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Parser service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@book_router.post("/", response_model=BookRead)
def create_book(
    book: BookCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(auth_handler.get_current_user),
):
    db_book = Book(**book.model_dump(), owner_id=current_user.id)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@book_router.get("/", response_model=List[BookRead])
def get_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()


@book_router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.delete("/{book_id}", response_model=dict)
def delete_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    session.delete(book)
    session.commit()
    return {"ok": True}


@book_router.patch("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int, update: BookUpdate, session: Session = Depends(get_session)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
    session.commit()
    session.refresh(book)
    return book
