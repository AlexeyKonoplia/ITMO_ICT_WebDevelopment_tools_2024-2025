import os
from datetime import time

from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, Session, create_engine, select

load_dotenv()
db_url = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
engine = create_engine(db_url, echo=True)


def init_db():
    for i in range(10):
        try:
            SQLModel.metadata.create_all(engine)
            # Создаем пользователя по умолчанию
            create_default_user()
            break
        except OperationalError as e:
            print(f"DB connection failed. Retrying in 3s... ({i + 1}/10)")
            time.sleep(3)


def create_default_user():
    """Создает пользователя по умолчанию, если его нет"""
    from model.models.models import User
    
    with Session(engine) as session:
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
            print("Created default user")


def get_session():
    with Session(engine) as session:
        yield session
