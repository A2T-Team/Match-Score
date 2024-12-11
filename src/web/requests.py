from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.core.auth import get_current_user

from src.models.user import User
from src.models.request import RequestType, RequestStatus, RequestAction
from src.schemas.request import CreateRequest
from src.crud.requests import view_requests, accept_request, reject_request, open_request, creating_request

import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse)
async def view_requests_by_status(request: Request,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(get_current_user),
                                   search: Optional[RequestStatus] = Query(RequestStatus.PENDING,
                                                                           alias='status',
                                                                           description='Filter requests by status')):
    requests = view_requests(db, current_user, search)
    return templates.TemplateResponse("view_requests.html", {"request": request, "requests": requests})


@router.post("/", response_class=HTMLResponse)
async def create_request(request: CreateRequest,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user),
                         r_type: RequestType = Query(RequestType.PROMOTE, alias='type', description='Type of request')):
    creating_request(db, request, current_user, r_type)
    return templates.TemplateResponse("create_request.html", {"request": request})


@router.get("/{request_id}", response_class=HTMLResponse)
async def open_by_id(request: Request,
                     request_id: UUID,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user),
                     action: Optional[RequestAction] = Query(None, alias='action', description='Action to be taken on request')):
    request_details = open_request(db, request_id, current_user, action)
    return templates.TemplateResponse("open_request.html", {"request": request, "request_details": request_details})
