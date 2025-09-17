from contextlib import asynccontextmanager

from fastapi import FastAPI

from .parser_service import parse_and_save
from common.connection import init_db
from common.parse import ParseRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.post("/parse")
async def parse_url(parse_request: ParseRequest):
    try:
        print(f"Parsing URL: {parse_request.url}")
        await parse_and_save(parse_request.url)
        return {"message": "Parsing completed"}
    except Exception as e:
        print(f"Error in parse_url: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}