from fastapi import APIRouter, Depends, Header

from sqlalchemy.orm import Session
from src.api.deps import get_db
import logging

from typing import Annotated
from uuid import UUID

from src.schemas.request import CreateRequest

from src.crud.requests import view_requests, accept_request, reject_request, open_request, creating_request


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create")
def create_request(token: Annotated[str, Header()], request: CreateRequest, db: Session = Depends(get_db)):
    return creating_request(db, request, token)


@router.get("/admin")
def get_all_requests(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    return view_requests(db, token)


@router.get("/admin/{request_id}")
def open_request(token: Annotated[str, Header()], request_id: UUID, db: Session = Depends(get_db)):
    return open_request(db, request_id, token)


@router.put("/admin/{request_id}/accept")
def accept_request(token: Annotated[str, Header()], request_id: UUID, db: Session = Depends(get_db)):
    return accept_request(db, request_id, token)


@router.delete("/admin/{request_id}/reject")
def reject_request(token: Annotated[str, Header()], request_id: UUID, db: Session = Depends(get_db)):
    return reject_request(db, request_id, token)
