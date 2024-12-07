from fastapi import APIRouter, Depends, Query

from sqlalchemy.orm import Session
from src.api.deps import get_db
import logging

from typing import Optional
from uuid import UUID

from src.core.auth import get_current_user

from src.models.user import User
from src.models.request import RequestStatus
from src.schemas.request import CreateRequest

from src.crud.requests import view_requests, accept_request, reject_request, open_request, creating_request


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create")
def create_request(request: CreateRequest,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    return creating_request(db, request, current_user)


@router.get("/")
def view_requests_by_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
                            search: Optional[RequestStatus] = Query(RequestStatus.PENDING,
                                                                    alias='status',
                                                                    description='Filter requests by status')):
    return view_requests(db, current_user, search)


@router.get("/{request_id}")
def open_by_id(request_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return open_request(db, request_id, current_user)


@router.put("/{request_id}/accept")
def accept(request_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return accept_request(db, request_id, current_user)


@router.put("/{request_id}/reject")
def reject(request_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return reject_request(db, request_id, current_user)
