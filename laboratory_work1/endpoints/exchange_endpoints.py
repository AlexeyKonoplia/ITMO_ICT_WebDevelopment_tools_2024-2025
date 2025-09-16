from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db.connection import get_session
from model.models.models import ExchangeRequest
from model.schemas.exchange_request import ExchangeRequestCreate, ExchangeRequestRead

exchange_router = APIRouter()


@exchange_router.post("/", response_model=ExchangeRequestRead)
def create_exchange_request(data: ExchangeRequestCreate, session: Session = Depends(get_session)):
    exchange = ExchangeRequest(**data.model_dump())
    session.add(exchange)
    session.commit()
    session.refresh(exchange)
    return exchange


@exchange_router.get("/", response_model=List[ExchangeRequestRead])
def get_all_exchange_requests(session: Session = Depends(get_session)):
    return session.exec(select(ExchangeRequest)).all()


@exchange_router.get("/{exchange_id}", response_model=ExchangeRequestRead)
def get_exchange_request(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(ExchangeRequest, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    return exchange


@exchange_router.delete("/{exchange_id}", response_model=dict)
def delete_exchange_request(exchange_id: int, session: Session = Depends(get_session)):
    exchange = session.get(ExchangeRequest, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    session.delete(exchange)
    session.commit()
    return {"ok": True}


@exchange_router.patch("/{exchange_id}/status", response_model=ExchangeRequestRead)
def update_exchange_status(exchange_id: int, status: str, session: Session = Depends(get_session)):
    exchange = session.get(ExchangeRequest, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    exchange.status = status
    session.commit()
    session.refresh(exchange)
    return exchange
