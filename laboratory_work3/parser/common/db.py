from typing import Optional
from sqlmodel import select

from common.connection import get_session
from common.models import Genre, Book, User


def get_or_create_default_user(session) -> int:
    """Создает пользователя по умолчанию, если его нет"""
    statement = select(User).where(User.id == 1)
    user = session.exec(statement).first()
    if not user:
        user = User(
            id=1,
            name="Default User",
            email="default@example.com",
            password="default_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user.id




def get_or_create_genre(session, genre_name: str) -> Optional[int]:
    if not genre_name:
        return None

    statement = select(Genre).where(Genre.name == genre_name)
    genre = session.exec(statement).first()
    if not genre:
        genre = Genre(name=genre_name)
        session.add(genre)
        session.commit()
        session.refresh(genre)
    return genre.id




def save_books(books_data):
    print(f"[DB] Начинаем сохранение {len(books_data)} книг")
    with next(get_session()) as session:
        try:
            # Создаем пользователя по умолчанию
            owner_id = get_or_create_default_user(session)
            print(f"[DB] Используем пользователя с ID: {owner_id}")
            
            for data in books_data:
                genre_id = get_or_create_genre(session, data["genre_name"]) if data["genre_name"] else 1

                book = Book(
                    title=data["title"],
                    author=data["author"],
                    description=data["description"],
                    year=data["year"],
                    genre_id=genre_id,
                    owner_id=owner_id
                )
                session.add(book)
                print(f"[DB] Добавлена книга: {data['title']}")
            session.commit()
            print(f"[DB] Успешно сохранено {len(books_data)} книг")
        except Exception as e:
            print(f"[DB ERROR] Ошибка при сохранении: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            raise

def save_books_async(books_data):
    """Синхронная версия для совместимости"""
    save_books(books_data)
