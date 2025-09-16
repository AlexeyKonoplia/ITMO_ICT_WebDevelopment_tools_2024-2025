from typing import Optional
from common.connection import get_session, get_sync_session
from common.models import Genre, Book

def get_or_create_genre(session, genre_name: str) -> Optional[int]:
    if not genre_name:
        return None

    genre = session.query(Genre).filter_by(name=genre_name).first()
    if not genre:
        genre = Genre(name=genre_name)
        session.add(genre)
        session.commit()
        session.refresh(genre)
    return genre.id

async def get_or_create_genre_async(session, genre_name: str) -> Optional[int]:
    if not genre_name:
        return None

    genre = await session.get(Genre, genre_name)  # Используем async методы
    if not genre:
        # Ищем по имени
        from sqlalchemy import select
        stmt = select(Genre).where(Genre.name == genre_name)
        result = await session.execute(stmt)
        genre = result.scalar_one_or_none()
        
        if not genre:
            genre = Genre(name=genre_name)
            session.add(genre)
            await session.commit()
            await session.refresh(genre)
    return genre.id

def save_books(books_data):
    # Используем синхронную сессию для multiprocessing
    with get_sync_session() as session:
        for data in books_data:
            genre_id = get_or_create_genre(session, data["genre_name"]) if data["genre_name"] else 1

            book = Book(
                title=data["title"],
                author=data["author"],
                description=data["description"],
                year=data["year"],
                genre_id=genre_id,
                owner_id=1
            )
            session.add(book)
        session.commit()

async def save_books_async(books_data):
    async for session in get_session():
        async with session.begin():
            for data in books_data:
                genre_id = await get_or_create_genre_async(session, data["genre_name"]) if data["genre_name"] else 1

                book = Book(
                    title=data["title"],
                    author=data["author"],
                    description=data["description"],
                    year=data["year"],
                    genre_id=genre_id,
                    owner_id=1
                )
                session.add(book)
            await session.commit()