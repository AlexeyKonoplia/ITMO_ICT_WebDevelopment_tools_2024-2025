from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from db.connection import init_db
from endpoints.book_endpoints import book_router
from endpoints.exchange_endpoints import exchange_router
from endpoints.genre_endpoints import genre_router
from endpoints.user_endpoints import user_router
from endpoints.user_genre_endpoints import user_genre_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(genre_router, prefix="/genres", tags=["genres"])
app.include_router(book_router, prefix="/books", tags=["books"])
app.include_router(user_genre_router, prefix="/user/genres", tags=["user genres"])
app.include_router(exchange_router, prefix="/requests", tags=["exchange requests"])

if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
