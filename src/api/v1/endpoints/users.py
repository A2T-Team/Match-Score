from fastapi import APIRouter, Depends, Header
from typing import Annotated
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.core.authentication import get_current_user
import uuid
from src.api.deps import get_db
from src.schemas.user import CreateUserRequest, UpdateUserRequest, LoginRequest, UpdateEmailRequest, CreateRequest
from src.models.user import User
from src.crud.users import (get_all_users, create_user, get_user_by_id, login_user, get_me, update_email, update_user,
                            get_by_username, get_by_email, delete_user, view_requests, accept_request,
                            reject_request, open_request, creating_request)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register")
def register(user: CreateUserRequest, db: Session = Depends(get_db)):
    create_user(db, user)
    return "Registration successful"


@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    token = login_user(db, user)
    return token


@router.get("/")
def get_users(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    return get_all_users(db, token)


@router.get("/me")
def read_user_me(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_me(db, token)
    return user


@router.get("/{username}")
def get_user_by_username(username: str, token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_by_username(db, username, token)
    return user


@router.get("/{email}")
def get_user_by_email(email: str, token: Annotated[str, Header()], db: Session = Depends(get_db)):
    user = get_by_email(db, email, token)
    return user


@router.put("/me/email")
def update_my_email(token: Annotated[str, Header()], new: UpdateEmailRequest, db: Session = Depends(get_db)):
    new_credentials = update_email(db, new, token)
    return new_credentials


@router.put("/admin/users/{username}")
def update_user_credentials(token: Annotated[str, Header()], username: str, new: UpdateUserRequest, db: Session = Depends(get_db)):
    new_credentials = update_user(db, new, username, token)
    return new_credentials


@router.delete("/admin/users/delete/{username}")
def delete_user_by_username(token: Annotated[str, Header()], username: str, db: Session = Depends(get_db)):
    return delete_user(db, username, token)


@router.post("/requests/create")
def create_request(token: Annotated[str, Header()], request: CreateRequest, db: Session = Depends(get_db)):
    return creating_request(db, request, token)


@router.get("/admin/requests")
def get_all_requests(token: Annotated[str, Header()], db: Session = Depends(get_db)):
    return view_requests(db, token)


@router.get("/admin/requests/{request_id}")
def open_request_by_id(token: Annotated[str, Header()], request_id: UUID, db: Session = Depends(get_db)):
    return open_request(db, request_id, token)


@router.put("/admin/requests/{request_id}/accept")
def accept_request_by_id(token: Annotated[str, Header()], request_id: UUID, db: Session = Depends(get_db)):
    return accept_request(db, request_id, token)


@router.delete("/admin/requests/{request_id}/reject")
def reject_request_by_id(token: Annotated[str, Header()], request_id: UUID, db: Session = Depends(get_db)):
    return reject_request(db, request_id, token)
